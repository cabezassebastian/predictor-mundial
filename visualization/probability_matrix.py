"""
Matriz de calor para resultados (marcador exacto).
Estilo FotMob: fondo #1a1a1a, texto #fafafa, acento #00985f
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

def plot_probability_matrix(team_a: str, team_b: str, score_matrix: np.ndarray, output_path: str = None):
    """Genera heatmap de matriz de resultados con paleta FotMob."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 7), facecolor='#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    max_g = score_matrix.shape[0] - 1
    
    # Heatmap con colores FotMob (de #222 a #00985f)
    cmap = sns.color_palette([
        '#272727', '#1a3d2e', '#0d5c3d', '#00985f', '#33c771', '#61df6e'
    ], as_cmap=True)
    
    sns.heatmap(score_matrix, annot=True, fmt=".1f", cmap=cmap, 
                cbar_kws={'label': 'Probabilidad (%)'}, ax=ax,
                annot_kws={"size": 10, "weight": "bold", "color": "#fafafa"},
                linewidths=0.5, linecolor='#333')
    
    # Colorbar text
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color('#9f9f9f')
    cbar.ax.tick_params(colors='#9f9f9f')
    
    ax.set_xlabel(f'Goles {team_b}', fontsize=12, labelpad=10, color='#9f9f9f')
    ax.set_ylabel(f'Goles {team_a}', fontsize=12, labelpad=10, color='#9f9f9f')
    ax.set_title('MATRIZ DE PROBABILIDADES', fontsize=14, fontweight='bold', 
                 pad=16, color='#fafafa')
    
    # Resaltar top 3
    flat_indices = np.argsort(score_matrix.flatten())[::-1][:3]
    for idx in flat_indices:
        r, c = np.unravel_index(idx, score_matrix.shape)
        ax.add_patch(plt.Rectangle((c, r), 1, 1, fill=False, edgecolor='#61df6e', lw=2.5))
        
    ax.tick_params(colors='#9f9f9f')
    ax.invert_yaxis()
    
    ax.set_xticks(np.arange(max_g + 1) + 0.5)
    ax.set_yticks(np.arange(max_g + 1) + 0.5)
    ax.set_xticklabels(np.arange(max_g + 1))
    ax.set_yticklabels(np.arange(max_g + 1))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches='tight')
        
    return fig
