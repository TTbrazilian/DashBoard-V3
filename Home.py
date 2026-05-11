import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. FUNÇÃO PARA CARREGAR IMAGEM SEM PERDA ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

LOGO_PATH = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.png"
logo_base64 = get_image_base64(LOGO_PATH)

# --- 3. CSS PARA IDENTIDADE VISUAL ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');

    /* Remover Sidebar e UI nativa */
    [data-testid="stSidebar"],
    header[data-testid="stHeader"],
    .stDeployButton,
    footer {{
        display: none !important;
    }}

    /* Fundo escuro sólido */
    .stApp {{
        background-color: #0E1117 !important;
    }}

    /* Container da Página */
    .block-container {{
        padding-top: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }}

    /* ── LOGO ── */
    .brand-box {{
        position: absolute;
        top: 20px;
        left: 20px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        z-index: 1000;
    }}
    .brand-box img {{
        width: 160px;
        height: auto;
        image-rendering: -webkit-optimize-contrast;
    }}
    .brand-box p {{
        color: white;
        font-family: 'Outfit', sans-serif;
        font-size: 14px;
        margin: -5px 0 0 5px !important;
        padding: 0 !important;
        white-space: nowrap;
    }}

    /* ── CARDS DE SETOR ── */
    .sector-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 28px;
        padding: 0 20px;
    }}

    .sector-card {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 200px;
        height: 180px;
        background: #181C26;
        border: 1px solid #2A2F3E;
        border-radius: 18px;
        cursor: pointer;
        transition: all 0.25s ease;
        text-decoration: none;
        position: relative;
        overflow: hidden;
    }}

    .sector-card::before {{
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, transparent 60%);
        pointer-events: none;
    }}

    .sector-card:hover {{
        border-color: #4A6CF7;
        background: #1E2335;
        transform: translateY(-4px);
        box-shadow: 0 12px 36px rgba(74, 108, 247, 0.18);
    }}

    .sector-card.active {{
        border-color: #4A6CF7;
        background: linear-gradient(145deg, #1E2D5E 0%, #1A2140 100%);
        box-shadow: 0 0 0 2px rgba(74,108,247,0.35), 0 12px 36px rgba(74,108,247,0.22);
    }}

    .sector-icon-bg {{
        width: 64px;
        height: 64px;
        border-radius: 16px;
        background: #252C40;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;
        transition: background 0.25s ease;
    }}

    .sector-card:hover .sector-icon-bg,
    .sector-card.active .sector-icon-bg {{
        background: rgba(74,108,247,0.18);
    }}

    .sector-icon-bg svg {{
        width: 30px;
        height: 30px;
        stroke: #8FA8FF;
    }}

    .sector-label {{
        color: #C8D0E8;
        font-family: 'Outfit', sans-serif;
        font-size: 15px;
        font-weight: 500;
        letter-spacing: 0.3px;
        margin: 0;
    }}

    /* ── TÍTULO DE MUNICÍPIOS ── */
    .municipio-header {{
        color: #C8D0E8;
        font-size: 17px;
        text-align: center;
        width: 100%;
        font-family: 'Outfit', sans-serif;
        font-weight: 400;
        letter-spacing: 0.5px;
        margin-top: 0;
        padding: 0;
    }}

    .municipio-header span {{
        color: #8FA8FF;
        font-weight: 600;
    }}

    /* ── BOTÕES DE MUNICÍPIO ── */
    div[data-testid="stButton"] > button {{
        background: #181C26 !important;
        border: 1px solid #2A2F3E !important;
        border-radius: 10px !important;
        color: #C8D0E8 !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        padding: 10px 8px !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }}
    div[data-testid="stButton"] > button:hover {{
        background: #1E2335 !important;
        border-color: #4A6CF7 !important;
        color: #fff !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74,108,247,0.15) !important;
    }}

    /* Ocultar botões invisíveis de controle de estado */
    .hidden-btn > div[data-testid="stButton"] > button {{
        display: none !important;
    }}

    /* Divisor sutil */
    .divider {{
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #4A6CF7, transparent);
        margin: 0 auto 28px auto;
        border-radius: 2px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. RENDERIZAÇÃO DO LOGO E SUBTÍTULO ---
if logo_base64:
    st.markdown(f"""
        <div class="brand-box">
            <img src="data:image/png;base64,{logo_base64}">
            <p>Inteligência em Gestão</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="brand-box">
            <h2 style="color:white; margin:0;">iG2P</h2>
            <p>Inteligência em Gestão</p>
        </div>
    """, unsafe_allow_html=True)

# ── ÍCONES SVG ────────────────────────────────────────────────────────────────
ICON_EDUCACAO = """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"
     stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
  <path d="M22 10v6M2 10l10-5 10 5-10 5-10-5z"/>
  <path d="M6 12v5c0 1.657 2.686 3 6 3s6-1.343 6-3v-5"/>
</svg>
"""
ICON_SAUDE = """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"
     stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="7" width="18" height="14" rx="2"/>
  <path d="M8 7V5a4 4 0 018 0v2"/>
  <path d="M12 11v6M9 14h6"/>
</svg>
"""

# ── ESTADO DE SESSÃO ──────────────────────────────────────────────────────────
if 'setor_ativo' not in st.session_state:
    st.session_state['setor_ativo'] = None

setor_escolhido = st.session_state.get('setor_ativo')

# ── ESPAÇAMENTO VERTICAL ANTES DOS CARDS ──────────────────────────────────────
st.markdown("<div style='height: 140px'></div>", unsafe_allow_html=True)

# ── CARDS DE SETOR ────────────────────────────────────────────────────────────
# Título sutil acima dos cards
st.markdown("""
    <p style="
        text-align:center;
        color:#5C6480;
        font-family:'Outfit',sans-serif;
        font-size:13px;
        letter-spacing:1.8px;
        text-transform:uppercase;
        margin-bottom:20px;
    ">Selecione o Setor</p>
""", unsafe_allow_html=True)

# Renderiza os dois cards como HTML visual
active_edu = 'active' if setor_escolhido == 'Educação' else ''
active_sau = 'active' if setor_escolhido == 'Saúde' else ''

st.markdown(f"""
<div class="sector-wrapper">
    <div class="sector-card {active_edu}" id="card-edu" style="pointer-events:none;">
        <div class="sector-icon-bg">{ICON_EDUCACAO}</div>
        <p class="sector-label">Educação</p>
    </div>
    <div class="sector-card {active_sau}" id="card-sau" style="pointer-events:none;">
        <div class="sector-icon-bg">{ICON_SAUDE}</div>
        <p class="sector-label">Saúde</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Botões Streamlit invisíveis posicionados sobre os cards (via colunas)
st.markdown("<div style='margin-top:-175px;'>", unsafe_allow_html=True)

_, col_edu, col_gap, col_sau, _ = st.columns([2.35, 1, 0.15, 1, 2.35])

with col_edu:
    if st.button("‎", key="btn_educacao", use_container_width=True,
                 help="Educação",
                 type="secondary"):
        st.session_state['setor_ativo'] = 'Educação'
        st.rerun()

with col_sau:
    if st.button("‎ ", key="btn_saude", use_container_width=True,
                 help="Saúde",
                 type="secondary"):
        st.session_state['setor_ativo'] = 'Saúde'
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Ajuste de estilo para os botões invisíveis de controle
st.markdown("""
<style>
    /* Botões de controle: transparentes, mesma área dos cards */
    div[data-testid="stButton"]:has(button[kind="secondary"]) > button {{
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        height: 175px !important;
        font-size: 1px !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }}
    div[data-testid="stButton"]:has(button[kind="secondary"]) > button:hover {{
        background: transparent !important;
        border: none !important;
        transform: none !important;
        box-shadow: none !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── GRADE DE MUNICÍPIOS ───────────────────────────────────────────────────────
if setor_escolhido:
    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.markdown(
        f'<p class="municipio-header">Municípios · <span>{setor_escolhido}</span></p>',
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if setor_escolhido == "Educação":
        nomes = [
            "Alpinópolis", "Cássia", "Capetinga", "Claraval", "Delfinópolis",
            "Ibiraci", "Itaú de Minas", "Pratápolis", "Restinga",
            "São João Batista Do Glória", "São José da Barra",
            "São Roque de Minas", "São Tomás de Aquino", "Itamogi"
        ]
        suffix = "Educação"
    else:
        nomes = ["Alpinópolis", "Bom Jesus da Penha", "Cássia", "Delfinópolis", "Itaú de Minas"]
        suffix = "Saúde"

    _, col_buttons, _ = st.columns([0.1, 0.8, 0.1])

    with col_buttons:
        cols = st.columns(5)
        for i, nome in enumerate(nomes):
            with cols[i % 5]:
                file_name = nome.replace(' ', '_')
                path = f"pages/{file_name}_{suffix}.py"

                if st.button(nome, key=f"btn_{nome}_{i}", use_container_width=True):
                    st.session_state['setor_ativo'] = setor_escolhido
                    try:
                        st.switch_page(path)
                    except Exception as e:
                        st.error(f"Página não encontrada: {path}")