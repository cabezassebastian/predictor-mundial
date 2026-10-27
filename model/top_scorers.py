"""
Módulo para calcular las probabilidades individuales de goles por jugador.
"""
import os
import sys
import math
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
from model.temporal_decay import decay_weight

def load_goalscorers(csv_path: str) -> pd.DataFrame:
    """Carga los datos de goleadores."""
    try:
        df = pd.read_csv(csv_path, engine='python', encoding='utf-8')
        return df
    except Exception as e:
        print(f"Error loading goalscorers: {e}")
        return pd.DataFrame()

def get_player_goal_rates(team: str, goalscorers_df: pd.DataFrame, 
                          matches_df: pd.DataFrame, reference_date: str) -> list[tuple[str, float]]:
    """
    Calcula la tasa de goles con decaimiento temporal para cada jugador del equipo.
    """
    if goalscorers_df is None or goalscorers_df.empty:
        return config.KNOWN_SCORERS.get(team, [])
        
    team_goals = goalscorers_df[
        (goalscorers_df['team'] == team) & 
        (goalscorers_df['date'] <= reference_date) & 
        (goalscorers_df['scorer'].notna()) &
        (goalscorers_df['own_goal'] == False) if 'own_goal' in goalscorers_df.columns else True
    ]
    
    if len(team_goals) == 0:
        return config.KNOWN_SCORERS.get(team, [])
        
    import datetime
    ref_dt = datetime.datetime.strptime(reference_date, "%Y-%m-%d")
    
    scorer_weights = {}
    for _, row in team_goals.iterrows():
        scorer = row['scorer']
        try:
            row_dt = datetime.datetime.strptime(row['date'], "%Y-%m-%d")
        except ValueError:
            continue
        days_ago = (ref_dt - row_dt).days
        decay = decay_weight(days_ago, half_life=config.DECAY_HALF_LIFE_DAYS * 2) # Decaimiento más lento para goleadores
        
        if scorer not in scorer_weights:
            scorer_weights[scorer] = 0.0
        scorer_weights[scorer] += decay
        
    # Filtrar solo partidos del equipo hasta la fecha de referencia
    team_matches = matches_df[(matches_df['home_team'] == team) | (matches_df['away_team'] == team)]
    team_matches = team_matches[team_matches['date'] <= reference_date]
    
    # Decaimiento temporal usando datetime standard
    total_match_weight = 0.0
    for _, row in team_matches.iterrows():
        try:
            row_dt = datetime.datetime.strptime(row['date'], "%Y-%m-%d")
        except ValueError:
            continue
        days_ago = (ref_dt - row_dt).days
        total_match_weight += decay_weight(days_ago, half_life=config.DECAY_HALF_LIFE_DAYS * 2)
        
    if total_match_weight == 0:
        return config.KNOWN_SCORERS.get(team, [])
        
    rates = [(player, weight / total_match_weight) for player, weight in scorer_weights.items()]
    rates.sort(key=lambda x: x[1], reverse=True)
    
    # Usar fallback si la data empírica es muy pobre (ej. máximo goleador tiene < 0.1 goles/partido)
    if not rates or rates[0][1] < 0.1:
        fallback = config.KNOWN_SCORERS.get(team, [])
        if fallback:
            return fallback
            
    return rates

def get_match_top_scorers(team_a: str, team_b: str, lambda_a: float, lambda_b: float,
                          goalscorers_df: pd.DataFrame, matches_df: pd.DataFrame, 
                          reference_date: str, top_n: int = 10) -> list[dict]:
    """
    Devuelve los goleadores más probables para un partido.
    """
    rates_a = get_player_goal_rates(team_a, goalscorers_df, matches_df, reference_date)
    rates_b = get_player_goal_rates(team_b, goalscorers_df, matches_df, reference_date)
    
    total_rate_a = sum(rate for _, rate in rates_a)
    total_rate_b = sum(rate for _, rate in rates_b)
    
    scorers = []
    
    # Equipo A
    if total_rate_a > 0:
        for player, rate in rates_a:
            r_j = rate / total_rate_a
            # P(anota) = 1 - e^(-r_j * lambda_team)
            p_score = (1.0 - math.exp(-r_j * lambda_a)) * 100
            if p_score > 1.0:
                scorers.append({'player': player, 'team': team_a, 'probability': p_score})
                
    # Equipo B
    if total_rate_b > 0:
        for player, rate in rates_b:
            r_j = rate / total_rate_b
            p_score = (1.0 - math.exp(-r_j * lambda_b)) * 100
            if p_score > 1.0:
                scorers.append({'player': player, 'team': team_b, 'probability': p_score})
                
    scorers.sort(key=lambda x: x['probability'], reverse=True)
    return scorers[:top_n]
