import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- 2. CSS PARA DESIGN "HERO" E GRID ---
st.markdown("""
    <style>
    /* Limpeza de interface */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    footer { visibility: hidden; }

    /* Fundo e Fonte */
    .stApp {
        background-color: #0d1101 !important; /* Verde quase preto da foto */
        color: #ffffff;
    }

    /* Cabeçalho Superior */
    .top-nav {
        display: flex;
        align-items: center;
        padding: 20px 40px;
        gap: 10px;
    }
    .top-nav b { color: #99ff33; font-size: 18px; }
    .top-nav span { color: #ffffff; opacity: 0.8; font-size: 18px; }

    /* Seção Hero */
    .hero-section {
        padding: 60px 40px 20px 40px;
        max-width: 900px;
    }
    .hero-title {
        font-size: 72px !important;
        font-weight: 800 !important;
        line-height: 1.1;
        margin-bottom: 20px;
    }
    .hero-title span { color: #99ff33; } /* Destaque verde */
    .hero-subtitle {
        font-size: 20px;
        color: #a0a0a0;
        margin-bottom: 40px;
    }

    /* Título das Seções */
    .section-label {
        color: #99ff33;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 14px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 40px 40px 20px 40px;
    }
    .section-label::before {
        content: "";
        display: inline-block;
        width: 40px;
        height: 2px;
        background-color: #99ff33;
    }

    /* Cards de Setor */
    .stButton > button {
        border-radius: 20px !important;
        border: 1px solid rgba(153, 255, 51, 0.1) !important;
        transition: all 0.3s ease !important;
        text-align: left !important;
    }

    /* Estilo específico para os Cards de Setor (Educação/Saúde) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton button,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton button {
        background: rgba(255, 255, 255, 0.03) !important;
        height: 280px !important;
        width: 100% !important;
        padding: 30px !important;
    }

    /* Estilo para os botões de Município (Grid inferior) */
    .municipio-grid .stButton button {
        background: rgba(255, 255, 255, 0.05) !important;
        height: 60px !important;
        font-weight: 500 !important;
    }
    
    .stButton button:hover {
        border-color: #99ff33 !important;
        background: rgba(153, 255, 51, 0.05) !important;
    }

    /* Ocultar labels padrão do Streamlit */
    label[data-testid="stWidgetLabel"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. TOP NAVIGATION ---
st.markdown("""
    <div class="top-nav">
        <b>iG2P</b> <span>| Gestão Inteligente</span>
    </div>
    """, unsafe_allow_html=True)

# --- 4. HERO SECTION ---
st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Inteligência em <span>Gestão Pública.</span></h1>
        <p class="hero-subtitle">Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-label">Selecione o Setor</div>', unsafe_allow_html=True)

# --- 5. CARDS DE SETOR (EDUCAÇÃO / SAÚDE) ---
col_edu, col_sau = st.columns(2)

with col_edu:
    st.markdown("""
        <div style="margin-bottom: -60px; margin-left: 30px; position: relative; z-index: 1;">
            <span style="background: #1a2a01; padding: 15px; border-radius: 12px; font-size: 24px;">🎓</span>
            <h3 style="margin-top: 20px; font-size: 32px;">Educação</h3>
            <p style="color: #808080; font-size: 14px;">Índices de alfabetização, infraestrutura escolar e performance acadêmica regional.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Selecionar Educação", key="btn_edu_main"):
        st.session_state.setor_selecionado = "Educação"

with col_sau:
    st.markdown("""
        <div style="margin-bottom: -60px; margin-left: 30px; position: relative; z-index: 1;">
            <span style="background: #1a2a01; padding: 15px; border-radius: 12px; font-size: 24px;">🛡️</span>
            <h3 style="margin-top: 20px; font-size: 32px;">Saúde</h3>
            <p style="color: #808080; font-size: 14px;">Leitos disponíveis, tempo de espera e cobertura vacinal em tempo real.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Selecionar Saúde", key="btn_sau_main"):
        st.session_state.setor_selecionado = "Saúde"

# --- 6. GRID DE MUNICÍPIOS ---
if "setor_selecionado" in st.session_state:
    setor = st.session_state.setor_selecionado
    st.markdown(f'<div class="section-label">Municípios do Setor: {setor}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="municipio-grid">', unsafe_allow_html=True)
    cols = st.columns(4) # Grid de 4 colunas como na foto
    
    if setor == "Saúde":
        municipios = [
            ("Alpinópolis", "Alpinópolis_Saúde.py"),
            ("Bom Jesus da Penha", "Bom_Jesus_da_Penha_Saúde.py"),
            ("Cássia", "Cássia_Saúde.py"),
            ("Delfinópolis", "Delfinópolis_Saúde.py"),
            ("Itaú de Minas", "Itaú_de_Minas_Saúde.py")
        ]
    else:
        municipios = [
            ("Alpinópolis", "Alpinópolis_Educação.py"),
            ("Município Educação B", None)
        ]

    for i, (nome, page) in enumerate(municipios):
        with cols[i % 4]:
            if st.button(nome, key=f"city_{nome}"):
                if page:
                    st.switch_page(f"pages/{page}")
    
    st.markdown('</div>', unsafe_allow_html=True)