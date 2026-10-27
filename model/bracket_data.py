"""
Datos del bracket del Mundial 2026 — Resultados reales y emparejamientos.
"""

# Resultados confirmados de la Ronda de 32 (R32)
R32_RESULTS = {
    # Lado izquierdo del bracket
    ("South Africa", "Canada"): {"score": "0 - 1", "winner": "Canada", "detail": "Gol de Eustáquio 90+2'"},
    ("Brazil", "Japan"): {"score": "2 - 1", "winner": "Brazil", "detail": "Martinelli 90+5'"},
    ("Germany", "Paraguay"): {"score": "1 - 1", "winner": "Paraguay", "detail": "Paraguay gana 4-3 en penales"},
    ("Netherlands", "Morocco"): {"score": "1 - 1", "winner": "Morocco", "detail": "Marruecos gana 3-2 en penales"},
    ("Mexico", "Ecuador"): {"score": "2 - 0", "winner": "Mexico", "detail": "Quiñones, R. Jiménez"},
    ("United States", "Bosnia and Herzegovina"): {"score": "2 - 0", "winner": "United States", "detail": "Balogun, Tillman"},
    ("Switzerland", "Algeria"): {"score": "2 - 0", "winner": "Switzerland", "detail": "Embolo, Ndoye"},
    ("Argentina", "Cape Verde"): {"score": "3 - 2", "winner": "Argentina", "detail": ""},
    
    # Lado derecho del bracket
    ("Ivory Coast", "Norway"): {"score": "1 - 2", "winner": "Norway", "detail": "Nusa, Haaland"},
    ("France", "Sweden"): {"score": "3 - 0", "winner": "France", "detail": "Mbappé x2, Barcola"},
    ("England", "DR Congo"): {"score": "2 - 1", "winner": "England", "detail": "Kane x2"},
    ("Belgium", "Senegal"): {"score": "3 - 2", "winner": "Belgium", "detail": "Prórroga, Tielemans 125'"},
    ("Spain", "Austria"): {"score": "3 - 0", "winner": "Spain", "detail": "Oyarzabal x2, Porro"},
    ("Portugal", "Croatia"): {"score": "2 - 1", "winner": "Portugal", "detail": "Ronaldo (pen), Ramos 90+4'"},
    ("Australia", "Egypt"): {"score": "1 - 1", "winner": "Egypt", "detail": "Egipto gana 4-2 en penales"},
    ("Colombia", "Ghana"): {"score": "1 - 0", "winner": "Colombia", "detail": ""},
}

# Resultados confirmados de la Ronda de 16 (R16)
R16_RESULTS = {
    ("Paraguay", "France"): {"score": "0 - 1", "winner": "France", "detail": "Mbappé 70' (pen)"},
    ("Canada", "Morocco"): {"score": "0 - 3", "winner": "Morocco", "detail": "Marruecos avanza a Cuartos"},
    ("Brazil", "Norway"): {"score": "1 - 2", "winner": "Norway", "detail": "Doblete de Haaland 79', 90'"},
    ("Mexico", "England"): {"score": "2 - 3", "winner": "England", "detail": "Bellingham x2, Kane"},
    ("Spain", "Portugal"): {"score": "1 - 0", "winner": "Spain", "detail": "Mikel Merino 90+'"},
    ("United States", "Belgium"): {"score": "1 - 4", "winner": "Belgium", "detail": "De Ketelaere x2, Lukaku"},
    ("Argentina", "Egypt"): {"score": "3 - 2", "winner": "Argentina", "detail": "Remontada: Messi 83', Enzo 90+3'"},
    ("Switzerland", "Colombia"): {"score": "0 - 0", "winner": "Switzerland", "detail": "Suiza gana 4-3 en penales (Kobel ataja)"}
}

# Emparejamientos confirmados de la Ronda de 16 (R16) ordenados por bracket
R16_MATCHES_CONFIRMED = [
    # Lado izquierdo (Partidos jugados)
    ("Paraguay", "France"),          # QF Left 1
    ("Canada", "Morocco"),           # QF Left 1
    ("Spain", "Portugal"),           # QF Left 2
    ("United States", "Belgium"),    # QF Left 2
    
    # Lado derecho (Partidos jugados)
    ("Brazil", "Norway"),            # QF Right 1
    ("Mexico", "England"),           # QF Right 1
    ("Argentina", "Egypt"),          # QF Right 2
    ("Switzerland", "Colombia")      # QF Right 2
]

# R32 partidos pendientes hoy
R32_PENDING = []

def get_r32_winner(team_a, team_b):
    """Devuelve el ganador de un partido R32, o None si no se ha jugado."""
    key = (team_a, team_b)
    if key in R32_RESULTS:
        return R32_RESULTS[key]["winner"]
    key_rev = (team_b, team_a)
    if key_rev in R32_RESULTS:
        return R32_RESULTS[key_rev]["winner"]
    return None

def get_r32_score(team_a, team_b):
    """Devuelve el marcador de un partido R32, o None si no se ha jugado."""
    key = (team_a, team_b)
    if key in R32_RESULTS:
        return R32_RESULTS[key]["score"]
    key_rev = (team_b, team_a)
    if key_rev in R32_RESULTS:
        return R32_RESULTS[key_rev]["score"]
    return None


# Resultados de Cuartos de Final (QF)
QF_RESULTS = {
    ("France", "Morocco"): {"score": "2 - 0", "winner": "France", "detail": "Francia avanza a Semis"},
    ("Spain", "Belgium"): {"score": "2 - 1", "winner": "Spain", "detail": "Espana gana 2-1"},
    ("Norway", "England"): {"score": "1 - 2", "winner": "England", "detail": "Inglaterra gana 2-1 AET"},
    ("Argentina", "Switzerland"): {"score": "3 - 1", "winner": "Argentina", "detail": "Argentina gana 3-1 AET"}
}

# Resultados de Semifinales (SF)
SF_RESULTS = {
    ("France", "Spain"): {"score": "0 - 2", "winner": "Spain", "detail": "Oyarzabal 22, Porro 58"}
}

