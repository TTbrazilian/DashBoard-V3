import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# --- 2. CSS PARA DESIGN "NEON LUMINARY" (STITCH STYLE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&display=swap');

    /* Reset e Fundo Profundo */
    .stApp {
        background-color: #060800 !important;
        font-family: 'Inter', sans-serif;
    }

    header[data-testid="stHeader"], [data-testid="stSidebar"], .stDeployButton, footer { 
        display: none !important; 
    }

    /* Brand Logo iG2P */
    .brand-header {
        position: fixed;
        top: 40px;
        left: 48px;
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-logo {
        color: #a4fd4c;
        font-family: 'Manrope', sans-serif;
        font-size: 32px;
        font-weight: 900;
        letter-spacing: -2px;
        text-decoration: none;
    }
    .brand-tagline {
        color: #a4fd4c;
        font-size: 14px;
        font-weight: 600;
        border-left: 1px solid rgba(164, 253, 76, 0.3);
        padding-left: 12px;
        margin-top: 4px;
    }

    /* Container Principal */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding-top: 120px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }

    /* Tipografia de Títulos */
    .hero-title {
        font-family: 'Manrope', sans-serif;
        font-size: 72px;
        font-weight: 800;
        color: white;
        line-height: 1.1;
        margin-bottom: 24px;
    }
    .hero-highlight {
        color: #a4fd4c;
        display: block;
    }
    .section-label {
        color: #a7b076;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 14px;
        font-weight: 700;
        margin-top: 60px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .section-label::before {
        content: "";
        width: 40px;
        height: 2px;
        background-color: #a4fd4c;
    }

    /* Estilização do Selectbox (Setor) */
    div[data-baseweb="select"] {
        background-color: #1a1f00 !important;
        border: 1px solid rgba(164, 253, 76, 0.2) !important;
        border-radius: 12px !important;
        padding: 8px !important;
    }
    div[data-baseweb="select"] * {
        color: white !important;
        cursor: pointer !important;
    }
    div[data-testid="stSelectbox"] label {
        display: none !important;
    }

    /* Grid de Municípios (Botões) */
    .stButton > button {
        width: 100% !important;
        background-color: #131800 !important;
        color: #a7b076 !important;
        border: 1px solid rgba(164, 253, 76, 0.1) !important;
        padding: 24px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        text-align: left !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
    }

    .stButton > button:hover {
        background-color: #222900 !important;
        color: #a4fd4c !important;
        border-color: #a4fd4c !important;
        transform: translateY(-2px);
    }

    /* Grid Layout para os botões */
    [data-testid="stHorizontalBlock"] {
        gap: 16px !important;
    }
    
    /* Informativo de Municípios do Setor */
    .results-label {
        display: flex;
        justify-content: space-between;
        width: 100%;
        color: #a7b076;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 48px;
        margin-bottom: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER / LOGO ---
st.markdown(
    f'''
    <div class="brand-header">
        <div class="brand-logo">iG2P</div>
        <div class="brand-tagline">Gestão Inteligente</div>
    </div>
    ''',
    unsafe_allow_html=True
)

# --- 4. CONTEÚDO ---
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('''
        <h1 class="hero-title">Inteligência em <span class="hero-highlight">Gestão Pública.</span></h1>
        <p style="color: #a7b076; font-size: 18px; max-width: 600px; margin-bottom: 40px;">
            Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.
        </p>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Selecione o Setor</div>', unsafe_allow_html=True)
    
    # Selectbox de Setor com design limpo
    setor = st.selectbox(
        "Selecione o Setor",
        ["Saúde", "Educação"],
        index=None,
        placeholder="Escolha entre Saúde ou Educação...",
    )

    if setor:
        st.markdown(f'''
            <div class="results-label">
                <span>Municípios do Setor: {setor}</span>
                <span style="opacity: 0.6;">RESULTADOS SUGERIDOS</span>
            </div>
        ''', unsafe_allow_html=True)

        # Lógica de botões em Grid (4 colunas)
        cols = st.columns(4)
        
        if setor == "Saúde":
            municipios = [
                ("Alpinópolis", "pages/Alpinópolis_Saúde.py"),
                ("Bom Jesus da Penha", "pages/Bom_Jesus_da_Penha_Saúde.py"),
                ("Cássia", "pages/Cássia_Saúde.py"),
                ("Delfinópolis", "pages/Delfinópolis_Saúde.py"),
                ("Itaú de Minas", "pages/Itaú_de_Minas_Saúde.py")
            ]
        else: # Educação
            municipios = [
                ("Alpinópolis", "pages/Alpinópolis_Educação.py"),
                ("Município Educação B", None)
            ]

        for i, (nome, path) in enumerate(municipios):
            with cols[i % 4]:
                if st.button(nome, key=f"btn_{nome}"):
                    if path:
                        st.switch_page(path)

    st.markdown('</div>', unsafe_allow_html=True)
