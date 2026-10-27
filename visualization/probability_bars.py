"""
Gráfico de barras de probabilidad.
Estilo FotMob: #00985f (green/win), #596470 (draw), #dd3636 (red/lose)
"""
import matplotlib
import matplotlib.pyplot as plt

def plot_probability_bars(team_a: str, team_b: str, prob_win_a: float, prob_draw: float, prob_win_b: float,
                          ci95_a: tuple, ci95_draw: tuple, ci95_b: tuple, output_path: str = None):
    """Genera gráfico de barras horizontales para probabilidades de resultado."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    labels = [team_b, 'Empate', team_a]
    probs = [prob_win_b, prob_draw, prob_win_a]
    cis = [ci95_b, ci95_draw, ci95_a]
    colors = ['#dd3636', '#596470', '#00985f']
    
    y_pos = range(len(labels))
    bars = ax.barh(y_pos, probs, color=colors, height=0.55, 
                   edgecolor='none')
    
    for i, (bar, prob, ci) in enumerate(zip(bars, probs, cis)):
        width = bar.get_width()
        ax.text(width + 2, bar.get_y() + bar.get_height()/2 + 0.08, 
                f'{prob:.1f}%', va='center', color='#fafafa', 
                fontweight='bold', fontsize=15)
        
        ax.text(width + 2, bar.get_y() + bar.get_height()/2 - 0.18, 
                f'IC 95%: {ci[0]:.1f}% – {ci[1]:.1f}%', va='center', 
                color='#717171', fontsize=9)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=13, fontweight='600', color='#fafafa')
    ax.set_xlim(0, max(probs) + 25)
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.xaxis.set_visible(False)
    ax.tick_params(left=False)
    
    plt.title('PROBABILIDAD DE RESULTADO', fontsize=14, fontweight='bold', 
              color='#fafafa', pad=16)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches='tight')
    
    return fig
