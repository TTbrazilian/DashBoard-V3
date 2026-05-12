import streamlit as st
import os
import base64

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

# ── 4. SVG ICONS como data-URI (para uso em CSS background-image) ────────────
SVG_EDU = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' "
    "fill='none' stroke='%238FA8FF' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'%3E"
    "%3Cpath d='M22 10v6M2 10l10-5 10 5-10 5-10-5z'/%3E"
    "%3Cpath d='M6 12v5c0 1.657 2.686 3 6 3s6-1.343 6-3v-5'/%3E"
    "%3C/svg%3E"
)

SVG_SAU = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' "
    "fill='none' stroke='%238FA8FF' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'%3E"
    "%3Crect x='3' y='7' width='18' height='14' rx='2'/%3E"
    "%3Cpath d='M8 7V5a4 4 0 018 0v2'/%3E"
    "%3Cpath d='M12 11v6M9 14h6'/%3E"
    "%3C/svg%3E"
)

# ── 5. CSS SELETORES ─────────────────────────────────────────────────────────
# O primeiro stHorizontalBlock da página é o seletor de setor.
# Layout: [espaço col1 | Educação col2 | gap col3 | Saúde col4 | espaço col5]
BLOCK   = "div[data-testid='stHorizontalBlock']:first-of-type"
EDU_BTN = f"{BLOCK} > div:nth-child(2) button"
SAU_BTN = f"{BLOCK} > div:nth-child(4) button"

# CSS do estado ativo é injetado dinamicamente conforme o setor selecionado
active_edu_css = f"""
  {EDU_BTN} {{
    border: 1.5px solid #5B7BFF !important;
    background: linear-gradient(145deg, #192150 0%, #141A3A 100%) !important;
    box-shadow: 0 0 0 3px rgba(91,123,255,0.18),
                0 16px 40px rgba(91,123,255,0.20) !important;
  }}
  {EDU_BTN}::after {{
    background-color: #1E2D6A !important;
    filter: brightness(1.25);
  }}
""" if setor_escolhido == "Educação" else ""

