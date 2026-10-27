"""
Manejo de rankings FIFA.
"""
import pandas as pd

def load_rankings(csv_path: str) -> dict[str, dict]:
    """
    Carga los rankings desde el archivo CSV.
    
    Args:
        csv_path: Ruta al archivo fifa_rankings.csv
        
    Returns:
        Diccionario con la información del ranking por equipo.
    """
    try:
        df = pd.read_csv(csv_path, engine='python', encoding='utf-8')
        rankings = {}
        
        # Guardar min y max para normalización general
        min_pts = df['points'].min()
        max_pts = df['points'].max()
        
        for _, row in df.iterrows():
            rankings[row['team']] = {
                'rank': row['rank'],
                'points': row['points'],
                'confederation': row['confederation'],
                'normalized': (row['points'] - min_pts) / (max_pts - min_pts) if max_pts > min_pts else 0.5
            }
        return rankings
    except Exception as e:
        print(f"Error cargando rankings: {e}")
        return {}

def get_normalized_ranking(team: str, rankings: dict[str, dict]) -> float:
    """
    Obtiene el ranking normalizado [0,1] de un equipo.
    
    Args:
        team: Nombre del equipo
        rankings: Diccionario de rankings cargado
        
    Returns:
        Valor normalizado entre 0 y 1. 0.1 si el equipo no está.
    """
    if team in rankings:
        return rankings[team]['normalized']
    # Fallback para equipos no conocidos (10th percentile estimado)
    return 0.1
