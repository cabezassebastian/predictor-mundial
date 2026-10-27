"""
Módulo para ponderar los resultados según la calidad del rival.
"""
import math
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
from model.temporal_decay import decay_weight
from model.fifa_ranking import get_normalized_ranking

def get_quality_weighted_form(team: str, matches_df: pd.DataFrame, reference_date_str: str, rankings_dict: dict) -> float:
    """
    Calcula la forma reciente del equipo ponderada por la calidad (ranking) de los rivales.
    """
    team_matches = matches_df[
        (matches_df['home_team'] == team) | (matches_df['away_team'] == team)
    ].copy()
    
    # Filtrar partidos futuros
    team_matches = team_matches[team_matches['date'] <= reference_date_str]
    
    if len(team_matches) == 0:
        return 0.5
        
    total_weight = 0.0
    total_score = 0.0
    
    import datetime
    ref_dt = datetime.datetime.strptime(reference_date_str, "%Y-%m-%d")
    
    for _, row in team_matches.iterrows():
        row_dt = datetime.datetime.strptime(row['date'], "%Y-%m-%d")
        days_ago = (ref_dt - row_dt).days
        decay = decay_weight(days_ago, config.DECAY_HALF_LIFE_DAYS)
        
        is_home = row['home_team'] == team
        opponent = row['away_team'] if is_home else row['home_team']
        
        # Obtener ranking del rival
        rival_norm_ranking = get_normalized_ranking(opponent, rankings_dict)
        
        weight = decay * rival_norm_ranking
        
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
        return 0.5
        
    return total_score / total_weight