active_sau_css = f"""
  {SAU_BTN} {{
    border: 1.5px solid #5B7BFF !important;
    background: linear-gradient(145deg, #192150 0%, #141A3A 100%) !important;
    box-shadow: 0 0 0 3px rgba(91,123,255,0.18),
                0 16px 40px rgba(91,123,255,0.20) !important;
  }}
  {SAU_BTN}::after {{
    background-color: #1E2D6A !important;
    filter: brightness(1.25);
  }}
""" if setor_escolhido == "Saúde" else ""

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');

  /* ── RESET STREAMLIT ── */
  [data-testid="stSidebar"],
  header[data-testid="stHeader"],
  .stDeployButton, footer {{ display: none !important; }}

  .stApp {{ background-color: #0D1017 !important; }}

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
    color: rgba(255,255,255,0.50);
    font-family: 'Outfit', sans-serif;
    font-size: 13px; margin: -3px 0 0 4px; white-space: nowrap;
  }}

  /* ── LABEL ACIMA DOS CARDS ── */
  .sector-label {{
    text-align: center;
    color: #404868;
    font-family: 'Outfit', sans-serif;
    font-size: 11.5px;
    letter-spacing: 2.4px;
    text-transform: uppercase;
    margin: 0 0 20px 0;
  }}

  /* ════════════════════════════════════════════
     CARD-BUTTONS  –  os próprios st.button
     estilizados como cards com ícone + label
  ════════════════════════════════════════════ */
  {EDU_BTN},
  {SAU_BTN} {{
    /* Dimensões do card */
    width:  100% !important;
    height: 210px !important;
    padding: 0 !important;

    /* Visual base */
    background: #111726 !important;
    border: 1.5px solid #1C2338 !important;
    border-radius: 22px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.40) !important;

    /* Flex: ícone em cima, texto em baixo */
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;

    /* Texto */
    color: #B8C4E0 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px !important;
    line-height: 1 !important;

    cursor: pointer !important;
    transition:
      border-color .22s ease,
      background   .22s ease,
      box-shadow   .22s ease,
      transform    .18s ease !important;
  }}

  /* Ícone como pseudo-elemento ::after (renderizado antes do texto via order) */
  {EDU_BTN}::after,
  {SAU_BTN}::after {{
    content: '' !important;
    display: block !important;
    order: -1 !important;            /* sobe acima do texto */
    width:  62px !important;
    height: 62px !important;
    border-radius: 15px !important;
    background-color: #192038 !important;
    background-size: 55% !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    margin-bottom: 20px !important;
    transition: background-color .22s ease !important;
  }}

  /* Ícone específico de cada card */
  {EDU_BTN}::after {{ background-image: url("{SVG_EDU}") !important; }}
  {SAU_BTN}::after {{ background-image: url("{SVG_SAU}") !important; }}

  /* Hover (somente para o card não ativo) */
  {EDU_BTN}:hover,
  {SAU_BTN}:hover {{
    border-color: #3A4E8C !important;
    background: #151C30 !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 36px rgba(60,80,180,0.18) !important;
  }}
  {EDU_BTN}:hover::after,
  {SAU_BTN}:hover::after {{
    background-color: #1E2A4A !important;
  }}

  /* ── ACTIVE STATE (injetado dinamicamente) ── */
  {active_edu_css}
  {active_sau_css}

  /* ── DIVISOR ── */
  .divider {{
    width: 48px; height: 2px;
    background: linear-gradient(90deg, transparent, #4A6CF7, transparent);
    margin: 0 auto 24px;
    border-radius: 2px;
  }}

  /* ── HEADER MUNICÍPIOS ── */
  .muni-header {{
    text-align: center;
    color: #7A87A8;
    font-family: 'Outfit', sans-serif;
    font-size: 14px;
    font-weight: 400;
    letter-spacing: 0.4px;
    margin: 0;
  }}
  .muni-header strong {{ color: #95AAFF; font-weight: 600; }}

  /* ── BOTÕES DE MUNICÍPIO ── */
  div[data-testid="stHorizontalBlock"]:not(:first-of-type)
    div[data-testid="stButton"] > button {{
    background: #111726 !important;
    border: 1px solid #1C2338 !important;
    border-radius: 10px !important;
    color: #9AAAC4 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 10px 6px !important;
    transition: all .18s ease !important;
    box-shadow: none !important;
  }}
  div[data-testid="stHorizontalBlock"]:not(:first-of-type)
    div[data-testid="stButton"] > button:hover {{
    background: #192150 !important;
    border-color: #5B7BFF !important;
    color: #fff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(91,123,255,0.15) !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── 6. LOGO ──────────────────────────────────────────────────────────────────
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

# ── 7. ESPAÇAMENTO ANTES DOS CARDS ───────────────────────────────────────────
st.markdown("<div style='height:130px'></div>", unsafe_allow_html=True)

# ── 8. LABEL + CARD-BUTTONS ──────────────────────────────────────────────────
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

# ── 9. GRADE DE MUNICÍPIOS ────────────────────────────────────────────────────
if setor_escolhido:
    st.markdown("<div style='height:34px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<p class="muni-header">Municípios &nbsp;·&nbsp; <strong>{setor_escolhido}</strong></p>',
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

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

    _, col_grid, _ = st.columns([0.1, 0.8, 0.1])
    with col_grid:
        cols = st.columns(5)
        for i, nome in enumerate(nomes):
            with cols[i % 5]:
                file_name = nome.replace(" ", "_")
                path = f"pages/{file_name}_{suffix}.py"
                if st.button(nome, key=f"muni_{nome}_{i}", use_container_width=True):
                    st.session_state["setor_ativo"] = setor_escolhido
                    try:
                        st.switch_page(path)
                    except Exception as e:
                        st.error(f"Página não encontrada: {path}")