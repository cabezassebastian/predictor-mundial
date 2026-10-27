"""
Módulo para calcular la fuerza compuesta de un equipo y generar lambda para Poisson.

MEJORAS v2:
- Integración de sistema Elo dinámico (superior al ranking FIFA estático)
- Factor de diferencia de goles (no solo W/D/L)
- Ventaja de sede para países anfitriones
- Factor de momentum (últimos 5 partidos pesan más)
- Clamp de lambda para evitar predicciones extremas
- Factor de forma en el torneo actual
"""
import os
import sys
import math
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
from model.fifa_ranking import get_normalized_ranking
from model.temporal_decay import get_weighted_form
from model.opponent_quality import get_quality_weighted_form
from model.historical_h2h import get_h2h_factor
from model.elo_ratings import calculate_all_elos, get_elo, ELO_INITIAL


def _get_goal_diff_form(team: str, matches_df: pd.DataFrame, reference_date: str, n_recent: int = 15) -> float:
    """
    Calcula la forma basada en diferencia de goles, no solo W/D/L.
    Un equipo que gana 3-0 es más fuerte que uno que gana 1-0.
    
    Returns:
        Valor normalizado [0, 1] donde 0.5 es neutral.
    """
    import datetime
    
    team_matches = matches_df[
        ((matches_df['home_team'] == team) | (matches_df['away_team'] == team)) &
        (matches_df['date'] <= reference_date)
    ].dropna(subset=['home_score', 'away_score']).copy()
    
    team_matches = team_matches.sort_values('date', ascending=False).head(n_recent)
    
    if len(team_matches) == 0:
        return 0.5
    
    ref_dt = datetime.datetime.strptime(reference_date, "%Y-%m-%d")
    total_weight = 0.0
    total_gd = 0.0
    
    for _, row in team_matches.iterrows():
        try:
            row_dt = datetime.datetime.strptime(row['date'], "%Y-%m-%d")
        except ValueError:
            continue
            
        days_ago = (ref_dt - row_dt).days
        decay = math.exp(-math.log(2) / 180 * max(0, days_ago))  # Half-life de 6 meses para form
        
        is_home = row['home_team'] == team
        h_score = int(row['home_score'])
        a_score = int(row['away_score'])
        
        # Diferencia de goles desde perspectiva del equipo
        gd = (h_score - a_score) if is_home else (a_score - h_score)
        
        # Clamp GD a [-3, 3] para evitar que goleadas distorsionen
        gd = max(-3, min(3, gd))
        
        total_gd += gd * decay
        total_weight += decay
    
    if total_weight == 0:
        return 0.5
    
    # Normalizar: GD promedio ponderado, luego mapear a [0, 1]
    avg_gd = total_gd / total_weight
    # Sigmoid suave para mapear (-inf, inf) -> (0, 1)
    normalized = 1.0 / (1.0 + math.exp(-avg_gd * 0.8))
    
    return normalized


def _get_momentum(team: str, matches_df: pd.DataFrame, reference_date: str) -> float:
    """
    Factor de momentum: últimos 5 partidos pesan MUCHO.
    Captura rachas de victorias o derrotas recientes.
    
    Returns:
        Valor [0, 1] donde >0.5 = momentum positivo.
    """
    team_matches = matches_df[
        ((matches_df['home_team'] == team) | (matches_df['away_team'] == team)) &
        (matches_df['date'] <= reference_date)
    ].dropna(subset=['home_score', 'away_score']).copy()
    
    last_5 = team_matches.sort_values('date', ascending=False).head(5)
    
    if len(last_5) == 0:
        return 0.5
    
    points = 0.0
    total = 0.0
    
    for i, (_, row) in enumerate(last_5.iterrows()):
        # Más reciente = más peso (5, 4, 3, 2, 1)
        weight = 5 - i
        
        is_home = row['home_team'] == team
        h_score = int(row['home_score'])
        a_score = int(row['away_score'])
        
        if h_score > a_score:
            result = 1.0 if is_home else 0.0
        elif h_score < a_score:
            result = 0.0 if is_home else 1.0
        else:
            result = 0.5
        
        points += result * weight
        total += weight
    
    return points / total if total > 0 else 0.5


def _get_tournament_form(team: str, matches_df: pd.DataFrame) -> float:
    """
    Forma en el torneo actual (Mundial 2026).
    Partidos del torneo en curso son extremadamente relevantes.
    
    Returns:
        Valor [0, 1] donde 0.5 es neutral. None si no hay partidos.
    """
    wc_matches = matches_df[
        (matches_df['tournament'] == 'FIFA World Cup') &
        (matches_df['date'].str.startswith('2026')) &
        ((matches_df['home_team'] == team) | (matches_df['away_team'] == team))
    ].dropna(subset=['home_score', 'away_score']).copy()
    
    if len(wc_matches) == 0:
        return None
    
    total_points = 0.0
    total_gd = 0.0
    n = len(wc_matches)
    
    for _, row in wc_matches.iterrows():
        is_home = row['home_team'] == team
        h_score = int(row['home_score'])
        a_score = int(row['away_score'])
        
        gd = (h_score - a_score) if is_home else (a_score - h_score)
        
        if h_score > a_score:
            result = 1.0 if is_home else 0.0
        elif h_score < a_score:
            result = 0.0 if is_home else 1.0
        else:
            result = 0.5
        
        total_points += result
        total_gd += gd
    
    # Combinar puntos y diferencia de goles
    win_rate = total_points / n
    avg_gd = total_gd / n
    gd_factor = 1.0 / (1.0 + math.exp(-avg_gd * 0.5))
    
    # 60% win_rate + 40% gd_factor
    return 0.6 * win_rate + 0.4 * gd_factor


