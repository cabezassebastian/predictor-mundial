"""
🏆 PREDICTOR MUNDIAL 2026 — MONTE CARLO
Aplicación principal CLI con interfaz interactiva.
"""

import os
import sys
import time

import numpy as np
import pandas as pd

# Asegurar que el directorio del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from data.download_data import download_all

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()


def load_data():
    """Carga los datos necesarios. Descarga si no existen."""
    if not os.path.exists(config.RESULTS_CSV):
        console.print("\n[yellow]⚠️  No se encontraron datos. Descargando...[/yellow]")
        download_all()
    
    if not os.path.exists(config.RESULTS_CSV):
        console.print("[red]❌ No se pudieron descargar los datos. Ejecuta: python data/download_data.py[/red]")
        sys.exit(1)
    
    matches_df = pd.read_csv(config.RESULTS_CSV, engine='python', encoding='utf-8')
    
    from model.fifa_ranking import load_rankings
    rankings = load_rankings(config.FIFA_RANKINGS_CSV)
    
    # Cargar goalscorers si existe
    goalscorers_df = None
    if os.path.exists(config.GOALSCORERS_CSV):
        try:
            goalscorers_df = pd.read_csv(config.GOALSCORERS_CSV, engine='python', encoding='utf-8')
        except Exception:
            pass
    
    return matches_df, rankings, goalscorers_df


def show_header():
    """Muestra el encabezado del programa."""
    header = """
[bold cyan]╔══════════════════════════════════════════════════╗
║   🏆 PREDICTOR MUNDIAL 2026 — MONTE CARLO       ║
║                                                  ║
║   Simulación basada en:                          ║
║   • Ranking FIFA (ancla)                         ║
║   • Forma reciente con decaimiento temporal      ║
║   • Calidad de rivales enfrentados               ║
║   • Ventaja histórica head-to-head               ║
║   • 100,000 simulaciones Monte Carlo             ║
╚══════════════════════════════════════════════════╝[/bold cyan]
"""
    console.print(header)


def show_menu():
    """Muestra el menú principal."""
    menu = Table(show_header=False, box=box.DOUBLE_EDGE, border_style="cyan",
                 padding=(0, 2), title="[bold]MENÚ PRINCIPAL[/bold]")
    menu.add_column(style="bold cyan", width=4)
    menu.add_column(style="white")
    menu.add_row("1.", "⚽ Analizar partido (elige 2 equipos)")
    menu.add_row("2.", "🏟️  Simular octavos de final (16 partidos)")
    menu.add_row("3.", "🏆 Simular torneo completo (→ campeón)")
    menu.add_row("4.", "📊 Top candidatos al título")
    menu.add_row("5.", "⚡ Top goleadores probables del torneo")
    menu.add_row("6.", "🔧 Calibrar modelo (backtesting 2018/2022)")
    menu.add_row("7.", "📥 Descargar/actualizar datos")
    menu.add_row("0.", "🚪 Salir")
    console.print(menu)


def select_team(prompt_text: str, exclude: str = None) -> str:
    """Muestra lista de equipos y permite seleccionar uno."""
    teams = [t for t in config.QUALIFIED_R32 if t != exclude]
    
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    table.add_column(style="cyan", width=4)
    table.add_column(style="white", width=28)
    table.add_column(style="cyan", width=4)
    table.add_column(style="white", width=28)
    
    # Mostrar en 2 columnas
    half = (len(teams) + 1) // 2
    for i in range(half):
        left = f"{i+1:2d}. {teams[i]}"
        right = ""
        if i + half < len(teams):
            right_idx = i + half
            right = f"{right_idx+1:2d}. {teams[right_idx]}"
        table.add_row(f"{i+1}", teams[i], 
                      f"{i+half+1}" if i+half < len(teams) else "",
                      teams[i+half] if i+half < len(teams) else "")
    
    console.print(f"\n[bold]{prompt_text}[/bold]")
    console.print(table)
    
    while True:
        try:
            choice = IntPrompt.ask("Número del equipo")
            if 1 <= choice <= len(teams):
                selected = teams[choice - 1]
                console.print(f"  ✅ Seleccionado: [bold]{selected}[/bold]")
                return selected
            console.print("[red]Número fuera de rango[/red]")
        except (ValueError, KeyboardInterrupt):
            console.print("[red]Entrada inválida[/red]")


