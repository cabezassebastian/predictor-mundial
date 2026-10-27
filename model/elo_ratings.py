"""
Módulo de Elo Ratings calculados dinámicamente desde datos históricos.
El sistema Elo es superior al ranking FIFA porque se actualiza automáticamente
después de cada partido y es más sensible a resultados recientes.

Basado en el modelo de FiveThirtyEight adaptado a fútbol internacional.
"""
import os
import sys
import math
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config

# K-factor base (sensibilidad de actualización)
K_BASE = 40.0

# K-factor por tipo de torneo
K_TOURNAMENT = {
    "FIFA World Cup": 60.0,
    "FIFA World Cup qualification": 40.0,
    "Copa América": 50.0,
    "Copa America": 50.0,
    "UEFA Euro": 50.0,
    "UEFA Euro qualification": 35.0,
    "African Cup of Nations": 50.0,
    "Africa Cup of Nations": 50.0,
    "AFC Asian Cup": 50.0,
    "CONCACAF Gold Cup": 45.0,
    "CONCACAF Nations League": 35.0,
    "UEFA Nations League": 35.0,
    "Confederations Cup": 45.0,
    "Friendly": 20.0,
    "Friendlies": 20.0,
}

# Elo inicial para equipos desconocidos
ELO_INITIAL = 1500.0

# Cache global de Elos calculados
_elo_cache = {}
_elo_calculated = False


def _goal_diff_multiplier(goal_diff: int) -> float:
    """
    Multiplicador por diferencia de goles (modelo FiveThirtyEight).
    Victorias amplias tienen más impacto que victorias ajustadas.
    """
    if goal_diff <= 0:
        return 1.0
    if goal_diff == 1:
        return 1.0
    if goal_diff == 2:
        return 1.5
    # Para 3+: ln(goal_diff) + 1 - algo menos agresivo
    return (11.0 + goal_diff) / 8.0


def _expected_result(elo_a: float, elo_b: float) -> float:
    """Probabilidad esperada de que A gane (fórmula Elo estándar)."""
    dr = elo_a - elo_b
    return 1.0 / (1.0 + 10.0 ** (-dr / 400.0))


def calculate_all_elos(matches_df: pd.DataFrame, reference_date: str = None) -> dict[str, float]:
    """
    Calcula ratings Elo para todos los equipos procesando cada partido
    cronológicamente desde el inicio del dataset.
    
    Returns:
        Dict[team_name, elo_rating]
    """
    global _elo_cache, _elo_calculated
    
    if _elo_calculated and _elo_cache:
        return _elo_cache
    
    elos = {}
    
    # Ordenar partidos cronológicamente
    sorted_df = matches_df.sort_values('date').copy()
    
    # Filtrar partidos con marcadores válidos
    sorted_df = sorted_df.dropna(subset=['home_score', 'away_score'])
    
    if reference_date:
        sorted_df = sorted_df[sorted_df['date'] <= reference_date]
    
    for _, row in sorted_df.iterrows():
        home = row['home_team']
        away = row['away_team']
        h_score = int(row['home_score'])
        a_score = int(row['away_score'])
        tournament = row.get('tournament', 'Friendly')
        
        # Obtener Elos actuales (o iniciales)
        elo_h = elos.get(home, ELO_INITIAL)
        elo_a = elos.get(away, ELO_INITIAL)
        
        # Ventaja local (+65 puntos Elo de ventaja home, salvo neutral)
        is_neutral = row.get('neutral', False)
        home_adv = 0.0 if is_neutral else 65.0
        
        # Expectativas
        exp_h = _expected_result(elo_h + home_adv, elo_a)
        exp_a = 1.0 - exp_h
        
        # Resultado real (1.0 = victoria, 0.5 = empate, 0.0 = derrota)
        if h_score > a_score:
            actual_h = 1.0
        elif h_score < a_score:
            actual_h = 0.0
        else:
            actual_h = 0.5
        actual_a = 1.0 - actual_h
        
        # K-factor ajustado por torneo y diferencia de goles
        k = K_TOURNAMENT.get(tournament, K_BASE)
        gd = abs(h_score - a_score)
        gd_mult = _goal_diff_multiplier(gd)
        k_eff = k * gd_mult
        
        # Actualizar Elos
        elos[home] = elo_h + k_eff * (actual_h - exp_h)
        elos[away] = elo_a + k_eff * (actual_a - exp_a)
    
    _elo_cache = elos
    _elo_calculated = True
    return elos


def get_elo(team: str, elos: dict[str, float]) -> float:
    """Obtiene el Elo de un equipo (o el valor inicial si no existe)."""
    return elos.get(team, ELO_INITIAL)


def get_elo_win_probability(elo_a: float, elo_b: float) -> tuple[float, float, float]:
    """
    Calcula P(win_a), P(draw), P(win_b) a partir de los Elos.
    Usa el modelo de regresión logística ordenada simplificado.
    """
    exp_a = _expected_result(elo_a, elo_b)
    
    # Probabilidad de empate: más probable cuando equipos son parejos
    elo_diff = abs(elo_a - elo_b)
    # P(draw) decrece con la diferencia de Elo
    p_draw = max(0.15, 0.30 - elo_diff / 2000.0)
    
    # Distribuir el resto según la expectativa Elo
    remaining = 1.0 - p_draw
    p_win_a = remaining * exp_a
    p_win_b = remaining * (1.0 - exp_a)
    
    return p_win_a, p_draw, p_win_b


def reset_elo_cache():
    """Resetea el cache de Elos (útil para recalcular con nuevos datos)."""
    global _elo_cache, _elo_calculated
    _elo_cache = {}
    _elo_calculated = False
