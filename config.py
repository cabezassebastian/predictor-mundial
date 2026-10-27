"""
Configuración global del Predictor del Mundial 2026.
Fuente única de verdad para equipos, emparejamientos y parámetros del modelo.
"""

# =============================================================================
# ALCANCE DE SIMULACIÓN
# =============================================================================
SIMULATION_SCOPE = "knockout"  # Solo fase eliminatoria (R32 → Final)

# =============================================================================
# EMPAREJAMIENTOS REALES DE OCTAVOS — Confirmados por FIFA (Jun 28 - Jul 3)
# Fuente única de verdad: QUALIFIED_R32 se deriva de aquí
# =============================================================================
R32_MATCHES = [
    # --- LADO IZQUIERDO DEL BRACKET ---
    ("Germany", "Paraguay"),
    ("France", "Sweden"),
    ("South Africa", "Canada"),
    ("Netherlands", "Morocco"),
    ("Portugal", "Croatia"),
    ("Spain", "Austria"),
    ("United States", "Bosnia and Herzegovina"),
    ("Belgium", "Senegal"),

    # --- LADO DERECHO DEL BRACKET ---
    ("Brazil", "Japan"),
    ("Ivory Coast", "Norway"),
    ("Mexico", "Ecuador"),
    ("England", "DR Congo"),
    ("Argentina", "Cape Verde"),
    ("Australia", "Egypt"),
    ("Switzerland", "Algeria"),
    ("Colombia", "Ghana")
]

# Derivar lista de clasificados directamente del bracket
# Si cambias R32_MATCHES, QUALIFIED_R32 se actualiza automáticamente
QUALIFIED_R32 = list(dict.fromkeys(
    team for match in R32_MATCHES for team in match
))

# =============================================================================
# ESTRUCTURA DEL BRACKET ELIMINATORIO
# Los índices se refieren a posiciones en R32_MATCHES
# =============================================================================
# R16: ganadores de estos pares de partidos se enfrentan
R16_PATHS = [(0, 1), (2, 3), (4, 5), (6, 7),   # Lado izquierdo
             (8, 9), (10, 11), (12, 13), (14, 15)]  # Lado derecho

# QF: ganadores de estos pares de R16 se enfrentan
QF_PATHS = [(0, 1), (2, 3),   # Lado izquierdo
            (4, 5), (6, 7)]    # Lado derecho

# SF: ganadores de estos pares de QF se enfrentan
SF_PATHS = [(0, 1),   # Semi 1
            (2, 3)]    # Semi 2

# =============================================================================
# PESOS DEL MODELO (HEURÍSTICOS — calibrar con calibration.py)
# =============================================================================
RANKING_WEIGHT = 0.50           # Ancla: ranking FIFA normalizado
FORM_WEIGHT = 0.25              # Forma reciente con decaimiento temporal
OPPONENT_QUALITY_WEIGHT = 0.15  # Calidad de los rivales enfrentados
H2H_WEIGHT = 0.10              # Historial directo entre ambas selecciones

# =============================================================================
# PARÁMETROS DE SIMULACIÓN
# =============================================================================
NUM_SIMULATIONS = 100_000       # Simulaciones por partido
TOURNAMENT_ITERATIONS = 10_000  # Iteraciones del torneo completo
DECAY_HALF_LIFE_DAYS = 365      # Partidos de hace 1 año pesan 50%
AVG_GOALS_PER_MATCH = 2.65      # Promedio histórico en Mundiales

# =============================================================================
# ESTADÍSTICAS AVANZADAS DE PARTIDO (promedios históricos de Mundiales)
# =============================================================================
AVG_CORNERS_PER_MATCH = 10.2    # Corners totales promedio por partido
AVG_CARDS_PER_MATCH = 3.8       # Tarjetas totales promedio por partido
SHOTS_PER_GOAL_RATIO = 9.5      # Tiros necesarios por cada gol (promedio)
ON_TARGET_RATIO = 0.35           # % de tiros que van a puerta
AVG_FOULS_PER_MATCH = 24.0      # Faltas totales promedio por partido
KNOCKOUT_INTENSITY = 1.3         # Multiplicador de tarjetas/faltas en eliminatoria