def analyze_match(matches_df, rankings, goalscorers_df, reference_date,
                  team_a=None, team_b=None, show_viz=True):
    """Analiza un partido entre dos equipos."""
    from model.monte_carlo import simulate_match
    from model.team_strength import calculate_lambdas
    from model.top_scorers import get_match_top_scorers
    
    if team_a is None:
        team_a = select_team("Selecciona el EQUIPO A (local):")
    if team_b is None:
        team_b = select_team("Selecciona el EQUIPO B (visitante):", exclude=team_a)
    
    console.print(f"\n[bold cyan]⚽ {team_a} vs {team_b}[/bold cyan]")
    console.print(f"[dim]Ejecutando {config.NUM_SIMULATIONS:,} simulaciones...[/dim]\n")
    
    start_time = time.time()
    result = simulate_match(team_a, team_b, matches_df, rankings, 
                           reference_date, config.NUM_SIMULATIONS)
    elapsed = time.time() - start_time
    
    # === Mostrar resultados en consola ===
    console.print(f"[dim]Completado en {elapsed:.2f}s[/dim]\n")
    
    # Tabla de probabilidades
    prob_table = Table(title="[bold]PROBABILIDAD DE RESULTADO[/bold]", 
                       box=box.HEAVY, border_style="cyan")
    prob_table.add_column("Resultado", style="bold", width=25)
    prob_table.add_column("Probabilidad", justify="right", width=12)
    prob_table.add_column("IC 95%", justify="right", style="dim", width=20)
    
    prob_table.add_row(
        f"🔵 Victoria {team_a}",
        f"[bold cyan]{result.prob_win_a:.1f}%[/bold cyan]",
        f"{result.ci95_a[0]:.1f}% — {result.ci95_a[1]:.1f}%"
    )
    prob_table.add_row(
        f"⚪ Empate",
        f"[bold]{result.prob_draw:.1f}%[/bold]",
        f"{result.ci95_draw[0]:.1f}% — {result.ci95_draw[1]:.1f}%"
    )
    prob_table.add_row(
        f"🔴 Victoria {team_b}",
        f"[bold red]{result.prob_win_b:.1f}%[/bold red]",
        f"{result.ci95_b[0]:.1f}% — {result.ci95_b[1]:.1f}%"
    )
    console.print(prob_table)
    
    # xG
    console.print(f"\n  ⚽ xG {team_a}: [bold]{result.expected_goals_a:.2f}[/bold]")
    console.print(f"  ⚽ xG {team_b}: [bold]{result.expected_goals_b:.2f}[/bold]")
    console.print(f"  λA={result.lambda_a:.3f}, λB={result.lambda_b:.3f}")
    
    # Top 5 marcadores
    scores_table = Table(title="\n[bold]TOP 10 MARCADORES MÁS PROBABLES[/bold]",
                         box=box.SIMPLE_HEAVY, border_style="green")
    scores_table.add_column("#", style="dim", width=3)
    scores_table.add_column("Marcador", justify="center", width=12)
    scores_table.add_column("Probabilidad", justify="right", width=12)
    scores_table.add_column("Resultado", width=25)
    
    for i, (score, prob, resultado) in enumerate(result.top_scores[:10]):
        style = "green" if f"Victoria {team_a}" in resultado else \
                "red" if f"Victoria {team_b}" in resultado else "dim"
        scores_table.add_row(str(i+1), score, f"{prob:.2f}%", f"[{style}]{resultado}[/{style}]")
    
    console.print(scores_table)
    
    # Top goleadores del partido
    if goalscorers_df is not None:
        try:
            scorers = get_match_top_scorers(
                team_a, team_b, result.lambda_a, result.lambda_b,
                goalscorers_df, matches_df, reference_date, top_n=10
            )
            if scorers:
                scorer_table = Table(title="\n[bold]TOP GOLEADORES PROBABLES DEL PARTIDO[/bold]",
                                     box=box.SIMPLE_HEAVY, border_style="yellow")
                scorer_table.add_column("#", style="dim", width=3)
                scorer_table.add_column("Jugador", width=22)
                scorer_table.add_column("Selección", width=15)
                scorer_table.add_column("P(gol)", justify="right", width=10)
                
                for i, s in enumerate(scorers[:10]):
                    scorer_table.add_row(
                        str(i+1), s['player'], s['team'], f"{s['probability']:.1f}%"
                    )
                console.print(scorer_table)
        except Exception as e:
            console.print(f"[dim]  ℹ️  Goleadores no disponibles: {e}[/dim]")
    
    # === Generar visualizaciones ===
    if show_viz:
        try:
            from visualization.probability_bars import plot_probability_bars
            from visualization.probability_matrix import plot_probability_matrix
            from visualization.top_scores import plot_top_scores
            
            safe_a = team_a.replace(" ", "_")
            safe_b = team_b.replace(" ", "_")
            prefix = os.path.join(config.OUTPUT_DIR, f"{safe_a}_vs_{safe_b}")
            
            console.print("\n[dim]Generando visualizaciones...[/dim]")
            
            plot_probability_bars(
                team_a, team_b,
                result.prob_win_a, result.prob_draw, result.prob_win_b,
                result.ci95_a, result.ci95_draw, result.ci95_b,
                output_path=f"{prefix}_probabilidades.png"
            )
            
            plot_probability_matrix(
                team_a, team_b, result.score_matrix,
                output_path=f"{prefix}_matriz.png"
            )
            
            plot_top_scores(
                team_a, team_b, result.top_scores,
                output_path=f"{prefix}_top_marcadores.png"
            )
            
            console.print(f"[green]✅ Gráficos guardados en: {config.OUTPUT_DIR}/[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Error generando visualizaciones: {e}[/yellow]")
    
    return result


