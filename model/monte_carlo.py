"""
Motor de simulación de Monte Carlo con modelo Dixon-Coles.
Incluye predicción de estadísticas avanzadas del partido.

MEJORAS v2:
- Modelo Dixon-Coles para corregir correlación en marcadores bajos
- Simulación híbrida: Monte Carlo para CIs + Dixon-Coles para probabilidades exactas
- Score matrix analítica (más precisa que Monte Carlo puro)
- Mejor resolución de penales basada en Elo
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd
import math

from model.team_strength import calculate_lambdas, calculate_strength
from model.match_stats import predict_match_stats, MatchStats
from model.dixon_coles import (
    build_score_matrix_dc, 
    get_match_probabilities_dc,
    dixon_coles_probability
)

# Rho para Dixon-Coles (estimado para fútbol internacional)
RHO = -0.13

@dataclass
class MatchResult:
    team_a: str
    team_b: str
    prob_win_a: float
    prob_draw: float
    prob_win_b: float
    ci95_a: tuple[float, float]
    ci95_draw: tuple[float, float]
    ci95_b: tuple[float, float]
    score_matrix: np.ndarray
    top_scores: list[tuple[str, float, str]]
    expected_goals_a: float
    expected_goals_b: float
    goals_dist_a: list[float]
    goals_dist_b: list[float]
    lambda_a: float
    lambda_b: float
    # Estadísticas avanzadas
    stats: MatchStats = None
    # Elo ratings
    elo_a: float = 0.0
    elo_b: float = 0.0

def wilson_score_interval(p: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """Calcula intervalo de confianza de Wilson al 95%."""
    if n == 0:
        return (0.0, 100.0)
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    spread = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator
    return (max(0, center - spread) * 100, min(1, center + spread) * 100)

def simulate_match(team_a: str, team_b: str, matches_df: pd.DataFrame, 
                   rankings_dict: dict, reference_date: str, 
                   n_simulations: int = 100000, 
                   weights: dict = None) -> MatchResult:
    """
    Simula un partido usando el modelo híbrido:
    - Dixon-Coles para probabilidades exactas (analítico, más preciso)
    - Monte Carlo para intervalos de confianza y distribuciones
    """
    n_sims = n_simulations
    lambda_a, lambda_b = calculate_lambdas(team_a, team_b, matches_df, rankings_dict, reference_date)
    
    # Calcular fuerzas para estadísticas
    s_a = calculate_strength(team_a, team_b, matches_df, rankings_dict, reference_date)
    s_b = calculate_strength(team_b, team_a, matches_df, rankings_dict, reference_date)
    
    # Obtener Elos
    from model.elo_ratings import calculate_all_elos, get_elo
    elos = calculate_all_elos(matches_df, reference_date)
    elo_a = get_elo(team_a, elos)
    elo_b = get_elo(team_b, elos)
    
    # === PROBABILIDADES EXACTAS (Dixon-Coles) ===
    prob_win_a_dc, prob_draw_dc, prob_win_b_dc = get_match_probabilities_dc(
        lambda_a, lambda_b, rho=RHO
    )
    
    # === SCORE MATRIX (Dixon-Coles analítico) ===
    max_goals = 6
    score_matrix = build_score_matrix_dc(lambda_a, lambda_b, max_goals, rho=RHO)
    
    # === MONTE CARLO para intervalos de confianza ===
    goals_a_mc = np.random.poisson(lambda_a, n_sims)
    goals_b_mc = np.random.poisson(lambda_b, n_sims)
    
    wins_a_mc = np.sum(goals_a_mc > goals_b_mc)
    draws_mc = np.sum(goals_a_mc == goals_b_mc)
    wins_b_mc = np.sum(goals_a_mc < goals_b_mc)
    
    p_win_a_mc = wins_a_mc / n_sims
    p_draw_mc = draws_mc / n_sims
    p_win_b_mc = wins_b_mc / n_sims
    
    # CIs from Monte Carlo
    ci_a = wilson_score_interval(p_win_a_mc, n_sims)
    ci_d = wilson_score_interval(p_draw_mc, n_sims)
    ci_b = wilson_score_interval(p_win_b_mc, n_sims)
    
    # Usar probabilidades Dixon-Coles (más precisas) como valores principales
    p_win_a = prob_win_a_dc
    p_draw = prob_draw_dc
    p_win_b = prob_win_b_dc
    
    # Top scores from the Dixon-Coles matrix
    scores_list = []
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            prob = score_matrix[i, j]
            if prob > 0.01:  # Filtrar resultados muy improbables
                result_str = f"Victoria {team_a}" if i > j else f"Victoria {team_b}" if j > i else "Empate"
                scores_list.append((f"{i} - {j}", prob, result_str))
                
    scores_list.sort(key=lambda x: x[1], reverse=True)
    
    # Goal distributions from Dixon-Coles (marginales)
    from scipy.stats import poisson as poisson_dist
    g_dist_a = [poisson_dist.pmf(i, lambda_a) * 100 for i in range(max_goals + 1)]
    g_dist_b = [poisson_dist.pmf(i, lambda_b) * 100 for i in range(max_goals + 1)]
    
    # Estadísticas avanzadas
    stats = predict_match_stats(lambda_a, lambda_b, s_a, s_b, is_knockout=True)
    
    return MatchResult(
        team_a=team_a, team_b=team_b,
        prob_win_a=p_win_a, prob_draw=p_draw, prob_win_b=p_win_b,
        ci95_a=ci_a, ci95_draw=ci_d, ci95_b=ci_b,
        score_matrix=score_matrix,
        top_scores=scores_list,
        expected_goals_a=lambda_a, expected_goals_b=lambda_b,
        goals_dist_a=g_dist_a, goals_dist_b=g_dist_b,
        lambda_a=lambda_a, lambda_b=lambda_b,
        stats=stats,
        elo_a=elo_a, elo_b=elo_b
    )

def simulate_knockout_match(team_a: str, team_b: str, matches_df: pd.DataFrame, 
                            rankings_dict: dict, reference_date: str, 
                            n_sims: int = 1000) -> str:
    """
    Simula un partido de eliminatoria y devuelve el nombre del ganador.
    Resuelve empates usando probabilidad de penales basada en Elo.
    """
    result = simulate_match(team_a, team_b, matches_df, rankings_dict, reference_date, n_sims)
    
    p_a = result.prob_win_a / 100.0
    p_b = result.prob_win_b / 100.0
    p_d = result.prob_draw / 100.0
    
    r = np.random.random()
    if r < p_a:
        return team_a
    elif r < p_a + p_b:
        return team_b
    else:
        # Draw -> penalties
        # Usar Elo para probabilidad de penales (más preciso que strength)
        from model.elo_ratings import calculate_all_elos, get_elo
        elos = calculate_all_elos(matches_df, reference_date)
        elo_a = get_elo(team_a, elos)
        elo_b = get_elo(team_b, elos)
        
        # En penales hay más paridad: rango más estrecho (0.4 - 0.6)
        elo_diff = elo_a - elo_b
        p_penalties_a = 1.0 / (1.0 + 10.0 ** (-elo_diff / 800.0))
        p_penalties_a = 0.4 + 0.2 * p_penalties_a  # Clamp a [0.4, 0.6]
        
        if np.random.random() < p_penalties_a:
            return team_a
        return team_b
