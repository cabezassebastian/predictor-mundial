"""
Módulo para calcular la forma reciente de un equipo con decaimiento temporal.
"""
import math
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config

def decay_weight(days_ago: float, half_life: float = 365) -> float:
    """
    Calcula el peso exponencial basado en los días transcurridos.
    """
    if days_ago < 0:
        return 1.0
    lam = math.log(2) / half_life
    return math.exp(-lam * days_ago)

def get_tournament_multiplier(tournament_name: str) -> float:
    """
    Obtiene el multiplicador de importancia del torneo.
    """
    return config.TOURNAMENT_MULTIPLIERS.get(tournament_name, config.DEFAULT_TOURNAMENT_MULTIPLIER)

def get_weighted_form(team: str, matches_df: pd.DataFrame, reference_date_str: str, rankings_dict: dict) -> tuple[float, int]:
    """
    Calcula la forma reciente del equipo ponderada por tiempo y tipo de torneo.
    
    Returns:
        Tupla (forma_ponderada, numero_de_partidos)
    """
    team_matches = matches_df[
        (matches_df['home_team'] == team) | (matches_df['away_team'] == team)
    ].copy()
    
    # Filtrar partidos en el futuro usando comparacion de strings
    team_matches = team_matches[team_matches['date'] <= reference_date_str]
    
    if len(team_matches) == 0:
        return 0.5, 0
        
    total_weight = 0.0
    total_score = 0.0
    
    import datetime
    ref_dt = datetime.datetime.strptime(reference_date_str, "%Y-%m-%d")
    
    for _, row in team_matches.iterrows():
        row_dt = datetime.datetime.strptime(row['date'], "%Y-%m-%d")
        days_ago = (ref_dt - row_dt).days
        decay = decay_weight(days_ago, config.DECAY_HALF_LIFE_DAYS)
        tourn_mult = get_tournament_multiplier(row['tournament'])
        
        weight = decay * tourn_mult
        
        # Determinar resultado (1 victoria, 0.5 empate, 0 derrota)
        is_home = row['home_team'] == team
        home_score = row['home_score']
        away_score = row['away_score']
        
        if home_score > away_score:
            result = 1.0 if is_home else 0.0
        elif home_score < away_score:
            result = 0.0 if is_home else 1.0
        else:
            result = 0.5
            
        total_score += result * weight
        total_weight += weight
        
    if total_weight == 0:
        return 0.5, len(team_matches)
        
    return total_score / total_weight, len(team_matches)
