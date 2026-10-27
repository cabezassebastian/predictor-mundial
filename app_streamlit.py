"""
🏆 PREDICTOR MUNDIAL 2026 — MONTE CARLO
Interfaz web estilo FotMob con Streamlit.
Ejecutar: streamlit run app_streamlit.py
"""

import os
import sys
import time

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Asegurar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

TRANSLATIONS = {
    "South Africa": "🇿🇦 Sudáfrica",
    "Canada": "🇨🇦 Canadá",
    "Brazil": "🇧🇷 Brasil",
    "Japan": "🇯🇵 Japón",
    "Germany": "🇩🇪 Alemania",
    "Paraguay": "🇵🇾 Paraguay",
    "Netherlands": "🇳🇱 Países Bajos",
    "Morocco": "🇲🇦 Marruecos",
    "Mexico": "🇲🇽 México",
    "Ecuador": "🇪🇨 Ecuador",
    "United States": "🇺🇸 Estados Unidos",
    "Bosnia and Herzegovina": "🇧🇦 Bosnia y Herzegovina",
    "Switzerland": "🇨🇭 Suiza",
    "Algeria": "🇩🇿 Argelia",
    "Argentina": "🇦🇷 Argentina",
    "Cape Verde": "🇨🇻 Cabo Verde",
    "Ivory Coast": "🇨🇮 Costa de Marfil",
    "Norway": "🇳🇴 Noruega",
    "France": "🇫🇷 Francia",
    "Sweden": "🇸🇪 Suecia",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra",
    "DR Congo": "🇨🇩 RD Congo",
    "Belgium": "🇧🇪 Bélgica",
    "Senegal": "🇸🇳 Senegal",
    "Spain": "🇪🇸 España",
    "Austria": "🇦🇹 Austria",
    "Portugal": "🇵🇹 Portugal",
    "Croatia": "🇭🇷 Croacia",
    "Australia": "🇦🇺 Australia",
    "Egypt": "🇪🇬 Egipto",
    "Colombia": "🇨🇴 Colombia",
    "Ghana": "🇬🇭 Ghana"
}

# Solo la bandera emoji (sin nombre)
FLAGS = {k: v.split(" ")[0] for k, v in TRANSLATIONS.items()}

# Nombre corto en español (sin bandera)
NAMES_ES = {
    "South Africa": "Sudáfrica", "Canada": "Canadá", "Brazil": "Brasil",
    "Japan": "Japón", "Germany": "Alemania", "Paraguay": "Paraguay",
    "Netherlands": "Países Bajos", "Morocco": "Marruecos", "Mexico": "México",
    "Ecuador": "Ecuador", "United States": "EE.UU.", 
    "Bosnia and Herzegovina": "Bosnia", "Switzerland": "Suiza",
    "Algeria": "Argelia", "Argentina": "Argentina", "Cape Verde": "Cabo Verde",
    "Ivory Coast": "Costa de Marfil", "Norway": "Noruega", "France": "Francia",
    "Sweden": "Suecia", "England": "Inglaterra", "DR Congo": "RD Congo",
    "Belgium": "Bélgica", "Senegal": "Senegal", "Spain": "España",
    "Austria": "Austria", "Portugal": "Portugal", "Croatia": "Croacia",
    "Australia": "Australia", "Egypt": "Egipto", "Colombia": "Colombia",
    "Ghana": "Ghana"
}

ELIMINATED = [
    # Eliminados en R32
    "South Africa", "Japan", "Germany", "Netherlands",
    "Ivory Coast", "Sweden", "Ecuador",
    "Bosnia and Herzegovina", "DR Congo", "Senegal",
    "Algeria", "Austria", "Croatia",
    "Australia", "Ghana", "Cape Verde",
    # Eliminados en R16
    "Paraguay", "Canada", "Portugal", "United States",
    "Brazil", "Mexico", "Egypt", "Colombia",
    # Eliminados en QF
    "Morocco", "Belgium", "Norway", "Switzerland"
]

PHASE = "Semifinales"

