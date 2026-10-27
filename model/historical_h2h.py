"""
Módulo para calcular la ventaja histórica en enfrentamientos directos (Head-to-Head).
"""
import math
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config

def get_h2h_factor(team_a: str, team_b: str, matches_df: pd.DataFrame) -> float:
    """
    Calcula el factor de ventaja histórica de team_a sobre team_b.
    
    Returns:
        Valor en [-0.5, 0.5] donde positivo significa ventaja para team_a.
    """
    h2h_matches = matches_df[
        ((matches_df['home_team'] == team_a) & (matches_df['away_team'] == team_b)) |
        ((matches_df['home_team'] == team_b) & (matches_df['away_team'] == team_a))
    ].copy()
    
    num_matches = len(h2h_matches)
    
    if num_matches == 0:
        return 0.0
        
    total_weight = 0.0
    weighted_wins_a = 0.0
    
    # Decaimiento mucho más lento para historial (ej. 10 años = 3650 días)
    # Partidos de hace mucho pesan menos, pero no desaparecen tan rápido como la forma reciente
    h2h_half_life = config.DECAY_HALF_LIFE_DAYS * 5
    lam = math.log(2) / h2h_half_life
    
    # Referencia temporal: el partido más reciente del dataset
    ref_date = matches_df['date'].max()
    
    import datetime
    try:
        ref_dt = datetime.datetime.strptime(ref_date, "%Y-%m-%d")
    except ValueError:
        ref_dt = datetime.datetime.now()
        
    for _, row in h2h_matches.iterrows():
        try:
            row_dt = datetime.datetime.strptime(row['date'], "%Y-%m-%d")
        except ValueError:
            continue
        days_ago = (ref_dt - row_dt).days
        decay = math.exp(-lam * days_ago) if days_ago >= 0 else 1.0
        
        is_a_home = row['home_team'] == team_a
        home_score = row['home_score']
        away_score = row['away_score']
        
        if home_score > away_score:
            result_a = 1.0 if is_a_home else 0.0
        elif home_score < away_score:
            result_a = 0.0 if is_a_home else 1.0
        else:
            result_a = 0.5
            
        weighted_wins_a += result_a * decay
        total_weight += decay
        
    if total_weight == 0:
        return 0.0
        
    h2h_advantage = weighted_wins_a / total_weight
    factor = h2h_advantage - 0.5
    
    # Atenuar si hay muy pocos partidos
    if num_matches < 3:
        factor *= (num_matches / 3.0)
        
    return factor
