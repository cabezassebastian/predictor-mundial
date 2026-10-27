import os
import sys

# Importar configuraciones locales
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
from model.bracket_data import R32_RESULTS, R16_RESULTS, QF_RESULTS, SF_RESULTS

def generate_bracket_html(translations, flags):
    """
    Genera un bracket de torneo en HTML interactivo utilizando Flexbox.
    """
    # Función de ayuda para renderizar un partido
    def render_match(t1, t2, phase):
        flag1 = flags.get(t1, "🏳️")
        flag2 = flags.get(t2, "🏳️")
        
        def short_name(t):
            name = t.upper()
            if name == "UNITED STATES": return "USA"
            if name == "SOUTH AFRICA": return "RSA"
            if name == "NETHERLANDS": return "NED"
            if name == "IVORY COAST": return "CIV"
            if name == "SWITZERLAND": return "SUI"
            if name == "CAPE VERDE": return "CPV"
            if name == "DR CONGO": return "COD"
            return name[:3]
            
        n1 = short_name(t1)
        n2 = short_name(t2)
        
        key = (t1, t2)
        key_rev = (t2, t1)
        
        result_str1 = ""
        result_str2 = ""
        winner = None
        
        if phase == "R32":
            res = R32_RESULTS.get(key) or R32_RESULTS.get(key_rev)
            if res:
                winner = res["winner"]
                scores = res["score"].split("-")
                if key in R32_RESULTS:
                    result_str1, result_str2 = scores[0].strip(), scores[1].strip()
                else:
                    result_str1, result_str2 = scores[1].strip(), scores[0].strip()
        elif phase == "R16":
            res = R16_RESULTS.get(key) or R16_RESULTS.get(key_rev)
            if res:
                winner = res["winner"]
                scores = res["score"].split("-")
                if key in R16_RESULTS:
                    result_str1, result_str2 = scores[0].strip(), scores[1].strip()
                else:
                    result_str1, result_str2 = scores[1].strip(), scores[0].strip()
        elif phase == "QF":
            res = QF_RESULTS.get(key) or QF_RESULTS.get(key_rev)
            if res:
                winner = res["winner"]
                scores = res["score"].split("-")
                if key in QF_RESULTS:
                    result_str1, result_str2 = scores[0].strip(), scores[1].strip()
                else:
                    result_str1, result_str2 = scores[1].strip(), scores[0].strip()
        elif phase == "SF":
            res = SF_RESULTS.get(key) or SF_RESULTS.get(key_rev)
            if res:
                winner = res["winner"]
                scores = res["score"].split("-")
                if key in SF_RESULTS:
                    result_str1, result_str2 = scores[0].strip(), scores[1].strip()
                else:
                    result_str1, result_str2 = scores[1].strip(), scores[0].strip()
        
        color1 = "#ffffff" if winner == t1 else "#9f9f9f" if winner else "#ffffff"
        color2 = "#ffffff" if winner == t2 else "#9f9f9f" if winner else "#ffffff"
        
        return (
            f'<a href="?t1={t1}&t2={t2}" target="_self" class="match-card">'
            '<div class="team">'
            f'<span class="flag">{flag1}</span>'
            f'<span class="name" style="color:{color1}">{n1}</span>'
            f'<span class="score" style="color:{color1}">{result_str1}</span>'
            '</div>'
            '<div class="team">'
            f'<span class="flag">{flag2}</span>'
            f'<span class="name" style="color:{color2}">{n2}</span>'
            f'<span class="score" style="color:{color2}">{result_str2}</span>'
            '</div>'
            '</a>'
        )

    r32_left = config.R32_MATCHES[:8]
    r32_right = config.R32_MATCHES[8:]
    
    r16_left = [
        (config.R32_MATCHES[0], config.R32_MATCHES[1]),
        (config.R32_MATCHES[2], config.R32_MATCHES[3]),
        (config.R32_MATCHES[4], config.R32_MATCHES[5]),
        (config.R32_MATCHES[6], config.R32_MATCHES[7])
    ]
    r16_right = [
        (config.R32_MATCHES[8], config.R32_MATCHES[9]),
        (config.R32_MATCHES[10], config.R32_MATCHES[11]),
        (config.R32_MATCHES[12], config.R32_MATCHES[13]),
        (config.R32_MATCHES[14], config.R32_MATCHES[15])
    ]
    
    def get_winner_or_tbd(match_tuple, phase):
        res = None
        if phase == "R32":
            res = R32_RESULTS.get(match_tuple) or R32_RESULTS.get((match_tuple[1], match_tuple[0]))
        elif phase == "R16":
            res = R16_RESULTS.get(match_tuple) or R16_RESULTS.get((match_tuple[1], match_tuple[0]))
        elif phase == "QF":
            res = QF_RESULTS.get(match_tuple) or QF_RESULTS.get((match_tuple[1], match_tuple[0]))
        elif phase == "SF":
            res = SF_RESULTS.get(match_tuple) or SF_RESULTS.get((match_tuple[1], match_tuple[0]))
        return res["winner"] if res else "TBD"

    col1_html = "".join([f'<div class="match-wrapper r32">{render_match(m[0], m[1], "R32")}</div>' for m in r32_left])
    col7_html = "".join([f'<div class="match-wrapper r32">{render_match(m[0], m[1], "R32")}</div>' for m in r32_right])
    
    col2_html = ""
    for m1, m2 in r16_left:
        w1, w2 = get_winner_or_tbd(m1, "R32"), get_winner_or_tbd(m2, "R32")
        if w1 == "TBD" or w2 == "TBD":
            col2_html += f'<div class="match-wrapper r16"><div class="match-card tbd">Ronda 16<br>Julio</div></div>'
        else:
            col2_html += f'<div class="match-wrapper r16">{render_match(w1, w2, "R16")}</div>'

    col6_html = ""
    for m1, m2 in r16_right:
        w1, w2 = get_winner_or_tbd(m1, "R32"), get_winner_or_tbd(m2, "R32")
        if w1 == "TBD" or w2 == "TBD":
            col6_html += f'<div class="match-wrapper r16"><div class="match-card tbd">Ronda 16<br>Julio</div></div>'
        else:
            col6_html += f'<div class="match-wrapper r16">{render_match(w1, w2, "R16")}</div>'
            
    qf_left = [
        ((config.R32_MATCHES[0], config.R32_MATCHES[1]), (config.R32_MATCHES[2], config.R32_MATCHES[3])),
        ((config.R32_MATCHES[4], config.R32_MATCHES[5]), (config.R32_MATCHES[6], config.R32_MATCHES[7]))
    ]
    col3_html = ""
    for m1_pair, m2_pair in qf_left:
        w1_r32_1, w1_r32_2 = get_winner_or_tbd(m1_pair[0], "R32"), get_winner_or_tbd(m1_pair[1], "R32")
        w2_r32_1, w2_r32_2 = get_winner_or_tbd(m2_pair[0], "R32"), get_winner_or_tbd(m2_pair[1], "R32")
        
        w1 = get_winner_or_tbd((w1_r32_1, w1_r32_2), "R16") if w1_r32_1 != "TBD" and w1_r32_2 != "TBD" else "TBD"
        w2 = get_winner_or_tbd((w2_r32_1, w2_r32_2), "R16") if w2_r32_1 != "TBD" and w2_r32_2 != "TBD" else "TBD"
        
        if w1 == "TBD" or w2 == "TBD":
            col3_html += f'<div class="match-wrapper qf"><div class="match-card tbd">Cuartos<br>9-10 Jul</div></div>'
        else:
            # En QF aún no hay resultados en bracket_data.py
            # Pero podemos renderizar el card clickable igual
            col3_html += f'<div class="match-wrapper qf">{render_match(w1, w2, "QF")}</div>'

    qf_right = [
        ((config.R32_MATCHES[8], config.R32_MATCHES[9]), (config.R32_MATCHES[10], config.R32_MATCHES[11])),
        ((config.R32_MATCHES[12], config.R32_MATCHES[13]), (config.R32_MATCHES[14], config.R32_MATCHES[15]))
    ]
    col5_html = ""
    for m1_pair, m2_pair in qf_right:
        w1_r32_1, w1_r32_2 = get_winner_or_tbd(m1_pair[0], "R32"), get_winner_or_tbd(m1_pair[1], "R32")
        w2_r32_1, w2_r32_2 = get_winner_or_tbd(m2_pair[0], "R32"), get_winner_or_tbd(m2_pair[1], "R32")
        
        w1 = get_winner_or_tbd((w1_r32_1, w1_r32_2), "R16") if w1_r32_1 != "TBD" and w1_r32_2 != "TBD" else "TBD"
        w2 = get_winner_or_tbd((w2_r32_1, w2_r32_2), "R16") if w2_r32_1 != "TBD" and w2_r32_2 != "TBD" else "TBD"
        
        if w1 == "TBD" or w2 == "TBD":
            col5_html += f'<div class="match-wrapper qf"><div class="match-card tbd">Cuartos<br>11 Jul</div></div>'
        else:
            col5_html += f'<div class="match-wrapper qf">{render_match(w1, w2, "QF")}</div>'
            
    # Determinar SF 1 (Lado Izquierdo)
    w_qf1 = get_winner_or_tbd(("France", "Morocco"), "QF")
    w_qf2 = get_winner_or_tbd(("Spain", "Belgium"), "QF")
    sf1_html = f'<div class="match-wrapper sf">{render_match(w_qf1, w_qf2, "SF")}</div>' if w_qf1 != "TBD" and w_qf2 != "TBD" else '<div class="match-wrapper sf"><div class="match-card tbd">Semi 1<br>14 Jul</div></div>'

    # Determinar SF 2 (Lado Derecho)
    w_qf3 = get_winner_or_tbd(("Norway", "England"), "QF")
    w_qf4 = get_winner_or_tbd(("Argentina", "Switzerland"), "QF")
    sf2_html = f'<div class="match-wrapper sf">{render_match(w_qf3, w_qf4, "SF")}</div>' if w_qf3 != "TBD" and w_qf4 != "TBD" else '<div class="match-wrapper sf"><div class="match-card tbd">Semi 2<br>15 Jul</div></div>'
    
    col4_html = (
        '<div class="center-column">'
        '<div class="trophy">🏆</div>'
        '<div class="champion-label">CAMPEÓN</div>'
        '<div class="sf-container">'
        f'{sf1_html}'
        '<div class="match-wrapper final"><div class="match-card tbd">FINAL<br>19 Jul</div></div>'
        f'{sf2_html}'
        '</div>'
        '<div class="match-wrapper third-place"><div class="match-card tbd">3ER PUESTO<br>18 Jul</div></div>'
        '</div>'
    )

    css = """<style>
    .bracket-container {
        display: flex;
        justify-content: space-between;
        background-color: #1a1a1a;
        padding: 20px 5px;
        border-radius: 12px;
        overflow-x: auto;
        font-family: 'Inter', sans-serif;
        min-width: 1000px;
    }
    .bracket-col {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        gap: 15px;
        width: 120px;
        position: relative;
    }
    .bracket-col.col2 { height: 100%; justify-content: space-around; }
    .bracket-col.col6 { height: 100%; justify-content: space-around; }
    
    .match-wrapper {
        position: relative;
        display: flex;
        align-items: center;
        margin: 5px 0;
    }
    .match-wrapper.r32 { height: 50px; }
    .match-wrapper.r16 { height: 120px; }
    .match-wrapper.qf { height: 260px; }
    
    .match-card {
        background-color: #222;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 4px 6px;
        width: 100%;
        text-decoration: none !important;
        display: flex;
        flex-direction: column;
        gap: 2px;
        transition: all 0.2s;
        cursor: pointer;
        z-index: 10;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .match-card:hover {
        border-color: #00985f;
        box-shadow: 0 0 10px rgba(0, 152, 95, 0.4);
        transform: scale(1.05);
    }
    .team {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
    }
    .flag {
        font-size: 12px;
    }
    .name {
        flex-grow: 1;
        font-weight: 600;
        color: #fff;
    }
    .score {
        font-weight: 700;
        min-width: 15px;
        text-align: right;
        color: #fff;
    }
    .tbd {
        justify-content: center;
        align-items: center;
        color: #717171;
        text-align: center;
        height: 40px;
        font-size: 10px;
        background-color: #1f1f1f;
    }
    .center-column {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 250px;
        position: relative;
    }
    .trophy {
        font-size: 40px;
        color: #717171;
    }
    .champion-label {
        color: #717171;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 20px;
    }
    .sf-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        gap: 10px;
    }
    .sf-container .match-wrapper {
        width: 30%;
    }
    .sf-container .final {
        width: 35%;
        transform: scale(1.1);
    }
    .final .match-card {
        border-color: #ffd700;
        background-color: #2a2a22;
    }
    .third-place {
        margin-top: 20px;
        width: 40%;
    }
    .third-place .match-card {
        border-color: #14a0ff;
    }
    
    /* Lineas conectoras ocultas para simplificar en Streamlit,
       pero el layout CSS Grid/Flex las mantiene alineadas. */
    </style>
    """
    
    html = css + (
        '<div class="bracket-container">'
        f'<div class="bracket-col col1">{col1_html}</div>'
        f'<div class="bracket-col col2">{col2_html}</div>'
        f'<div class="bracket-col col3">{col3_html}</div>'
        f'{col4_html}'
        f'<div class="bracket-col col5">{col5_html}</div>'
        f'<div class="bracket-col col6">{col6_html}</div>'
        f'<div class="bracket-col col7">{col7_html}</div>'
        '</div>'
    )
    
    import re
    html = re.sub(r'^\s+', '', html, flags=re.MULTILINE)
    return html
