import streamlit as st
import os
import base64
import math

# ── 1. CONFIGURAÇÃO ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── 2. LOGO ──────────────────────────────────────────────────────────────────
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

LOGO_PATH = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.png"
logo_base64 = get_image_base64(LOGO_PATH)

# ── 3. ESTADO ────────────────────────────────────────────────────────────────
if "setor_ativo" not in st.session_state:
    st.session_state["setor_ativo"] = None

setor = st.session_state["setor_ativo"]

# ── 4. GRADE SIMÉTRICA ───────────────────────────────────────────────────────
def calcular_colunas(n: int) -> int:
    if n <= 3:
        return n
    return min(range(3, 8), key=lambda c: (math.ceil(n / c) * c - n, abs(math.ceil(n / c) - 2)))

# ── 5. SVG HELPERS ───────────────────────────────────────────────────────────
def svg(paths: str, stroke: str) -> str:
    c = stroke.replace("#", "%23")
    return (
        f"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        f"viewBox='0 0 24 24' fill='none' stroke='{c}' "
        f"stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E"
        f"{paths}%3C/svg%3E"
    )

# Chapéu de formatura
P_EDU = (
    "%3Cpolygon points='12 2 2 7 12 12 22 7 12 2'/%3E"
    "%3Cpolyline points='6 9.5 6 16'/%3E"
    "%3Cpath d='M6 16c0 2 2.686 3.5 6 3.5s6-1.5 6-3.5V9.5'/%3E"
    "%3Cline x1='22' y1='7' x2='22' y2='13'/%3E"
)
# Cruz médica
P_SAU = (
    "%3Crect x='3' y='3' width='18' height='18' rx='3'/%3E"
    "%3Cline x1='12' y1='7' x2='12' y2='17'/%3E"
    "%3Cline x1='7' y1='12' x2='17' y2='12'/%3E"
)

GRAY  = "#94A3B8"
GREEN = "#2ECC71"

EDU_GRAY  = svg(P_EDU, GRAY)
EDU_GREEN = svg(P_EDU, GREEN)
SAU_GRAY  = svg(P_SAU, GRAY)
SAU_GREEN = svg(P_SAU, GREEN)

# Ícone dos municípios depende do setor ativo
MUNI_DEFAULT = SAU_GRAY  if setor == "Saúde" else EDU_GRAY
MUNI_HOVER   = SAU_GREEN if setor == "Saúde" else EDU_GREEN

# ── 6. SELETORES CSS ─────────────────────────────────────────────────────────
# Layout dos cards de setor:  [espaço | Edu | gap | Sau | espaço]
#   st.columns([2.2, 1.4, 0.12, 1.4, 2.2])
# → stHorizontalBlock :first-of-type com 5 stColumn filhos diretos
# O 1º stHorizontalBlock da página É este (as chamadas st.markdown antes
# geram stMarkdown, não stHorizontalBlock).
#
# Municipality rows são FLAT (sem st.columns aninhado), então são
# :not(:first-of-type) irmãos do mesmo stVerticalBlock. Isso elimina
# o bug de :first-of-type se repetir em contextos aninhados.

S  = "div[data-testid='stHorizontalBlock']"
SC = "div[data-testid='stColumn']"
SB = "div[data-testid='stButton']"

# Sector card buttons (2nd and 4th direct stColumn children of first HBlock)
EDU_BTN = f"{S}:first-of-type > {SC}:nth-child(2) button"
SAU_BTN = f"{S}:first-of-type > {SC}:nth-child(4) button"

# All municipality buttons (any HBlock that is NOT the first one)
MUNI_BTN = f"{S}:not(:first-of-type) {SB} button"