def simulate_r32(matches_df, rankings, goalscorers_df, reference_date):
    """Simula los 16 partidos de octavos de final."""
    from model.monte_carlo import simulate_match
    
    console.print("\n[bold cyan]🏟️  SIMULACIÓN DE OCTAVOS DE FINAL[/bold cyan]")
    console.print(f"[dim]{config.NUM_SIMULATIONS:,} simulaciones por partido[/dim]\n")
    
    results_table = Table(title="[bold]RESULTADOS OCTAVOS DE FINAL[/bold]",
                          box=box.DOUBLE_EDGE, border_style="cyan")
    results_table.add_column("#", style="dim", width=3)
    results_table.add_column("Equipo A", width=22)
    results_table.add_column("vs", justify="center", width=4)
    results_table.add_column("Equipo B", width=22)
    results_table.add_column("Favorito", style="bold green", width=22)
    results_table.add_column("%", justify="right", width=8)
    
    winners = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Simulando octavos...", total=len(config.R32_MATCHES))
        
        for i, (team_a, team_b) in enumerate(config.R32_MATCHES):
            result = simulate_match(team_a, team_b, matches_df, rankings,
                                   reference_date, config.NUM_SIMULATIONS)
            
            if result.prob_win_a >= result.prob_win_b:
                winner = team_a
                pct = result.prob_win_a + result.prob_draw * (result.prob_win_a / (result.prob_win_a + result.prob_win_b))
            else:
                winner = team_b
                pct = result.prob_win_b + result.prob_draw * (result.prob_win_b / (result.prob_win_a + result.prob_win_b))
            
            winners.append(winner)
            results_table.add_row(
                str(i+1), team_a, "vs", team_b, winner, f"{pct:.1f}%"
            )
            progress.advance(task)
    
    console.print(results_table)
    return winners


def simulate_full_tournament(matches_df, rankings, reference_date):
    """Simula el torneo completo múltiples veces."""
    from visualization.tournament_bracket import simulate_tournament, plot_tournament_results
    
    console.print("\n[bold cyan]🏆 SIMULACIÓN DEL TORNEO COMPLETO[/bold cyan]")
    console.print(f"[dim]{config.TOURNAMENT_ITERATIONS:,} iteraciones del bracket[/dim]")
    console.print(f"[dim]Tiempo estimado: ~2-5 minutos...[/dim]\n")
    
    start_time = time.time()
    results_df = simulate_tournament(matches_df, rankings, reference_date,
                                      n_iterations=config.TOURNAMENT_ITERATIONS)
    elapsed = time.time() - start_time
    
    console.print(f"\n[dim]Completado en {elapsed:.1f}s[/dim]\n")
    
    # Mostrar tabla de resultados
    display_df = results_df.sort_values('champion_pct', ascending=False)
    
    results_table = Table(title="[bold]PROBABILIDADES POR RONDA[/bold]",
                          box=box.DOUBLE_EDGE, border_style="gold1")
    results_table.add_column("Selección", style="bold", width=22)
    results_table.add_column("R32→R16", justify="right", width=10)
    results_table.add_column("R16→QF", justify="right", width=10)
    results_table.add_column("QF→SF", justify="right", width=10)
    results_table.add_column("SF→Final", justify="right", width=10)
    results_table.add_column("🏆 CAMPEÓN", justify="right", style="bold gold1", width=12)
    
    for _, row in display_df.iterrows():
        results_table.add_row(
            row['team'],
            f"{row['r16_pct']:.1f}%",
            f"{row['qf_pct']:.1f}%",
            f"{row['sf_pct']:.1f}%",
            f"{row['final_pct']:.1f}%",
            f"{row['champion_pct']:.1f}%",
        )
    
    console.print(results_table)
    
    # Generar gráfico
    try:
        output_path = os.path.join(config.OUTPUT_DIR, "torneo_completo.png")
        plot_tournament_results(display_df, output_path=output_path)
        console.print(f"\n[green]✅ Gráfico guardado en: {output_path}[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠️  Error generando gráfico: {e}[/yellow]")
    
    return results_df