# =============================================================================
# VENTAJA DE SEDE (HOST ADVANTAGE)
# =============================================================================
HOST_COUNTRIES = ["United States", "Mexico", "Canada"]
HOST_BOOST = 0.06               # +6% boost al strength del equipo anfitrión
CONFEDERATION_BOOST = 0.03      # +3% boost a equipos del mismo continente que la sede

# =============================================================================
# MANEJO DE EQUIPOS CON DATOS INSUFICIENTES
# =============================================================================
MIN_MATCHES_THRESHOLD = 10      # Mínimo de partidos para confiar en forma
# Si un equipo tiene < MIN_MATCHES_THRESHOLD partidos:
FALLBACK_RANKING_WEIGHT = 0.80
FALLBACK_FORM_WEIGHT = 0.10
FALLBACK_OQ_WEIGHT = 0.05
FALLBACK_H2H_WEIGHT = 0.05

# =============================================================================
# MULTIPLICADORES POR TIPO DE TORNEO
# Partidos de mayor importancia pesan más en el cálculo de forma
# =============================================================================
TOURNAMENT_MULTIPLIERS = {
    "FIFA World Cup": 1.5,
    "FIFA World Cup qualification": 1.2,
    "Copa América": 1.3,
    "Copa America": 1.3,
    "UEFA Euro": 1.3,
    "UEFA Euro qualification": 1.1,
    "African Cup of Nations": 1.3,
    "Africa Cup of Nations": 1.3,
    "AFC Asian Cup": 1.3,
    "AFC Asian Cup qualification": 1.1,
    "CONCACAF Gold Cup": 1.2,
    "CONCACAF Nations League": 1.1,
    "UEFA Nations League": 1.0,
    "Confederations Cup": 1.2,
    "Finalissima": 1.2,
    "Friendly": 0.5,
    "Friendlies": 0.5,
}

# Multiplicador por defecto para torneos no listados
DEFAULT_TOURNAMENT_MULTIPLIER = 0.8

