"""
Simulación y visualización del torneo completo.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rich.progress import track

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
from model.monte_carlo import simulate_knockout_match

def simulate_tournament(matches_df: pd.DataFrame, rankings_dict: dict, 
                        reference_date: str, n_iterations: int = 1000) -> pd.DataFrame:
    """
    Simula el torneo completo N veces y cuenta hasta dónde llega cada equipo.
    """
    teams = config.QUALIFIED_R32
    results = {team: {'r32': 0, 'r16': 0, 'qf': 0, 'sf': 0, 'final': 0, 'champion': 0} for team in teams}
    
    from model.bracket_data import R16_MATCHES_CONFIRMED, R16_RESULTS, QF_RESULTS, SF_RESULTS
    
    # Pre-calcular resultados fijos
    for t1, t2 in config.R32_MATCHES:
        results[t1]['r32'] = n_iterations
        results[t2]['r32'] = n_iterations
        
    for m in R16_MATCHES_CONFIRMED:
        results[m[0]]['r16'] = n_iterations
        results[m[1]]['r16'] = n_iterations
        
    qf_teams = ["France", "Morocco", "Spain", "Belgium", "Norway", "England", "Argentina", "Switzerland"]
    for team in qf_teams:
        results[team]['qf'] = n_iterations
        
    sf_teams = ["France", "Spain", "England", "Argentina"]
    for team in sf_teams:
        results[team]['sf'] = n_iterations
        
    # España ya está en la final, Francia en el 3er puesto
    results["Spain"]['final'] = n_iterations
        
    for it in track(range(n_iterations), description=f"Simulando {n_iterations} torneos desde Semifinales..."):
        # SF 2: England vs Argentina
        sf2_winner = simulate_knockout_match("England", "Argentina", matches_df, rankings_dict, reference_date, n_sims=1)
        sf2_loser = "England" if sf2_winner == "Argentina" else "Argentina"
        
        results[sf2_winner]['final'] += 1
        
        # Final: Spain vs sf2_winner
        champion = simulate_knockout_match("Spain", sf2_winner, matches_df, rankings_dict, reference_date, n_sims=1)
        results[champion]['champion'] += 1
        
    # Convertir a DataFrame
    df_data = []
    for team, stages in results.items():
        df_data.append({
            'team': team,
            'r32_pct': (stages['r32'] / n_iterations) * 100,
            'r16_pct': (stages['r16'] / n_iterations) * 100,
            'qf_pct': (stages['qf'] / n_iterations) * 100,
            'sf_pct': (stages['sf'] / n_iterations) * 100,
            'final_pct': (stages['final'] / n_iterations) * 100,
            'champion_pct': (stages['champion'] / n_iterations) * 100
        })
        
    return pd.DataFrame(df_data)

def plot_tournament_results(results_df: pd.DataFrame, output_path: str = None):
    """Gráfico de top 10 candidatos a campeón."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0d1117')
    ax.set_facecolor('#0d1117')
    
    top10 = results_df.sort_values('champion_pct', ascending=False).head(10)
    
    y_pos = np.arange(len(top10))[::-1]
    probs = top10['champion_pct'].values
    teams = top10['team'].values
    
    # Colores degradados
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top10)))
    
    bars = ax.barh(y_pos, probs, color=colors, height=0.6)
    
    for bar, val in zip(bars, probs):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%', va='center', color='white', fontweight='bold', fontsize=12)
                
    ax.set_yticks(y_pos)
    ax.set_yticklabels(teams, fontsize=12, fontweight='bold')
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.xaxis.set_visible(False)
    ax.tick_params(left=False)
    
    plt.title('TOP 10 CANDIDATOS AL TÍTULO', fontsize=16, fontweight='bold', 
              color='white', pad=20)
              
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches='tight')
        
    return fig