def calculate_strength(team: str, opponent: str, matches_df: pd.DataFrame, 
                       rankings_dict: dict, reference_date: str) -> float:
    """
    Calcula la fuerza compuesta de un equipo (versión avanzada).
    
    Componentes:
    1. Ranking FIFA (normalizado) — ancla estable
    2. Elo dinámico — más preciso que FIFA, se actualiza por partido
    3. Forma reciente con decaimiento — partidos recientes pesan más
    4. Calidad de rivales enfrentados — no es lo mismo ganarle a Brasil que a Curazao
    5. Head-to-Head — historial directo
    6. Diferencia de goles — no solo W/D/L
    7. Momentum — últimos 5 partidos
    8. Forma en el torneo actual — WC2026 en curso
    9. Ventaja de sede — USA/MEX/CAN
    """
    # 1. Ranking FIFA (normalizado 0-1)
    ranking_norm = get_normalized_ranking(team, rankings_dict)
    
    # 2. Elo dinámico
    elos = calculate_all_elos(matches_df, reference_date)
    elo_team = get_elo(team, elos)
    # Normalizar Elo a [0, 1] (rango típico: 1200-2100)
    elo_norm = max(0.0, min(1.0, (elo_team - 1200.0) / 900.0))
    
    # 3. Forma reciente con decaimiento temporal
    form_decay, num_matches = get_weighted_form(team, matches_df, reference_date, rankings_dict)
    
    # 4. Calidad de rivales
    opp_quality = get_quality_weighted_form(team, matches_df, reference_date, rankings_dict)
    
    # 5. Head-to-Head
    h2h_factor = get_h2h_factor(team, opponent, matches_df)
    
    # 6. Diferencia de goles
    gd_form = _get_goal_diff_form(team, matches_df, reference_date)
    
    # 7. Momentum
    momentum = _get_momentum(team, matches_df, reference_date)
    
    # 8. Forma en el torneo actual
    tournament_form = _get_tournament_form(team, matches_df)
    
    # Determinar pesos
    if num_matches >= config.MIN_MATCHES_THRESHOLD:
        # Pesos normales (suman ~1.0 sin tournament_form)
        w_ranking = 0.12    # FIFA ranking (menor peso, Elo es mejor)
        w_elo = 0.25        # Elo dinámico (componente más importante)
        w_form = 0.15       # Forma reciente
        w_quality = 0.12    # Calidad de rivales
        w_h2h = 0.08        # Head-to-Head
        w_gd = 0.10         # Diferencia de goles
        w_momentum = 0.08   # Momentum últimos 5
        w_tournament = 0.10 # Forma en WC2026
    else:
        # Datos insuficientes: confiar más en ranking/Elo
        w_ranking = 0.30
        w_elo = 0.35
        w_form = 0.10
        w_quality = 0.05
        w_h2h = 0.05
        w_gd = 0.05
        w_momentum = 0.05
        w_tournament = 0.05
    
    # Calcular fuerza base
    strength = (w_ranking * ranking_norm + 
                w_elo * elo_norm +
                w_form * form_decay + 
                w_quality * opp_quality + 
                w_h2h * (h2h_factor + 0.5) +  # h2h está en [-0.5, 0.5], centramos en [0, 1]
                w_gd * gd_form +
                w_momentum * momentum)
    
    # Agregar forma del torneo si existe
    if tournament_form is not None:
        strength += w_tournament * tournament_form
    else:
        # Redistribuir el peso del torneo al Elo
        strength += w_tournament * elo_norm
    
    # Ventaja de sede
    if team in config.HOST_COUNTRIES:
        strength += config.HOST_BOOST
                
    return max(0.01, strength)


def calculate_lambdas(team_a: str, team_b: str, matches_df: pd.DataFrame, 
                      rankings_dict: dict, reference_date: str) -> tuple[float, float]:
    """
    Calcula los expected goals (lambda) para ambos equipos.
    Lambda se clampea entre 0.3 y 4.0 para evitar predicciones irreales.
    """
    s_a = calculate_strength(team_a, team_b, matches_df, rankings_dict, reference_date)
    s_b = calculate_strength(team_b, team_a, matches_df, rankings_dict, reference_date)
    
    total_s = s_a + s_b
    if total_s == 0:
        total_s = 1.0
        
    lambda_a = config.AVG_GOALS_PER_MATCH * (s_a / total_s)
    lambda_b = config.AVG_GOALS_PER_MATCH * (s_b / total_s)
    
    # Clamp para evitar extremos irreales
    lambda_a = max(0.3, min(4.0, lambda_a))
    lambda_b = max(0.3, min(4.0, lambda_b))
    
    return lambda_a, lambda_b