# =============================================================================
# GOLEADORES CONOCIDOS (FALLBACK)
# Tasa aproximada de goles/partido para jugadores clave de cada selección
# Se usa cuando goalscorers.csv no tiene datos recientes del jugador
# =============================================================================
KNOWN_SCORERS = {
    "Argentina": [
        ("Messi", 0.55), ("Lautaro Martínez", 0.38),
        ("Álvarez", 0.30), ("Di María", 0.15),
    ],
    "France": [
        ("Mbappé", 0.50), ("Dembélé", 0.25),
        ("Griezmann", 0.22), ("Thuram", 0.20),
    ],
    "Brazil": [
        ("Vinícius Jr", 0.35), ("Rodrygo", 0.25),
        ("Raphinha", 0.22), ("Endrick", 0.18),
    ],
    "England": [
        ("Kane", 0.45), ("Saka", 0.25),
        ("Foden", 0.20), ("Bellingham", 0.22),
    ],
    "Spain": [
        ("Morata", 0.35), ("Yamal", 0.22),
        ("Williams", 0.20), ("Olmo", 0.18),
    ],
    "Germany": [
        ("Havertz", 0.30), ("Musiala", 0.25),
        ("Füllkrug", 0.35), ("Wirtz", 0.20),
    ],
    "Portugal": [
        ("Cristiano Ronaldo", 0.45), ("Bruno Fernandes", 0.20),
        ("Leão", 0.18), ("Félix", 0.15),
    ],
    "Netherlands": [
        ("Depay", 0.30), ("Gakpo", 0.28),
        ("Simons", 0.18),
    ],
    "Belgium": [
        ("Lukaku", 0.38), ("De Bruyne", 0.15),
        ("Doku", 0.15), ("Trossard", 0.18),
    ],
    "Colombia": [
        ("Luis Díaz", 0.25), ("Córdoba", 0.22),
        ("James Rodríguez", 0.12),
    ],
    "Mexico": [
        ("Giménez", 0.30), ("Vega", 0.18),
        ("Lozano", 0.15),
    ],
    "United States": [
        ("Pulisic", 0.25), ("Weah", 0.20),
        ("Balogun", 0.22),
    ],
    "Uruguay": [
        ("Núñez", 0.35), ("Valverde", 0.15),
        ("Suárez", 0.20),
    ],
    "Croatia": [
        ("Kramarić", 0.25), ("Petković", 0.20),
        ("Modrić", 0.10),
    ],
    "Japan": [
        ("Mitoma", 0.20), ("Kubo", 0.18),
        ("Kamada", 0.15),
    ],
    "Morocco": [
        ("En-Nesyri", 0.30), ("Hakimi", 0.10),
        ("Ziyech", 0.15),
    ],
    "Senegal": [
        ("Mané", 0.30), ("Dia", 0.22),
        ("Diatta", 0.12),
    ],
    "Switzerland": [
        ("Embolo", 0.25), ("Ndoye", 0.18),
        ("Shaqiri", 0.12),
    ],
    "Norway": [
        ("Haaland", 0.55), ("Ødegaard", 0.15),
        ("Sørloth", 0.22),
    ],
    "Ecuador": [
        ("Valencia", 0.28), ("Páez", 0.15),
        ("Sarmiento", 0.12),
    ],
    "South Africa": [
        ("Zwane", 0.15), ("Mokwana", 0.12),
    ],
    "Canada": [
        ("David", 0.35), ("Davies", 0.15),
        ("Larin", 0.20),
    ],
    "Paraguay": [
        ("Enciso", 0.20), ("Almirón", 0.18),
        ("Sanabria", 0.22),
    ],
    "Ivory Coast": [
        ("Haller", 0.25), ("Pépé", 0.18),
        ("Boly", 0.05),
    ],
    "Sweden": [
        ("Isak", 0.35), ("Kulusevski", 0.20),
        ("Gyökeres", 0.30),
    ],
    "DR Congo": [
        ("Bakambu", 0.22), ("Wissa", 0.20),
    ],
    "Algeria": [
        ("Benrahma", 0.20), ("Bounedjah", 0.22),
        ("Slimani", 0.15),
    ],
    "Austria": [
        ("Arnautović", 0.25), ("Baumgartner", 0.18),
        ("Gregoritsch", 0.20),
    ],
    "Australia": [
        ("Duke", 0.20), ("Maclaren", 0.22),
        ("Leckie", 0.12),
    ],
    "Egypt": [
        ("Salah", 0.40), ("Marmoush", 0.22),
        ("Trezeguet", 0.15),
    ],
    "Cape Verde": [
        ("Rodrigues", 0.15), ("Borges", 0.12),
    ],
    "Ghana": [
        ("Kudus", 0.25), ("Ayew", 0.18),
        ("Williams", 0.15),
    ],
    "Bosnia and Herzegovina": [
        ("Džeko", 0.30), ("Demirović", 0.20),
    ],
}

# =============================================================================
# RUTAS DE ARCHIVOS
# =============================================================================
import os
import sys

if getattr(sys, 'frozen', False):
    # Si corre como exe empaquetado, usa la ruta del .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si corre normal, usa la ruta del script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

RESULTS_CSV = os.path.join(DATA_DIR, "results.csv")
GOALSCORERS_CSV = os.path.join(DATA_DIR, "goalscorers.csv")
FIFA_RANKINGS_CSV = os.path.join(DATA_DIR, "fifa_rankings.csv")

# Crear directorios si no existen
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =============================================================================
# GRUPOS DEL MUNDIAL 2026 (referencia — la fase de grupos ya concluyó)
# =============================================================================
GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Ivory Coast", "Ecuador", "Curacao"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Uruguay", "Cape Verde", "Saudi Arabia"],
    "I": ["France", "Senegal", "Norway", "Iraq"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "Colombia", "Uzbekistan", "DR Congo"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}
REFERENCE_DATE = '2026-06-11'
