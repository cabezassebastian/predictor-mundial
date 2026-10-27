"""
Modelo Dixon-Coles para predicción de resultados de fútbol.

El modelo Dixon-Coles (1997) es el estándar de la industria para predicción
de marcadores de fútbol. Mejora el modelo Poisson independiente corrigiendo
la correlación entre goles de ambos equipos, especialmente para resultados
de marcador bajo (0-0, 1-0, 0-1, 1-1).

Referencia: Dixon, M.J. & Coles, S.G. (1997). "Modelling Association 
Football Scores and Inefficiencies in the Football Betting Market"
"""
import numpy as np
from scipy.stats import poisson
import math


def dixon_coles_tau(x: int, y: int, lambda_a: float, lambda_b: float, rho: float) -> float:
    """
    Factor de corrección tau de Dixon-Coles.
    
    Corrige la probabilidad conjunta P(X=x, Y=y) para resultados de
    marcador bajo donde la independencia Poisson falla.
    
    rho < 0: hay MENOS 0-0 y 1-1 de lo esperado (equipos más ofensivos)
    rho > 0: hay MÁS 0-0 y 1-1 de lo esperado (equipos defensivos)
    
    En la práctica para fútbol internacional, rho ≈ -0.13
    
    Args:
        x: goles equipo A
        y: goles equipo B
        lambda_a: expected goals equipo A
        lambda_b: expected goals equipo B
        rho: parámetro de dependencia (típicamente entre -0.2 y 0.0)
    
    Returns:
        Factor multiplicativo tau
    """
    if x == 0 and y == 0:
        return 1.0 - lambda_a * lambda_b * rho
    elif x == 0 and y == 1:
        return 1.0 + lambda_a * rho
    elif x == 1 and y == 0:
        return 1.0 + lambda_b * rho
    elif x == 1 and y == 1:
        return 1.0 - rho
    else:
        return 1.0


def dixon_coles_probability(x: int, y: int, lambda_a: float, lambda_b: float, 
                             rho: float = -0.13) -> float:
    """
    Calcula P(X=x, Y=y) usando el modelo Dixon-Coles.
    
    Es Poisson bivariado corregido:
    P(x,y) = tau(x,y,lambda_a,lambda_b,rho) * Poisson(x|lambda_a) * Poisson(y|lambda_b)
    """
    tau = dixon_coles_tau(x, y, lambda_a, lambda_b, rho)
    p_x = poisson.pmf(x, lambda_a)
    p_y = poisson.pmf(y, lambda_b)
    return tau * p_x * p_y


def build_score_matrix_dc(lambda_a: float, lambda_b: float, max_goals: int = 6,
                           rho: float = -0.13) -> np.ndarray:
    """
    Construye la matriz de probabilidades de marcadores usando Dixon-Coles.
    
    Returns:
        Matriz (max_goals+1) x (max_goals+1) con probabilidades en porcentaje
    """
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            matrix[i, j] = dixon_coles_probability(i, j, lambda_a, lambda_b, rho) * 100.0
    
    # Normalizar para que sume exactamente 100% (por truncamiento a max_goals)
    total = matrix.sum()
    if total > 0:
        matrix = matrix * (100.0 / total)
    
    return matrix


def get_match_probabilities_dc(lambda_a: float, lambda_b: float, 
                                rho: float = -0.13) -> tuple[float, float, float]:
    """
    Calcula P(win_a), P(draw), P(win_b) usando Dixon-Coles.
    
    Más preciso que el método Poisson independiente, especialmente
    para partidos entre equipos parejos donde el empate es común.
    
    Returns:
        Tupla (prob_win_a, prob_draw, prob_win_b) como porcentajes
    """
    max_goals = 8  # Usar más goles para mayor precisión
    
    p_win_a = 0.0
    p_draw = 0.0
    p_win_b = 0.0
    
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p = dixon_coles_probability(i, j, lambda_a, lambda_b, rho)
            if i > j:
                p_win_a += p
            elif i == j:
                p_draw += p
            else:
                p_win_b += p
    
    # Normalizar
    total = p_win_a + p_draw + p_win_b
    if total > 0:
        p_win_a /= total
        p_draw /= total
        p_win_b /= total
    
    return p_win_a * 100, p_draw * 100, p_win_b * 100


def estimate_rho_from_data(matches_df, n_recent: int = 500) -> float:
    """
    Estima el parámetro rho óptimo a partir de datos reales recientes.
    
    En la práctica para fútbol internacional, rho suele estar entre -0.15 y -0.08.
    Valores negativos significan que hay menos empates a 0 y 1-1 de lo que 
    Poisson puro predice.
    """
    recent = matches_df.dropna(subset=['home_score', 'away_score']).tail(n_recent)
    
    if len(recent) < 50:
        return -0.13  # valor por defecto
    
    # Contar resultados de marcador bajo
    n_total = len(recent)
    n_00 = len(recent[(recent['home_score'] == 0) & (recent['away_score'] == 0)])
    n_11 = len(recent[(recent['home_score'] == 1) & (recent['away_score'] == 1)])
    n_10 = len(recent[(recent['home_score'] == 1) & (recent['away_score'] == 0)])
    n_01 = len(recent[(recent['home_score'] == 0) & (recent['away_score'] == 1)])
    
    # Promedios de goles
    avg_home = recent['home_score'].mean()
    avg_away = recent['away_score'].mean()
    
    # Frecuencia observada vs esperada bajo Poisson independiente
    exp_00 = poisson.pmf(0, avg_home) * poisson.pmf(0, avg_away)
    obs_00 = n_00 / n_total
    
    exp_11 = poisson.pmf(1, avg_home) * poisson.pmf(1, avg_away)
    obs_11 = n_11 / n_total
    
    # Si hay más 0-0 y 1-1 de lo esperado, rho > 0; si menos, rho < 0
    # Estimación simplificada
    if exp_00 > 0 and exp_11 > 0:
        ratio_00 = obs_00 / exp_00
        ratio_11 = obs_11 / exp_11
        # rho negativo si los ratios son < 1
        rho_est = -0.5 * (2.0 - ratio_00 - ratio_11)
        # Clamp a rango razonable
        rho_est = max(-0.25, min(0.1, rho_est))
        return rho_est
    
    return -0.13