def show_top_candidates(matches_df, rankings, reference_date):
    """Muestra los top candidatos al título."""
    # Reutiliza la simulación del torneo completo
    results_df = simulate_full_tournament(matches_df, rankings, reference_date)
    
    top10 = results_df.sort_values('champion_pct', ascending=False).head(10)
    
    console.print("\n[bold gold1]🏆 TOP 10 CANDIDATOS AL TÍTULO[/bold gold1]\n")
    for i, (_, row) in enumerate(top10.iterrows()):
        bar_len = int(row['champion_pct'] * 2)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        console.print(f"  {i+1:2d}. {row['team']:22s} {bar} {row['champion_pct']:.1f}%")


def show_top_scorers_tournament(matches_df, rankings, goalscorers_df, reference_date):
    """Muestra los goleadores más probables del torneo."""
    from model.top_scorers import get_match_top_scorers
    from model.team_strength import calculate_lambdas
    
    console.print("\n[bold yellow]⚡ TOP GOLEADORES PROBABLES DEL TORNEO[/bold yellow]")
    console.print("[dim]Calculando probabilidades de gol para octavos de final...[/dim]\n")
    
    all_scorers = {}
    
    for team_a, team_b in config.R32_MATCHES:
        try:
            lambda_a, lambda_b = calculate_lambdas(
                team_a, team_b, matches_df, rankings, reference_date
            )
            scorers = get_match_top_scorers(
                team_a, team_b, lambda_a, lambda_b,
                goalscorers_df, matches_df, reference_date, top_n=5
            )
            for s in scorers:
                key = (s['player'], s['team'])
                if key not in all_scorers:
                    all_scorers[key] = s['probability']
                else:
                    all_scorers[key] = max(all_scorers[key], s['probability'])
        except Exception:
            continue
    
    # Ordenar por probabilidad
    sorted_scorers = sorted(all_scorers.items(), key=lambda x: x[1], reverse=True)
    
    scorer_table = Table(title="[bold]TOP 15 GOLEADORES MÁS PROBABLES (Octavos)[/bold]",
                         box=box.HEAVY, border_style="yellow")
    scorer_table.add_column("#", style="dim", width=3)
    scorer_table.add_column("Jugador", width=22)
    scorer_table.add_column("Selección", width=18)
    scorer_table.add_column("P(gol)", justify="right", width=10)
    
    for i, ((player, team), prob) in enumerate(sorted_scorers[:15]):
        scorer_table.add_row(str(i+1), player, team, f"{prob:.1f}%")
    
    console.print(scorer_table)