# ── 7. ACTIVE STATE (apenas o setor clicado recebe verde) ─────────────────────
active_css = ""
if setor == "Educação":
    active_css = f"""
  {EDU_BTN} {{
    border-color: {GREEN} !important;
    background: #162B1F !important;
    box-shadow: 0 0 0 3px rgba(46,204,113,0.18), 0 14px 36px rgba(46,204,113,0.16) !important;
    color: #ffffff !important;
  }}
  {EDU_BTN}::before {{
    background-image: url("{EDU_GREEN}") !important;
    background-color: rgba(46,204,113,0.12) !important;
  }}
"""
elif setor == "Saúde":
    active_css = f"""
  {SAU_BTN} {{
    border-color: {GREEN} !important;
    background: #162B1F !important;
    box-shadow: 0 0 0 3px rgba(46,204,113,0.18), 0 14px 36px rgba(46,204,113,0.16) !important;
    color: #ffffff !important;
  }}
  {SAU_BTN}::before {{
    background-image: url("{SAU_GREEN}") !important;
    background-color: rgba(46,204,113,0.12) !important;
  }}
"""

# ── 8. CSS PRINCIPAL ──────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');

  /* ── RESET STREAMLIT ── */
  [data-testid="stSidebar"],
  header[data-testid="stHeader"],
  .stDeployButton, footer {{ display: none !important; }}

  .stApp {{ background-color: #0E1117 !important; }}
  .block-container {{
    padding-top: 0 !important; padding-left: 0 !important;
    padding-right: 0 !important; max-width: 100% !important;
  }}

  /* ── LOGO ── */
  .brand-box {{
    position: absolute; top: 22px; left: 24px;
    display: flex; flex-direction: column;
    align-items: flex-start; z-index: 1000;
  }}
  .brand-box img  {{ width: 155px; height: auto; }}
  .brand-box span {{
    color: {GRAY}; font-family: 'Outfit', sans-serif;
    font-size: 12.5px; margin: -3px 0 0 4px; white-space: nowrap;
  }}

  /* ── LABEL ACIMA DOS CARDS ── */
  .sector-label {{
    text-align: center; color: {GRAY}; opacity: 0.5;
    font-family: 'Outfit', sans-serif; font-size: 11px;
    letter-spacing: 2.6px; text-transform: uppercase; margin: 0 0 18px;
  }}

  /* ══════════════════════════════════════════════════════════
     SECTOR CARD BUTTONS
     Seletor: primeiro stHorizontalBlock → 2ª e 4ª stColumn
  ══════════════════════════════════════════════════════════ */

  {EDU_BTN},
  {SAU_BTN} {{
    /* Dimensão de card */
    width: 100% !important;
    height: 200px !important;
    padding: 0 !important;

    /* Visual cinza base */
    background: #1E293B !important;
    border: 1.5px solid rgba(148,163,184,0.13) !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.40) !important;

    /* Flex coluna: ::before (ícone) em cima, texto em baixo */
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;

    /* Texto cinza */
    color: {GRAY} !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px !important;
    line-height: 1 !important;
    cursor: pointer !important;

    transition:
      border-color .22s ease,
      background   .22s ease,
      box-shadow   .22s ease,
      color        .22s ease,
      transform    .18s ease !important;
  }}

  /* Ícone via ::before (aparece naturalmente antes do conteúdo) */
  {EDU_BTN}::before,
  {SAU_BTN}::before {{
    content: '' !important;
    display: block !important;
    flex-shrink: 0 !important;
    width: 62px !important;
    height: 62px !important;
    border-radius: 15px !important;
    background-color: rgba(148,163,184,0.08) !important;
    background-size: 54% !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    margin-bottom: 18px !important;
    transition: background-color .22s ease, background-image .22s ease !important;
  }}

  /* Ícone correto por setor */
  {EDU_BTN}::before {{ background-image: url("{EDU_GRAY}") !important; }}
  {SAU_BTN}::before {{ background-image: url("{SAU_GRAY}") !important; }}

  /* Hover */
  {EDU_BTN}:hover,
  {SAU_BTN}:hover {{
    border-color: rgba(46,204,113,0.38) !important;
    background: #1A2A20 !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(46,204,113,0.12) !important;
    color: #ffffff !important;
  }}
  {EDU_BTN}:hover::before {{
    background-image: url("{EDU_GREEN}") !important;
    background-color: rgba(46,204,113,0.10) !important;
  }}
  {SAU_BTN}:hover::before {{
    background-image: url("{SAU_GREEN}") !important;
    background-color: rgba(46,204,113,0.10) !important;
  }}

  /* Active (verde — gerado pelo Python após clique) */
  {active_css}

  /* ══════════════════════════════════════════════════════════
     MUNICIPALITY BUTTONS
     Layout flat: cada row é um stHorizontalBlock irmão
     → :not(:first-of-type) os seleciona todos sem ambiguidade
  ══════════════════════════════════════════════════════════ */

  {MUNI_BTN} {{
    width: 100% !important;
    height: 115px !important;
    padding: 0 !important;

    background: #1E293B !important;
    border: 1.5px solid rgba(148,163,184,0.10) !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.28) !important;

    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;

    color: {GRAY} !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    line-height: 1.35 !important;
    white-space: normal !important;
    word-break: break-word !important;
    text-align: center !important;
    cursor: pointer !important;

    /* Animação de entrada (slide da esquerda) */
    animation: slideInMuni 0.34s ease both !important;

    transition:
      border-color .18s ease,
      background   .18s ease,
      box-shadow   .18s ease,
      color        .18s ease,
      transform    .16s ease !important;
  }}

  @keyframes slideInMuni {{
    from {{ opacity: 0; transform: translateX(-20px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
  }}

  /* Ícone do município via ::before */
  {MUNI_BTN}::before {{
    content: '' !important;
    display: block !important;
    flex-shrink: 0 !important;
    width: 36px !important;
    height: 36px !important;
    border-radius: 9px !important;
    background-color: rgba(148,163,184,0.08) !important;
    background-image: url("{MUNI_DEFAULT}") !important;
    background-size: 58% !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    margin-bottom: 9px !important;
    transition: background-color .18s ease, background-image .18s ease !important;
  }}

  /* Hover */
  {MUNI_BTN}:hover {{
    background: #1A2A20 !important;
    border-color: rgba(46,204,113,0.48) !important;
    color: #ffffff !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 6px 20px rgba(46,204,113,0.14) !important;
  }}
  {MUNI_BTN}:hover::before {{
    background-image: url("{MUNI_HOVER}") !important;
    background-color: rgba(46,204,113,0.10) !important;
  }}

  /* ── STAGGER DE ANIMAÇÃO por coluna (delay escalonado da esquerda → direita)
     Os botões dos municípios ocupam nth-child(2) em diante (nth-child(1)
     é a coluna de padding esquerda). Gerado para até 9 posições. ── */
  {S}:not(:first-of-type) > {SC}:nth-child(2) {SB} button {{ animation-delay: 0.04s !important; }}
  {S}:not(:first-of-type) > {SC}:nth-child(3) {SB} button {{ animation-delay: 0.10s !important; }}
  {S}:not(:first-of-type) > {SC}:nth-child(4) {SB} button {{ animation-delay: 0.16s !important; }}
  {S}:not(:first-of-type) > {SC}:nth-child(5) {SB} button {{ animation-delay: 0.22s !important; }}
  {S}:not(:first-of-type) > {SC}:nth-child(6) {SB} button {{ animation-delay: 0.28s !important; }}
  {S}:not(:first-of-type) > {SC}:nth-child(7) {SB} button {{ animation-delay: 0.34s !important; }}
  {S}:not(:first-of-type) > {SC}:nth-child(8) {SB} button {{ animation-delay: 0.40s !important; }}
  {S}:not(:first-of-type) > {SC}:nth-child(9) {SB} button {{ animation-delay: 0.46s !important; }}

  /* ── HEADER E DIVIDER ── */
  @keyframes fadeSlide {{
    from {{ opacity: 0; transform: translateX(-14px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
  }}

  .divider {{
    width: 40px; height: 2px;
    background: linear-gradient(90deg, transparent, {GREEN}, transparent);
    margin: 0 auto 22px; border-radius: 2px;
    animation: fadeSlide 0.38s ease 0.02s both;
  }}

  .muni-header {{
    text-align: center; color: {GRAY};
    font-family: 'Outfit', sans-serif; font-size: 13px;
    font-weight: 400; margin: 0;
    animation: fadeSlide 0.38s ease 0.07s both;
  }}
  .muni-header strong {{ color: {GREEN}; font-weight: 600; }}

  /* Gap entre colunas */
  {S}:not(:first-of-type) > {SC} {{
    padding-left: 5px !important;
    padding-right: 5px !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── 9. LOGO ──────────────────────────────────────────────────────────────────
if logo_base64:
    st.markdown(f"""
      <div class="brand-box">
        <img src="data:image/png;base64,{logo_base64}">
        <span>Inteligência em Gestão</span>
      </div>""", unsafe_allow_html=True)
else:
    st.markdown("""
      <div class="brand-box">
        <h2 style="color:white;margin:0">iG2P</h2>
        <span>Inteligência em Gestão</span>
      </div>""", unsafe_allow_html=True)

# ── 10. ESPAÇAMENTO + LABEL ──────────────────────────────────────────────────
st.markdown("<div style='height:130px'></div>", unsafe_allow_html=True)
st.markdown('<p class="sector-label">Selecione o Setor</p>', unsafe_allow_html=True)

# ── 11. CARD-BUTTONS DOS SETORES ─────────────────────────────────────────────
# st.columns([2.2, 1.4, 0.12, 1.4, 2.2]) → 5 stColumn filhos diretos
# nth-child(2) = Educação | nth-child(4) = Saúde
_, col_edu, _gap, col_sau, _ = st.columns([2.2, 1.4, 0.12, 1.4, 2.2])

with col_edu:
    if st.button("Educação", key="btn_educacao", use_container_width=True):
        st.session_state["setor_ativo"] = "Educação"
        st.rerun()

with col_sau:
    if st.button("Saúde", key="btn_saude", use_container_width=True):
        st.session_state["setor_ativo"] = "Saúde"
        st.rerun()

# ── 12. GRADE DE MUNICÍPIOS (layout FLAT — sem st.columns aninhado) ───────────
# Cada row é criada por uma chamada st.columns() separada, tornando todos os
# stHorizontalBlock de municípios irmãos do stHorizontalBlock dos setores.
# Isso garante que :first-of-type aponte APENAS para os cards de setor.
if setor:
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<p class="muni-header">Municípios &nbsp;·&nbsp; <strong>{setor}</strong></p>',
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if setor == "Educação":
        nomes = [
            "Alpinópolis", "Cássia", "Capetinga", "Claraval", "Delfinópolis",
            "Ibiraci", "Itaú de Minas", "Pratápolis", "Restinga",
            "São João Batista Do Glória", "São José da Barra",
            "São Roque de Minas", "São Tomás de Aquino", "Itamogi",
        ]
        suffix = "Educação"
    else:
        nomes  = ["Alpinópolis", "Bom Jesus da Penha", "Cássia", "Delfinópolis", "Itaú de Minas"]
        suffix = "Saúde"

    n_cols = calcular_colunas(len(nomes))

    # Padding lateral embutido nas colunas (sem wrapper → sem aninhamento)
    PAD   = 0.05
    C_W   = (1.0 - 2 * PAD) / n_cols
    widths = [PAD] + [C_W] * n_cols + [PAD]

    # Dividir em linhas e renderizar cada uma com st.columns() flat
    rows = [nomes[i : i + n_cols] for i in range(0, len(nomes), n_cols)]

    for row_idx, row in enumerate(rows):
        all_cols = st.columns(widths, gap="small")
        muni_cols = all_cols[1:-1]  # descarta padding esq/dir

        for i, nome in enumerate(row):
            with muni_cols[i]:
                file_name = nome.replace(" ", "_")
                path = f"pages/{file_name}_{suffix}.py"
                if st.button(nome, key=f"muni_{nome}", use_container_width=True):
                    st.session_state["setor_ativo"] = setor
                    try:
                        st.switch_page(path)
                    except Exception as e:
                        st.error(f"Página não encontrada: {path}")

        if row_idx < len(rows) - 1:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)