import streamlit as st
import os
import base64
import math

# ── 1. CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── 2. LOGO ─────────────────────────────────────────────────────────────────
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

LOGO_PATH = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.png"
logo_base64 = get_image_base64(LOGO_PATH)

# ── 3. ESTADO INICIAL ────────────────────────────────────────────────────────
if "setor_ativo" not in st.session_state:
    st.session_state["setor_ativo"] = None

setor_escolhido = st.session_state["setor_ativo"]

# ── 4. GRADE SIMÉTRICA ───────────────────────────────────────────────────────
def calcular_colunas(n: int) -> int:
    if n <= 3:
        return n
    return min(
        range(3, 8),
        key=lambda c: (math.ceil(n / c) * c - n, abs(math.ceil(n / c) - 2)),
    )

# ── 5. ÍCONES SVG (quatro variantes: edu/sau × gray/green) ───────────────────
def make_svg(paths: str, stroke: str) -> str:
    """Retorna data-URI de um SVG com a cor de stroke indicada (URL-encoded)."""
    color = stroke.replace("#", "%23")
    return (
        f"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        f"viewBox='0 0 24 24' fill='none' stroke='{color}' "
        f"stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E"
        f"{paths}%3C/svg%3E"
    )

PATHS_EDU = (
    "%3Cpolygon points='12 2 2 7 12 12 22 7 12 2'/%3E"
    "%3Cpolyline points='6 9.5 6 16'/%3E"
    "%3Cpath d='M6 16c0 2 2.686 3.5 6 3.5s6-1.5 6-3.5V9.5'/%3E"
    "%3Cline x1='22' y1='7' x2='22' y2='13'/%3E"
)
PATHS_SAU = (
    "%3Crect x='3' y='3' width='18' height='18' rx='3'/%3E"
    "%3Cline x1='12' y1='7' x2='12' y2='17'/%3E"
    "%3Cline x1='7' y1='12' x2='17' y2='12'/%3E"
)

GRAY  = "#94A3B8"
GREEN = "#2ECC71"

SVG_EDU_GRAY  = make_svg(PATHS_EDU, GRAY)
SVG_EDU_GREEN = make_svg(PATHS_EDU, GREEN)
SVG_SAU_GRAY  = make_svg(PATHS_SAU, GRAY)
SVG_SAU_GREEN = make_svg(PATHS_SAU, GREEN)

# ── 6. ÍCONE DOS MUNICÍPIOS depende do setor selecionado ─────────────────────
# Municípios que aparecem em AMBOS os setores herdam o ícone do setor ativo.
if setor_escolhido == "Educação":
    MUNI_ICON_DEFAULT = SVG_EDU_GRAY
    MUNI_ICON_HOVER   = SVG_EDU_GREEN
elif setor_escolhido == "Saúde":
    MUNI_ICON_DEFAULT = SVG_SAU_GRAY
    MUNI_ICON_HOVER   = SVG_SAU_GREEN
else:
    MUNI_ICON_DEFAULT = SVG_EDU_GRAY   # fallback (não visível sem setor)
    MUNI_ICON_HOVER   = SVG_EDU_GREEN

# ── 7. SELETORES CSS ─────────────────────────────────────────────────────────
# Primeiro stHorizontalBlock = linha dos cards de setor
# Layout: [espaço col1 | Edu col2 | gap col3 | Sau col4 | espaço col5]
BLOCK   = "div[data-testid='stHorizontalBlock']:first-of-type"
EDU_BTN = f"{BLOCK} > div:nth-child(2) button"
SAU_BTN = f"{BLOCK} > div:nth-child(4) button"

# ── 8. ACTIVE STATE (injetado dinamicamente; vazio enquanto nenhum foi clicado)
active_edu_css = f"""
  {EDU_BTN} {{
    border: 1.5px solid {GREEN} !important;
    background: #162B1F !important;
    box-shadow: 0 0 0 3px rgba(46,204,113,0.16), 0 14px 36px rgba(46,204,113,0.14) !important;
    color: #FFFFFF !important;
  }}
  {EDU_BTN}::after {{
    background-image: url("{SVG_EDU_GREEN}") !important;
    background-color: rgba(46,204,113,0.12) !important;
  }}
""" if setor_escolhido == "Educação" else ""

active_sau_css = f"""
  {SAU_BTN} {{
    border: 1.5px solid {GREEN} !important;
    background: #162B1F !important;
    box-shadow: 0 0 0 3px rgba(46,204,113,0.16), 0 14px 36px rgba(46,204,113,0.14) !important;
    color: #FFFFFF !important;
  }}
  {SAU_BTN}::after {{
    background-image: url("{SVG_SAU_GREEN}") !important;
    background-color: rgba(46,204,113,0.12) !important;
  }}
""" if setor_escolhido == "Saúde" else ""

