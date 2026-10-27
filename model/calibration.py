"""
Módulo para calibración del modelo mediante backtesting.
"""
import os
import sys
import pandas as pd
import numpy as np
from itertools import product
from rich.console import Console
from rich.progress import track

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
from model.monte_carlo import simulate_match

def get_historical_tournaments(matches_df: pd.DataFrame):
    """Obtiene los partidos de la fase de grupos de Mundiales 2018 y 2022."""
    wc_matches = matches_df[matches_df['tournament'] == 'FIFA World Cup'].copy()
    
    # 2018: Junio - Julio 2018
    # 2022: Nov - Dic 2022
    mask_2018 = (wc_matches['date'].str.startswith('2018')) & (wc_matches['neutral'] == True)
    mask_2022 = (wc_matches['date'].str.startswith('2022')) & (wc_matches['neutral'] == True)
    
    return wc_matches[mask_2018 | mask_2022]

def run_calibration(matches_df: pd.DataFrame, rankings_dict: dict, reference_date: str) -> dict:
    """
    Ejecuta backtesting y devuelve métricas.
    """
    test_matches = get_historical_tournaments(matches_df)
    
    if len(test_matches) == 0:
        return {'brier_score': 0, 'log_loss': 0, 'accuracy': 0}
        
    brier_sum = 0
    log_loss_sum = 0
    correct = 0
    n_matches = 0
    
    # Usar solo 1000 simulaciones por partido para calibración para que sea más rápido
    n_sims = 1000
    
    for _, row in test_matches.iterrows():
        match_date = row['date']
        team_a = row['home_team']
        team_b = row['away_team']
        
        # Simular con los datos disponibles ANTES del partido
        try:
            result = simulate_match(team_a, team_b, matches_df, rankings_dict, match_date, n_sims)
            
            p_a = result.prob_win_a / 100.0
            p_d = result.prob_draw / 100.0
            p_b = result.prob_win_b / 100.0
            
            # Resultado real
            home_score = row['home_score']
            away_score = row['away_score']
            
            actual_a = 1.0 if home_score > away_score else 0.0
            actual_d = 1.0 if home_score == away_score else 0.0
            actual_b = 1.0 if home_score < away_score else 0.0
            
            # Brier Score (suma de errores al cuadrado)
            brier = (p_a - actual_a)**2 + (p_d - actual_d)**2 + (p_b - actual_b)**2
            brier_sum += brier
            
            # Log Loss
            epsilon = 1e-15
            p_actual = p_a if actual_a else p_d if actual_d else p_b
            p_actual = max(epsilon, min(1 - epsilon, p_actual))
            log_loss_sum += -math.log(p_actual)
            
            # Accuracy
            probs = [p_a, p_d, p_b]
            max_idx = probs.index(max(probs))
            
            if (max_idx == 0 and actual_a == 1.0) or \
               (max_idx == 1 and actual_d == 1.0) or \
               (max_idx == 2 and actual_b == 1.0):
                correct += 1
                
            n_matches += 1
            
        except Exception:
            continue
            
    if n_matches == 0:
        return {'brier_score': 0, 'log_loss': 0, 'accuracy': 0}
        
    return {
        'brier_score': brier_sum / n_matches,
        'log_loss': log_loss_sum / n_matches,
        'accuracy': (correct / n_matches) * 100
    }

def grid_search_weights(matches_df: pd.DataFrame, rankings_dict: dict, step: float = 0.05) -> dict:
    """
    Busca la mejor combinación de pesos minimizando el Brier Score.
    """
    print(f"Iniciando Grid Search (paso {step}). Tiempo estimado: 30-60 segundos.")
    
    best_brier = float('inf')
    best_weights = None
    best_metrics = None
    
    # Guardar pesos originales
    orig_r = config.RANKING_WEIGHT
    orig_f = config.FORM_WEIGHT
    orig_q = config.OPPONENT_QUALITY_WEIGHT
    orig_h = config.H2H_WEIGHT
    
    # Generar combinaciones que sumen 1.0
    vals = np.arange(0, 1.01, step)
    
    valid_combos = []
    for r, f, q in product(vals, vals, vals):
        h = 1.0 - (r + f + q)
        if 0 <= h <= 1.0 and abs(r + f + q + h - 1.0) < 1e-5:
            valid_combos.append((r, f, q, h))
            
    # Reducir combinaciones para no tardar mucho si hay demasiadas
    if len(valid_combos) > 200:
        # Tomar una muestra representativa o enfocarse en rangos sensatos
        valid_combos = [c for c in valid_combos if c[0] >= 0.2] 
    
    try:
        for r, f, q, h in valid_combos:
            config.RANKING_WEIGHT = r
            config.FORM_WEIGHT = f
            config.OPPONENT_QUALITY_WEIGHT = q
            config.H2H_WEIGHT = h
            
            # Usar fecha reciente para que tome todo 2018 y 2022
            metrics = run_calibration(matches_df, rankings_dict, "2023-01-01")
            
            if metrics['brier_score'] < best_brier and metrics['n_matches'] > 0:
                best_brier = metrics['brier_score']
                best_weights = {'ranking': r, 'form': f, 'quality': q, 'h2h': h}
                best_metrics = metrics
                
    finally:
        # Restaurar
        config.RANKING_WEIGHT = orig_r
        config.FORM_WEIGHT = orig_f
        config.OPPONENT_QUALITY_WEIGHT = orig_q
        config.H2H_WEIGHT = orig_h
        
    return {
        'weights': best_weights,
        'metrics': best_metrics
    }