def run_calibration(matches_df, rankings, reference_date):
    """Ejecuta la calibración del modelo."""
    from model.calibration import run_calibration as calibrate, grid_search_weights
    
    console.print("\n[bold cyan]🔧 CALIBRACIÓN DEL MODELO[/bold cyan]")
    console.print("[dim]Evaluando pesos actuales contra Mundiales 2018 y 2022...[/dim]\n")
    
    # Evaluar pesos actuales
    current_metrics = calibrate(matches_df, rankings, reference_date)
    
    console.print(f"  Brier Score:  {current_metrics['brier_score']:.4f}")
    console.print(f"  Log-Loss:     {current_metrics['log_loss']:.4f}")
    console.print(f"  Accuracy:     {current_metrics['accuracy']:.1f}%")
    
    # Preguntar si quiere grid search
    do_grid = Prompt.ask("\n¿Ejecutar búsqueda de pesos óptimos? (~30-60 seg)", 
                         choices=["s", "n"], default="s")
    
    if do_grid == "s":
        console.print("\n[dim]Buscando pesos óptimos (esto tardará ~30-60 segundos)...[/dim]")
        start = time.time()
        optimal = grid_search_weights(matches_df, rankings)
        elapsed = time.time() - start
        
        console.print(f"\n[dim]Búsqueda completada en {elapsed:.1f}s[/dim]\n")
        
        # Tabla comparativa
        comp_table = Table(title="[bold]COMPARACIÓN DE PESOS[/bold]",
                          box=box.DOUBLE_EDGE, border_style="cyan")
        comp_table.add_column("", width=12)
        comp_table.add_column("Ranking", justify="right", width=10)
        comp_table.add_column("Forma", justify="right", width=10)
        comp_table.add_column("Calidad", justify="right", width=10)
        comp_table.add_column("H2H", justify="right", width=10)
        comp_table.add_column("Brier", justify="right", width=10)
        comp_table.add_column("Accuracy", justify="right", width=10)
        
        comp_table.add_row(
            "Actuales",
            f"{config.RANKING_WEIGHT:.2f}", f"{config.FORM_WEIGHT:.2f}",
            f"{config.OPPONENT_QUALITY_WEIGHT:.2f}", f"{config.H2H_WEIGHT:.2f}",
            f"{current_metrics['brier_score']:.4f}", f"{current_metrics['accuracy']:.1f}%"
        )
        comp_table.add_row(
            "[bold green]Óptimos[/bold green]",
            f"[green]{optimal['weights']['ranking']:.2f}[/green]",
            f"[green]{optimal['weights']['form']:.2f}[/green]",
            f"[green]{optimal['weights']['quality']:.2f}[/green]",
            f"[green]{optimal['weights']['h2h']:.2f}[/green]",
            f"[green]{optimal['metrics']['brier_score']:.4f}[/green]",
            f"[green]{optimal['metrics']['accuracy']:.1f}%[/green]"
        )
        console.print(comp_table)


def main():
    """Punto de entrada principal."""
    show_header()
    
    # Cargar datos
    console.print("[dim]Cargando datos...[/dim]")
    matches_df, rankings, goalscorers_df = load_data()
    reference_date = "2026-06-11"  # Fecha del ranking FIFA más reciente
    console.print(f"[green]✅ Datos cargados: {len(matches_df):,} partidos[/green]")
    
    while True:
        show_menu()
        choice = Prompt.ask("\nElige una opción", choices=["0","1","2","3","4","5","6","7"])
        
        try:
            if choice == "0":
                console.print("\n[cyan]¡Hasta la próxima! 🏆[/cyan]")
                break
            elif choice == "1":
                analyze_match(matches_df, rankings, goalscorers_df, reference_date)
            elif choice == "2":
                simulate_r32(matches_df, rankings, goalscorers_df, reference_date)
            elif choice == "3":
                simulate_full_tournament(matches_df, rankings, reference_date)
            elif choice == "4":
                show_top_candidates(matches_df, rankings, reference_date)
            elif choice == "5":
                show_top_scorers_tournament(matches_df, rankings, goalscorers_df, reference_date)
            elif choice == "6":
                run_calibration(matches_df, rankings, reference_date)
            elif choice == "7":
                force = Prompt.ask("¿Sobreescribir archivos existentes?", 
                                   choices=["s", "n"], default="n") == "s"
                download_all(force=force)
                # Recargar datos
                matches_df, rankings, goalscorers_df = load_data()
        except KeyboardInterrupt:
            console.print("\n[yellow]Operación cancelada[/yellow]")
        except Exception as e:
            console.print(f"\n[red]❌ Error: {e}[/red]")
            import traceback
            traceback.print_exc()
        
        console.print()


if __name__ == "__main__":
    # Soporte para argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--match" and len(sys.argv) >= 4:
            team_a, team_b = sys.argv[2], sys.argv[3]
            n_sims = int(sys.argv[4]) if len(sys.argv) > 4 else config.NUM_SIMULATIONS
            
            matches_df, rankings, goalscorers_df = load_data()
            reference_date = "2026-06-11"
            
            config.NUM_SIMULATIONS = n_sims
            analyze_match(matches_df, rankings, goalscorers_df, reference_date,
                         team_a=team_a, team_b=team_b)
        elif sys.argv[1] == "--calibrate":
            matches_df, rankings, _ = load_data()
            reference_date = "2026-06-11"
            run_calibration(matches_df, rankings, reference_date)
        elif sys.argv[1] == "--help":
            console.print("""
[bold]Uso:[/bold]
  python app.py                              # Modo interactivo
  python app.py --match "Spain" "Uruguay"    # Analizar partido directo
  python app.py --match "Spain" "Uruguay" 200000  # Con N simulaciones
  python app.py --calibrate                  # Ejecutar calibración
""")
        else:
            main()
    else:
        main()
