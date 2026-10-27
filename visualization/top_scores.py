"""
Visualización de los marcadores más probables.
"""
import matplotlib
import matplotlib.pyplot as plt

def plot_top_scores(team_a: str, team_b: str, top_scores: list, output_path: str = None):
    """Genera tabla de marcadores probables como imagen."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 4 + len(top_scores[:10])*0.4), facecolor='#0d1117')
    ax.set_facecolor('#0d1117')
    ax.axis('off')
    
    # Preparar datos
    col_labels = ['#', 'MARCADOR', 'PROBABILIDAD', 'RESULTADO']
    cell_text = []
    cell_colors = []
    
    for i, (score, prob, res) in enumerate(top_scores[:10]):
        cell_text.append([str(i+1), score, f"{prob:.2f}%", res])
        
        # Colores según resultado
        if f"Victoria {team_a}" in res:
            c = '#4caf50' # Verde
        elif f"Victoria {team_b}" in res:
            c = '#f44336' # Rojo
        else:
            c = '#9e9e9e' # Gris
            
        row_c = ['#161b22', '#161b22', '#161b22', c]
        if i % 2 == 1:
            row_c = ['#0d1117', '#0d1117', '#0d1117', c]
            
        cell_colors.append(row_c)
    
    table = ax.table(cellText=cell_text, colLabels=col_labels, cellColours=cell_colors,
                     loc='center', cellLoc='center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2)
    
    # Formato de cabecera
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#21262d')
        else:
            if col == 3:
                cell.set_text_props(weight='bold')
                
        cell.set_edgecolor('#30363d')
        
    plt.title('TOP 10 MARCADORES MÁS PROBABLES', fontsize=16, fontweight='bold', 
              color='white', pad=20)
              
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches='tight')
        
    return fig