# ── 9. CSS PRINCIPAL ──────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');

  /* ── RESET ── */
  [data-testid="stSidebar"],
  header[data-testid="stHeader"],
  .stDeployButton, footer {{ display: none !important; }}

  .stApp {{ background-color: #0E1117 !important; }}
  .block-container {{
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
  }}

  /* ── LOGO ── */
  .brand-box {{
    position: absolute; top: 22px; left: 24px;
    display: flex; flex-direction: column;
    align-items: flex-start; z-index: 1000;
  }}
  .brand-box img  {{ width: 155px; height: auto; }}
  .brand-box span {{
    color: #94A3B8;
    font-family: 'Outfit', sans-serif;
    font-size: 12.5px; margin: -3px 0 0 4px; white-space: nowrap;
  }}

  /* ── LABEL ACIMA DOS CARDS ── */
  .sector-label {{
    text-align: center;
    color: #94A3B8;
    font-family: 'Outfit', sans-serif;
    font-size: 11px;
    letter-spacing: 2.6px;
    text-transform: uppercase;
    margin: 0 0 18px;
    opacity: 0.55;
  }}

  /* ════════════════════════════════════════
     CARD-BUTTONS DOS SETORES  –  BASE CINZA
     Ambos começam iguais; só muda via Python
  ════════════════════════════════════════ */
  {EDU_BTN},
  {SAU_BTN} {{
    width: 100% !important;
    height: 200px !important;
    padding: 0 !important;

    background: #1E293B !important;
    border: 1.5px solid rgba(148,163,184,0.12) !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.40) !important;

    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;

    color: #94A3B8 !important;           /* cinza — não ativo */
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

  /* Ícone via ::after */
  {EDU_BTN}::after,
  {SAU_BTN}::after {{
    content: '' !important;
    display: block !important;
    order: -1 !important;
    width: 60px !important;
    height: 60px !important;
    border-radius: 14px !important;
    background-color: rgba(148,163,184,0.08) !important;
    background-size: 54% !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    margin-bottom: 18px !important;
    transition: background-color .22s ease, background-image .22s ease !important;
  }}

  /* Ícones base (cinza) */
  {EDU_BTN}::after {{ background-image: url("{SVG_EDU_GRAY}") !important; }}
  {SAU_BTN}::after {{ background-image: url("{SVG_SAU_GRAY}") !important; }}

  /* Hover dos setores */
  {EDU_BTN}:hover,
  {SAU_BTN}:hover {{
    border-color: rgba(46,204,113,0.35) !important;
    background: #1A2A20 !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(46,204,113,0.10) !important;
    color: #ffffff !important;
  }}
  {EDU_BTN}:hover::after {{
    background-image: url("{SVG_EDU_GREEN}") !important;
    background-color: rgba(46,204,113,0.10) !important;
  }}
  {SAU_BTN}:hover::after {{
    background-image: url("{SVG_SAU_GREEN}") !important;
    background-color: rgba(46,204,113,0.10) !important;
  }}

  /* Active (injetado dinamicamente — vazio se nenhum foi clicado) */
  {active_edu_css}
  {active_sau_css}

  /* ════════════════════════════════════════
     ANIMAÇÃO  –  fade + slide da esquerda
  ════════════════════════════════════════ */
  @keyframes fadeSlideIn {{
    from {{ opacity: 0; transform: translateX(-22px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
  }}

  /* Header dos municípios */
  .muni-header {{
    animation: fadeSlideIn 0.40s ease both;
    animation-delay: 0.05s;

    text-align: center;
    color: #94A3B8;
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    font-weight: 400;
    letter-spacing: 0.4px;
    margin: 0;
  }}
  .muni-header strong {{ color: #2ECC71; font-weight: 600; }}

  /* Cada coluna dentro de um row de município anima com delay escalonado */
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    > div:nth-child(1)  {{ animation: fadeSlideIn 0.35s ease both; animation-delay: 0.08s; }}
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    > div:nth-child(2)  {{ animation: fadeSlideIn 0.35s ease both; animation-delay: 0.14s; }}
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    > div:nth-child(3)  {{ animation: fadeSlideIn 0.35s ease both; animation-delay: 0.20s; }}
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    > div:nth-child(4)  {{ animation: fadeSlideIn 0.35s ease both; animation-delay: 0.26s; }}
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    > div:nth-child(5)  {{ animation: fadeSlideIn 0.35s ease both; animation-delay: 0.32s; }}
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    > div:nth-child(6)  {{ animation: fadeSlideIn 0.35s ease both; animation-delay: 0.38s; }}
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    > div:nth-child(7)  {{ animation: fadeSlideIn 0.35s ease both; animation-delay: 0.44s; }}

  /* ════════════════════════════════════════
     BOTÕES DOS MUNICÍPIOS  –  card com ícone
  ════════════════════════════════════════ */
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    div[data-testid='stButton'] > button {{
    /* Dimensão de card */
    width: 100% !important;
    height: 120px !important;
    padding: 0 !important;

    /* Visual cinza base */
    background: #1E293B !important;
    border: 1.5px solid rgba(148,163,184,0.10) !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.30) !important;

    /* Flex: ícone cima, texto baixo */
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;

    color: #94A3B8 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 12.5px !important;
    font-weight: 400 !important;
    line-height: 1.3 !important;
    white-space: normal !important;
    word-break: break-word !important;
    text-align: center !important;
    cursor: pointer !important;

    transition:
      border-color .20s ease,
      background   .20s ease,
      box-shadow   .20s ease,
      color        .20s ease,
      transform    .16s ease !important;
  }}

  /* Ícone do município via ::after — cor e símbolo dependem do setor ativo */
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    div[data-testid='stButton'] > button::after {{
    content: '' !important;
    display: block !important;
    order: -1 !important;
    width: 36px !important;
    height: 36px !important;
    border-radius: 9px !important;
    background-color: rgba(148,163,184,0.08) !important;
    background-image: url("{MUNI_ICON_DEFAULT}") !important;
    background-size: 58% !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    margin-bottom: 10px !important;
    transition: background-color .20s ease, background-image .20s ease !important;
  }}

  /* Hover dos municípios */
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    div[data-testid='stButton'] > button:hover {{
    background: #1A2A20 !important;
    border-color: rgba(46,204,113,0.45) !important;
    color: #FFFFFF !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 6px 20px rgba(46,204,113,0.14) !important;
  }}
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    div[data-testid='stButton'] > button:hover::after {{
    background-image: url("{MUNI_ICON_HOVER}") !important;
    background-color: rgba(46,204,113,0.12) !important;
  }}

  /* Gap entre colunas dos municípios */
  div[data-testid='stHorizontalBlock']:not(:first-of-type)
    > div[data-testid='stColumn'] {{
    padding-left: 5px !important;
    padding-right: 5px !important;
  }}

  /* ── DIVISOR ── */
  .divider {{
    width: 40px; height: 2px;
    background: linear-gradient(90deg, transparent, #2ECC71, transparent);
    margin: 0 auto 22px;
    border-radius: 2px;
    animation: fadeSlideIn 0.35s ease both;
    animation-delay: 0.02s;
  }}
</style>
""", unsafe_allow_html=True)

# ── 10. LOGO ─────────────────────────────────────────────────────────────────
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

# ── 11. ESPAÇAMENTO ──────────────────────────────────────────────────────────
st.markdown("<div style='height:130px'></div>", unsafe_allow_html=True)

# ── 12. LABEL + CARD-BUTTONS DE SETOR ────────────────────────────────────────
st.markdown('<p class="sector-label">Selecione o Setor</p>', unsafe_allow_html=True)

# Layout: [espaço | Educação | gap | Saúde | espaço]
_, col_edu, col_gap, col_sau, _ = st.columns([2.2, 1.4, 0.12, 1.4, 2.2])

with col_edu:
    if st.button("Educação", key="btn_educacao", use_container_width=True):
        st.session_state["setor_ativo"] = "Educação"
        st.rerun()

with col_sau:
    if st.button("Saúde", key="btn_saude", use_container_width=True):
        st.session_state["setor_ativo"] = "Saúde"
        st.rerun()

# ── 13. GRADE DE MUNICÍPIOS ───────────────────────────────────────────────────
if setor_escolhido:
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<p class="muni-header">Municípios &nbsp;·&nbsp; <strong>{setor_escolhido}</strong></p>',
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Definição dos municípios por setor ───────────────────────────────────
    # Municípios presentes em ambos os setores receberão o ícone do setor ativo
    # (garantido porque MUNI_ICON_DEFAULT/HOVER já foram definidos acima
    #  com base em setor_escolhido — não há lógica por município individual)
    if setor_escolhido == "Educação":
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

    n_colunas = calcular_colunas(len(nomes))

    _, col_grid, _ = st.columns([0.05, 0.90, 0.05])
    with col_grid:
        cols = st.columns(n_colunas, gap="small")
        for i, nome in enumerate(nomes):
            with cols[i % n_colunas]:
                file_name = nome.replace(" ", "_")
                path = f"pages/{file_name}_{suffix}.py"
                if st.button(nome, key=f"muni_{nome}_{i}", use_container_width=True):
                    st.session_state["setor_ativo"] = setor_escolhido
                    try:
                        st.switch_page(path)
                    except Exception as e:
                        st.error(f"Página não encontrada: {path}")