# === Configuración de la página ===
st.set_page_config(
    page_title="⚽ Predictor Mundial 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CSS FOTMOB — Paleta real extraída de fotmob.com ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* === FOTMOB PALETTE ===
       --eerieBlack: #1a1a1a (bg)
       --fotMobBlack: #222 (cards)
       --charlestonGreen: #272727
       --darkCharcoal: #333 (borders)
       --onyx: #383838
       --outerSpace: #464646
       --darkSilver: #717171
       --quickSilver: #9f9f9f (secondary text)
       --fotMobGreen: #00985f (primary green)
       --accentGreen: #61df6e
       --punch: #dd3636 (red)
       --dodgerBlue: #14a0ff
    */
    
    /* === BASE === */
    .stApp {
        background-color: #1a1a1a !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    /* === SIDEBAR === */
    section[data-testid="stSidebar"] {
        background-color: #222 !important;
        border-right: 1px solid #333;
    }
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #9f9f9f !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h5 {
        color: #e8e8e8 !important;
    }
    
    /* === MATCH HEADER === */
    .match-header {
        background: #272727;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        text-align: center;
        border: 1px solid #333;
    }
    .match-header .phase-badge {
        display: inline-block;
        background: #00985f;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }
    .match-header .teams-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2.5rem;
    }
    .match-header .team-block {
        text-align: center;
        min-width: 110px;
    }
    .match-header .team-flag {
        font-size: 3.2rem;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    .match-header .team-name {
        color: #fafafa;
        font-size: 1rem;
        font-weight: 600;
    }
    .match-header .vs-text {
        color: #464646;
        font-size: 1.2rem;
        font-weight: 800;
        letter-spacing: 2px;
    }
    
    /* === PROB BAR === */
    .prob-bar-container {
        background: #222;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid #333;
    }
    .prob-bar {
        display: flex;
        height: 36px;
        border-radius: 6px;
        overflow: hidden;
        margin: 0.6rem 0;
    }
    .prob-bar .win-a { background: #00985f; }
    .prob-bar .draw { background: #596470; }
    .prob-bar .win-b { background: #dd3636; }
    .prob-bar span {
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .prob-labels {
        display: flex;
        justify-content: space-between;
        color: #9f9f9f;
        font-size: 0.75rem;
    }
    
    /* === STAT ROW (FOTMOB STYLE) === */
    .stat-row {
        display: flex;
        align-items: center;
        padding: 0.55rem 0;
        border-bottom: 1px solid #333;
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-value-left {
        width: 44px;
        text-align: right;
        font-weight: 600;
        font-size: 0.95rem;
        color: #fafafa;
    }
    .stat-value-right {
        width: 44px;
        text-align: left;
        font-weight: 600;
        font-size: 0.95rem;
        color: #fafafa;
    }
    .stat-bar-container {
        flex: 2;
        display: flex;
        gap: 3px;
        align-items: center;
    }
    .stat-bar-left {
        flex: 1;
        height: 5px;
        border-radius: 3px;
        background: #383838;
        overflow: hidden;
        display: flex;
        justify-content: flex-end;
    }
    .stat-bar-right {
        flex: 1;
        height: 5px;
        border-radius: 3px;
        background: #383838;
        overflow: hidden;
    }
    .stat-bar-left .fill {
        height: 100%;
        border-radius: 3px;
        background: #00985f;
    }
    .stat-bar-right .fill {
        height: 100%;
        border-radius: 3px;
        background: #dd3636;
    }
    
    /* === STATS CARD === */
    .stats-card {
        background: #222;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #333;
        margin-bottom: 1rem;
    }
    .stats-card-title {
        color: #9f9f9f;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #333;
    }
    
    /* === XG DISPLAY === */
    .xg-display {
        display: flex;
        justify-content: space-around;
        text-align: center;
        margin: 1rem 0;
    }
    .xg-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #fafafa;
    }
    .xg-label {
        color: #9f9f9f;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* === BRACKET === */
    .bracket-match {
        background: #272727;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 4px 0;
        font-size: 0.8rem;
    }
    .bracket-match.played {
        opacity: 0.85;
    }
    .bracket-match .winner {
        color: #00985f;
        font-weight: 700;
    }
    .bracket-match .loser {
        color: #717171;
    }
    
    /* === TABS (FOTMOB SEGMENTED CONTROL) === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #272727;
        border-radius: 10px;
        padding: 3px;
        border: 1px solid #333;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #9f9f9f;
        font-weight: 500;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #383838 !important;
        color: #fafafa !important;
    }
    
    /* === GENERAL === */
    h1, h2, h3, h4, h5 { color: #fafafa !important; }
    .stMetric label { color: #9f9f9f !important; }
    .stMetric [data-testid="stMetricValue"] { color: #fafafa !important; }
    .stMarkdown p { color: #e8e8e8; }
    .stCaption { color: #717171 !important; }
    
    /* Streamlit button */
    .stButton > button[kind="primary"] {
        background-color: #00985f !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #33c771 !important;
    }
    
    /* Streamlit slider */
    .stSlider [data-testid="stThumbValue"] { color: #fafafa !important; }
    
    /* DataFrame */
    .stDataFrame { border: 1px solid #333 !important; border-radius: 8px; }
    
    /* Success/warning messages */
    .stSuccess { background-color: #00985f22 !important; border-color: #00985f !important; }
    .stWarning { background-color: #dd363622 !important; border-color: #dd3636 !important; }
    
    /* Streamlit branding and header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Carga datos con cache de Streamlit."""
    if not os.path.exists(config.RESULTS_CSV):
        from data.download_data import download_all
        download_all()
    try:
        matches_df = pd.read_csv(config.RESULTS_CSV, engine='python', encoding='utf-8')
    except:
        matches_df = pd.DataFrame()
    
    from model.fifa_ranking import load_rankings
    rankings = load_rankings(config.FIFA_RANKINGS_CSV)
    
    goalscorers_df = None
    if os.path.exists(config.GOALSCORERS_CSV):
        try:
            goalscorers_df = pd.read_csv(config.GOALSCORERS_CSV, engine='python', encoding='utf-8')
        except:
            goalscorers_df = pd.DataFrame()
    
    return matches_df, rankings, goalscorers_df


def render_match_header(team_a, team_b):
    """Renderiza el header del partido estilo FotMob."""
    flag_a = FLAGS.get(team_a, "🏳️")
    flag_b = FLAGS.get(team_b, "🏳️")
    name_a = NAMES_ES.get(team_a, team_a)
    name_b = NAMES_ES.get(team_b, team_b)
    
    st.markdown(f"""
    <div class="match-header">
        <div class="phase-badge">🏆 Fase Eliminatoria — Mundial 2026</div>
        <div class="teams-row">
            <div class="team-block">
                <div class="team-flag">{flag_a}</div>
                <div class="team-name">{name_a}</div>
            </div>
            <div class="vs-text">VS</div>
            <div class="team-block">
                <div class="team-flag">{flag_b}</div>
                <div class="team-name">{name_b}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_prob_bar(prob_a, prob_draw, prob_b, team_a, team_b):
    """Renderiza la barra de probabilidad tricolor estilo FotMob."""
    name_a = NAMES_ES.get(team_a, team_a)
    name_b = NAMES_ES.get(team_b, team_b)
    
    st.markdown(f"""
    <div class="prob-bar-container">
        <div class="prob-labels">
            <span>Victoria {name_a}</span>
            <span>Empate</span>
            <span>Victoria {name_b}</span>
        </div>
        <div class="prob-bar">
            <span class="win-a" style="width:{prob_a}%">{prob_a:.1f}%</span>
            <span class="draw" style="width:{prob_draw}%">{prob_draw:.1f}%</span>
            <span class="win-b" style="width:{prob_b}%">{prob_b:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_row(label, val_a, val_b, is_percentage=False):
    """Renderiza una fila de estadísticas enfrentadas estilo FotMob."""
    total = val_a + val_b if (val_a + val_b) > 0 else 1
    pct_a = (val_a / total) * 100
    pct_b = (val_b / total) * 100
    
    fmt = f"{val_a:.0f}%" if is_percentage else f"{val_a:.1f}"
    fmt_b = f"{val_b:.0f}%" if is_percentage else f"{val_b:.1f}"
    
    # Color: el que tiene más se resalta (FotMob green/red)
    color_a = "#00985f" if val_a > val_b else "#9f9f9f" if val_a == val_b else "#717171"
    color_b = "#dd3636" if val_b > val_a else "#9f9f9f" if val_a == val_b else "#717171"
    
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-value-left" style="color:{color_a}">{fmt}</div>
        <div class="stat-bar-container">
            <div class="stat-bar-left"><div class="fill" style="width:{pct_a}%"></div></div>
            <div class="stat-bar-right"><div class="fill" style="width:{pct_b}%"></div></div>
        </div>
        <div class="stat-value-right" style="color:{color_b}">{fmt_b}</div>
    </div>
    <div style="text-align:center;color:#6b7280;font-size:0.75rem;margin-top:-4px;margin-bottom:4px;">{label}</div>
    """, unsafe_allow_html=True)


def render_bracket():
    """Renderiza el bracket visual del torneo."""
    from visualization.html_bracket import generate_bracket_html
    html = generate_bracket_html(TRANSLATIONS, FLAGS)
    st.markdown(html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    # === Leer Query Params para Enrutamiento ===
    params = st.query_params
    if "t1" in params and "t2" in params:
        st.session_state["sel_team_a"] = params["t1"]
        st.session_state["sel_team_b"] = params["t2"]
        st.query_params.clear()

    # === Sidebar ===
    st.sidebar.markdown("## ⚽ Predictor Mundial")
    st.sidebar.markdown("---")
    
    # Solo mostrar equipos que siguen vivos en el torneo (Cuartos de Final)
    valid_teams = [t for t in config.QUALIFIED_R32 if t not in ELIMINATED]
    
    if "sel_team_a" not in st.session_state or st.session_state["sel_team_a"] not in valid_teams:
        st.session_state["sel_team_a"] = valid_teams[0]
        
    team_a = st.sidebar.selectbox("🟢 Equipo Local", valid_teams, 
                                   format_func=lambda x: TRANSLATIONS.get(x, x), key="sel_team_a")
    
    team_b_options = [t for t in valid_teams if t != team_a]
    if "sel_team_b" not in st.session_state or st.session_state["sel_team_b"] not in team_b_options:
        st.session_state["sel_team_b"] = team_b_options[0]
        
    team_b = st.sidebar.selectbox("🔴 Equipo Visitante", team_b_options, 
                                   format_func=lambda x: TRANSLATIONS.get(x, x), key="sel_team_b")
    
    n_sims = st.sidebar.slider("Simulaciones", 10_000, 500_000, 100_000, step=10_000)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### Pesos del Modelo")
    w_r = st.sidebar.slider("📊 Ranking FIFA", 0.0, 1.0, config.RANKING_WEIGHT, 0.05)
    w_f = st.sidebar.slider("📈 Forma reciente", 0.0, 1.0, config.FORM_WEIGHT, 0.05)
    w_q = st.sidebar.slider("🎯 Calidad rivales", 0.0, 1.0, config.OPPONENT_QUALITY_WEIGHT, 0.05)
    w_h = st.sidebar.slider("🤝 H2H histórico", 0.0, 1.0, config.H2H_WEIGHT, 0.05)
    
    total_w = w_r + w_f + w_q + w_h
    if abs(total_w - 1.0) > 0.01:
        st.sidebar.warning(f"⚠️ Pesos suman {total_w:.2f} (deben sumar 1.0)")
    else:
        st.sidebar.success(f"✅ Pesos válidos ({total_w:.2f})")
    
    # Actualizar config dinámicamente
    config.RANKING_WEIGHT = w_r
    config.FORM_WEIGHT = w_f
    config.OPPONENT_QUALITY_WEIGHT = w_q
    config.H2H_WEIGHT = w_h
    config.NUM_SIMULATIONS = n_sims
    
    # === Cargar datos ===
    matches_df, rankings, goalscorers_df = load_data()
    reference_date = "2026-06-11"
    
    # === Tabs principales ===
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚽ Análisis de Partido", 
        "🏆 Bracket del Torneo",
        "📊 Simulación Monte Carlo", 
        "🔧 Calibración"
    ])
    
    # =============================================
    # TAB 1: ANÁLISIS DE PARTIDO (ESTILO FOTMOB)
    # =============================================
    with tab1:
        render_match_header(team_a, team_b)
        
        VALID_MATCHES = [
            ("England", "Argentina"), ("Argentina", "England"), # SF 2
            ("Spain", "England"), ("England", "Spain"), # Posible Final
            ("Spain", "Argentina"), ("Argentina", "Spain"), # Posible Final
            ("France", "England"), ("England", "France"), # Posible 3er Puesto
            ("France", "Argentina"), ("Argentina", "France") # Posible 3er Puesto
        ]
        
        is_valid = (team_a, team_b) in VALID_MATCHES
        
        if not is_valid:
            st.error("🚫 ¡Acción no permitida! El Mundial ya se encuentra en rondas Finales (14 de Julio). Solo puedes simular la Semifinal 2 o los posibles cruces por Medallas.")
            simulate_btn = st.button("🎲 Simular Partido", type="primary", use_container_width=True, disabled=True)
        else:
            simulate_btn = st.button("🎲 Simular Partido", type="primary", use_container_width=True)
            
            if simulate_btn or f"result_{team_a}_{team_b}" in st.session_state:
                if simulate_btn:
                    with st.spinner(f"Analizando {n_sims:,} simulaciones..."):
                        from model.monte_carlo import simulate_match
                        start_time = time.time()
                        result = simulate_match(team_a, team_b, matches_df, rankings,
                                              reference_date, n_sims)
                        elapsed = time.time() - start_time
                        st.session_state[f"result_{team_a}_{team_b}"] = result
                        st.session_state["last_elapsed"] = elapsed
                
                result = st.session_state.get(f"result_{team_a}_{team_b}")
                if result:
                    elapsed = st.session_state.get("last_elapsed", 0)
                    st.caption(f"⏱ {elapsed:.2f}s • {n_sims:,} simulaciones Monte Carlo")
                
                    # === BARRA DE PROBABILIDAD 1-X-2 ===
                    render_prob_bar(result.prob_win_a, result.prob_draw, result.prob_win_b, team_a, team_b)
                
                    # === xG DISPLAY ===
                    name_a = NAMES_ES.get(team_a, team_a)
                    name_b = NAMES_ES.get(team_b, team_b)
                
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-card-title">⚽ Goles Esperados (xG)</div>
                        <div class="xg-display">
                            <div>
                                <div class="xg-label">{name_a}</div>
                                <div class="xg-value">{result.expected_goals_a:.2f}</div>
                            </div>
                            <div>
                                <div class="xg-label">vs</div>
                                <div style="font-size:1.5rem;color:#464646;margin-top:0.8rem">⚽</div>
                            </div>
                            <div>
                                <div class="xg-label">{name_b}</div>
                                <div class="xg-value">{result.expected_goals_b:.2f}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                    # === ELO DISPLAY ===
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-card-title">📈 Power Index (Elo Dinámico)</div>
                        <div class="xg-display">
                            <div>
                                <div class="xg-label">{name_a}</div>
                                <div class="xg-value" style="font-size:1.8rem;color:#14a0ff">{result.elo_a:.0f}</div>
                            </div>
                            <div>
                                <div class="xg-label">vs</div>
                                <div style="font-size:1.5rem;color:#464646;margin-top:0.8rem">⚡</div>
                            </div>
                            <div>
                                <div class="xg-label">{name_b}</div>
                                <div class="xg-value" style="font-size:1.8rem;color:#14a0ff">{result.elo_b:.0f}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                    # === ESTADÍSTICAS ENFRENTADAS (ESTILO FOTMOB) ===
                    if result.stats:
                        stats = result.stats
                    
                        col_stats, col_matrix = st.columns([1, 1])
                    
                        with col_stats:
                            st.markdown('<div class="stats-card"><div class="stats-card-title">📊 Estadísticas Predichas</div>', unsafe_allow_html=True)
                        
                            render_stat_row("Posesión %", stats.possession_a, stats.possession_b, is_percentage=True)
                            render_stat_row("Tiros totales", stats.shots_a, stats.shots_b)
                            render_stat_row("Tiros a puerta", stats.shots_on_target_a, stats.shots_on_target_b)
                            render_stat_row("Corners", stats.corners_a, stats.corners_b)
                            render_stat_row("Faltas", stats.fouls_a, stats.fouls_b)
                            render_stat_row("Tarjetas", stats.cards_a, stats.cards_b)
                        
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                        with col_matrix:
                            # Matriz de probabilidades
                            st.markdown('<div class="stats-card"><div class="stats-card-title">🎯 Resultados Exactos Más Probables</div>', unsafe_allow_html=True)
                        
                            scores_data = []
                            for i, (score, prob, resultado) in enumerate(result.top_scores[:8]):
                                scores_data.append({
                                    "Marcador": score,
                                    "Prob.": f"{prob:.1f}%",
                                    "Resultado": resultado
                                })
                        
                            st.dataframe(
                                pd.DataFrame(scores_data),
                                use_container_width=True,
                                hide_index=True
                            )
                            st.markdown('</div>', unsafe_allow_html=True)
                
                    # === HEATMAP DE MARCADORES ===
                    st.markdown("---")
                    from visualization.probability_matrix import plot_probability_matrix
                    fig_matrix = plot_probability_matrix(team_a, team_b, result.score_matrix)
                    st.pyplot(fig_matrix)
                    plt.close(fig_matrix)
                
                # === TOP GOLEADORES ===
                if goalscorers_df is not None:
                    try:
                        from model.top_scorers import get_match_top_scorers
                        scorers = get_match_top_scorers(
                            team_a, team_b, result.lambda_a, result.lambda_b,
                            goalscorers_df, matches_df, reference_date, top_n=10
                        )
                        if scorers:
                            st.markdown("---")
                            st.markdown('<div class="stats-card"><div class="stats-card-title">⚡ Goleadores Probables</div>', unsafe_allow_html=True)
                            scorers_data = [{
                                "#": i+1,
                                "Jugador": s['player'],
                                "Selección": NAMES_ES.get(s['team'], s['team']),
                                "P(gol)": f"{s['probability']:.1f}%"
                            } for i, s in enumerate(scorers[:10])]
                            st.dataframe(pd.DataFrame(scorers_data),
                                        use_container_width=True, hide_index=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                    except Exception:
                        pass
    
    # =============================================
    # TAB 2: BRACKET DEL TORNEO
    # =============================================
    with tab2:
        st.markdown("### 🏆 Cuadro Eliminatorio — Mundial 2026")
        st.markdown("Resultados confirmados de Octavos de Final. El torneo se encuentra en Cuartos de Final.")
        render_bracket()
    
    # =============================================
    # TAB 3: SIMULACIÓN MONTE CARLO DEL TORNEO
    # =============================================
    with tab3:
        st.markdown("### 📊 Simulación Monte Carlo del Torneo Restante")
        st.markdown("Ejecuta miles de iteraciones desde los Cuartos de Final para calcular la probabilidad de los 8 equipos restantes de ganar el título.")
        
        n_tournament = st.number_input("Número exacto de iteraciones (1 - 20,000)", 
                                       min_value=1, max_value=20000, 
                                       value=config.TOURNAMENT_ITERATIONS, step=100)
        
        if st.button("🏆 Simular Torneo Completo", type="primary"):
            with st.spinner(f"Simulando {n_tournament:,} torneos... (2-5 min)"):
                from visualization.tournament_bracket import simulate_tournament
                start_time = time.time()
                results_df = simulate_tournament(matches_df, rankings, reference_date,
                                                  n_iterations=n_tournament)
                elapsed = time.time() - start_time
            
            st.success(f"✅ Completado en {elapsed:.1f}s")
            st.session_state["tournament_results"] = results_df
        
        if "tournament_results" in st.session_state:
            results_df = st.session_state["tournament_results"]
            
            # Limpiar tabla para que solo queden los 8 equipos vivos (champion_pct > 0)
            display_df = results_df[results_df['champion_pct'] > 0].sort_values('champion_pct', ascending=False)
            
            st.markdown('<div class="stats-card"><div class="stats-card-title">🏆 Probabilidad de Ser Campeón (Cuartos de Final)</div>', unsafe_allow_html=True)
            top_teams = display_df.head(8)
            
            fig, ax = plt.subplots(figsize=(12, 6), facecolor='#1a1a1a')
            ax.set_facecolor('#1a1a1a')
            
            colors_list = ['#00985f', '#0da868', '#1ab871', '#27c87a', '#33c771',
                          '#3fcf7e', '#4bd78b', '#57df98', '#63e7a5', '#6fefb2']
            bars = ax.barh(range(len(top_teams)-1, -1, -1), top_teams['champion_pct'].values, 
                          color=colors_list[:len(top_teams)], height=0.6, 
                          edgecolor='none')
            
            teams_labels = [f"{FLAGS.get(t, '')} {NAMES_ES.get(t, t)}" for t in top_teams['team'].values]
            ax.set_yticks(range(len(top_teams)-1, -1, -1))
            ax.set_yticklabels(teams_labels, color='#fafafa', fontsize=11)
            ax.tick_params(colors='#464646', left=False)
            
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.xaxis.set_visible(False)
            
            for bar, val in zip(bars, top_teams['champion_pct'].values):
                ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                       f'{val:.1f}%', va='center', color='#fafafa', fontsize=11, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Tabla completa
            st.markdown("---")
            st.markdown("##### 📋 Probabilidades por Ronda")
            
            # Traducir nombres de equipos
            display_df_es = display_df.copy()
            display_df_es['team'] = display_df_es['team'].apply(
                lambda t: f"{FLAGS.get(t, '')} {NAMES_ES.get(t, t)}"
            )
            
            st.dataframe(
                display_df_es.rename(columns={
                    'team': 'Selección',
                    'r32_pct': 'R32 %',
                    'r16_pct': 'R16 %',
                    'qf_pct': 'QF %',
                    'sf_pct': 'SF %',
                    'final_pct': 'Final %',
                    'champion_pct': '🏆 Campeón %'
                }),
                use_container_width=True,
                hide_index=True
            )
    
    # =============================================
    # TAB 4: CALIBRACIÓN
    # =============================================
    with tab4:
        st.markdown("### 🔧 Calibración del Modelo")
        st.markdown("""
        Evalúa los pesos del modelo contra resultados reales de los Mundiales 2018 (Rusia) 
        y 2022 (Qatar). Calcula **Brier Score**, **Log-Loss** y **Accuracy**.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Evaluar Pesos Actuales", use_container_width=True):
                with st.spinner("Evaluando..."):
                    from model.calibration import run_calibration
                    metrics = run_calibration(matches_df, rankings, reference_date)
                    st.session_state["calibration_metrics"] = metrics
        
        with col2:
            if st.button("🔍 Buscar Pesos Óptimos (~30-60s)", use_container_width=True):
                with st.spinner("Buscando pesos óptimos (~1,771 combinaciones)..."):
                    from model.calibration import grid_search_weights
                    optimal = grid_search_weights(matches_df, rankings)
                    st.session_state["optimal_weights"] = optimal
        
        if "calibration_metrics" in st.session_state:
            m = st.session_state["calibration_metrics"]
            col1, col2, col3 = st.columns(3)
            col1.metric("Brier Score", f"{m['brier_score']:.4f}")
            col2.metric("Log-Loss", f"{m['log_loss']:.4f}")
            col3.metric("Accuracy", f"{m['accuracy']:.1f}%")
        
        if "optimal_weights" in st.session_state:
            opt = st.session_state["optimal_weights"]
            st.markdown("##### Pesos Óptimos Encontrados")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Ranking", f"{opt['weights']['ranking']:.2f}",
                        delta=f"{opt['weights']['ranking'] - config.RANKING_WEIGHT:+.2f}")
            col2.metric("Forma", f"{opt['weights']['form']:.2f}",
                        delta=f"{opt['weights']['form'] - config.FORM_WEIGHT:+.2f}")
            col3.metric("Calidad", f"{opt['weights']['quality']:.2f}",
                        delta=f"{opt['weights']['quality'] - config.OPPONENT_QUALITY_WEIGHT:+.2f}")
            col4.metric("H2H", f"{opt['weights']['h2h']:.2f}",
                        delta=f"{opt['weights']['h2h'] - config.H2H_WEIGHT:+.2f}")
            
            st.markdown(f"**Brier Score óptimo:** {opt['metrics']['brier_score']:.4f}")
            st.markdown(f"**Accuracy óptima:** {opt['metrics']['accuracy']:.1f}%")
            
            if st.button("✅ Aplicar Pesos Óptimos"):
                config.RANKING_WEIGHT = opt['weights']['ranking']
                config.FORM_WEIGHT = opt['weights']['form']
                config.OPPONENT_QUALITY_WEIGHT = opt['weights']['quality']
                config.H2H_WEIGHT = opt['weights']['h2h']
                st.success("Pesos actualizados para esta sesión")
                st.rerun()


if __name__ == "__main__":
    main()
