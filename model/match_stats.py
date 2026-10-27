"""
Módulo de predicción de estadísticas avanzadas del partido.
Predice corners, tarjetas, tiros, posesión y faltas usando correlaciones
con el λ (expected goals) de Poisson y promedios históricos de mundiales.
"""
import os
import sys
import math
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config


@dataclass
class MatchStats:
    """Estadísticas predichas para un partido."""
    corners_a: float
    corners_b: float
    cards_a: float
    cards_b: float
    shots_a: float
    shots_b: float
    shots_on_target_a: float
    shots_on_target_b: float
    possession_a: float
    possession_b: float
    fouls_a: float
    fouls_b: float


def predict_match_stats(lambda_a: float, lambda_b: float,
                        strength_a: float, strength_b: float,
                        is_knockout: bool = True) -> MatchStats:
    """
    Predice las estadísticas del partido basándose en los expected goals
    y la fuerza relativa de cada equipo.
    
    La lógica:
    - Un equipo con mayor λ ataca más → más corners, más tiros
    - Un equipo más débil defiende más → más faltas, más tarjetas
    - Partidos eliminatorios son más intensos → más tarjetas y faltas
    """
    total_lambda = lambda_a + lambda_b
    if total_lambda == 0:
        total_lambda = 1.0
    
    share_a = lambda_a / total_lambda
    share_b = lambda_b / total_lambda
    
    total_strength = strength_a + strength_b
    if total_strength == 0:
        total_strength = 1.0
    strength_share_a = strength_a / total_strength
    strength_share_b = strength_b / total_strength
    
    intensity = config.KNOCKOUT_INTENSITY if is_knockout else 1.0
    
    # --- CORNERS ---
    # Equipos que atacan más generan más corners
    # El equipo dominante genera ~55-60% de los corners
    total_corners = config.AVG_CORNERS_PER_MATCH
    corners_a = total_corners * (0.3 + 0.4 * share_a)
    corners_b = total_corners * (0.3 + 0.4 * share_b)
    
    # --- TIROS ---
    # Más expected goals = más tiros
    shots_a = lambda_a * config.SHOTS_PER_GOAL_RATIO
    shots_b = lambda_b * config.SHOTS_PER_GOAL_RATIO
    
    # --- TIROS A PUERTA ---
    shots_on_target_a = shots_a * config.ON_TARGET_RATIO
    shots_on_target_b = shots_b * config.ON_TARGET_RATIO
    
    # --- POSESIÓN ---
    # Basada en fuerza relativa. El equipo más fuerte domina la posesión.
    # Rango realista: 35% - 65%
    base_possession_a = 50.0 + (strength_share_a - 0.5) * 30.0
    base_possession_a = max(35.0, min(65.0, base_possession_a))
    possession_a = round(base_possession_a, 1)
    possession_b = round(100.0 - possession_a, 1)
    
    # --- FALTAS ---
    # Correlación inversa con posesión: menos posesión = más faltas
    # El equipo que defiende más comete más faltas
    total_fouls = config.AVG_FOULS_PER_MATCH * intensity
    fouls_a = total_fouls * (0.3 + 0.4 * share_b)  # invertido: si B ataca, A comete más faltas
    fouls_b = total_fouls * (0.3 + 0.4 * share_a)
    
    # --- TARJETAS ---
    # Correlacionadas con faltas e intensidad del partido
    total_cards = config.AVG_CARDS_PER_MATCH * intensity
    # Equipo más débil tiende a recibir más tarjetas (juego más duro defensivo)
    cards_a = total_cards * (0.3 + 0.4 * share_b)
    cards_b = total_cards * (0.3 + 0.4 * share_a)
    
    return MatchStats(
        corners_a=round(corners_a, 1),
        corners_b=round(corners_b, 1),
        cards_a=round(cards_a, 1),
        cards_b=round(cards_b, 1),
        shots_a=round(shots_a, 1),
        shots_b=round(shots_b, 1),
        shots_on_target_a=round(shots_on_target_a, 1),
        shots_on_target_b=round(shots_on_target_b, 1),
        possession_a=possession_a,
        possession_b=possession_b,
        fouls_a=round(fouls_a, 1),
        fouls_b=round(fouls_b, 1)
    )
