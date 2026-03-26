import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PARA DESIGN "NEON LUMINARY" (ULTRA CLEAN & NON-FIXED) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&display=swap');

    /* Reset e Fundo Profundo */
    .stApp {
        background-color: #060800 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Esconde elementos padrão do Streamlit */
    header[data-testid="stHeader"], [data-testid="stSidebar"], .stDeployButton, footer { 
        display: none !important; 
    }

    /* Brand Header - AGORA NÃO É FIXO (Scrolla com a página) */
    .brand-header {
        width: 100%;
        padding: 40px 48px;
        display: flex;
        align-items: center;
        gap: 12px;
        background-color: transparent;
    }
    .brand-logo {
        color: #a4fd4c;
        font-family: 'Manrope', sans-serif;
        font-size: 24px;
        font-weight: 900;
        letter-spacing: -1.5px;
    }
    .brand-divider {
        color: rgba(164, 253, 76, 0.3);
        font-size: 24px;
        font-weight: 200;
    }
    .brand-tagline {
        color: #a4fd4c;
        font-size: 14px;
        font-weight: 600;
        margin-top: 4px;
    }

    /* Container Principal */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 48px 100px 48px;
    }

    /* Tipografia Hero */
    .hero-title {
        font-family: 'Manrope', sans-serif;
        font-size: 64px;
        font-weight: 800;
        color: white;
        line-height: 1.1;
        margin-bottom: 24px;
    }
    .hero-highlight {
        color: #a4fd4c;
        display: block;
    }
    .hero-subtitle {
        color: #a7b076; 
        font-size: 18px; 
        max-width: 600px; 
        margin-bottom: 60px;
        line-height: 1.6;
    }

    /* Seção de Seleção */
    .section-label {
        color: white;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 32px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .section-label::before {
        content: "";
        width: 40px;
        height: 2px;
        background-color: #a4fd4c;
    }

    /* Estilização do Selectbox (Searchbox) */
    div[data-baseweb="select"] {
        background-color: #111500 !important;
        border: 1px solid rgba(164, 253, 76, 0.1) !important;
        border-radius: 12px !important;
        padding: 12px !important;
        transition: all 0.3s ease;
    }
    div[data-baseweb="select"]:hover {
        border-color: rgba(164, 253, 76, 0.4) !important;
        background-color: #1a1f00 !important;
    }
    div[data-baseweb="select"] * {
        color: white !important;
        cursor: pointer !important;
    }
    div[data-testid="stSelectbox"] label {
        display: none !important;
    }

    /* Grid de Municípios (Botões de Card) */
    .stButton > button {
        width: 100% !important;
        background-color: #0e1200 !important;
        color: white !important;
        border: 1px solid rgba(164, 253, 76, 0.05) !important;
        padding: 32px 24px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-align: center !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
    }

    .stButton > button:hover {
        background-color: #1a1f00 !important;
        color: #a4fd4c !important;
        border-color: #a4fd4c !important;
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(164, 253, 76, 0.1) !important;
    }

    /* Informativo de Resultados */
    .results-header {
        display: flex;
        justify-content: space-between;
        width: 100%;
        color: #a7b076;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 64px;
        margin-bottom: 24px;
        border-bottom: 1px solid rgba(164, 253, 76, 0.1);
        padding-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER (NÃO FIXO) ---
st.markdown(
    '''
    <div class="brand-header">
        <span class="brand-logo">iG2P</span>
        <span class="brand-divider">|</span>
        <span class="brand-tagline">Gestão Inteligente</span>
    </div>
    ''',
    unsafe_allow_html=True
)

# --- 4. CONTEÚDO PRINCIPAL ---
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Hero Section
    st.markdown('''
        <h1 class="hero-title">Inteligência em <span class="hero-highlight">Gestão Pública.</span></h1>
        <p class="hero-subtitle">
            Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.
        </p>
    ''', unsafe_allow_html=True)

    # Seletor de Setor
    st.markdown('<div class="section-label">Selecione o Setor</div>', unsafe_allow_html=True)
    
    setor = st.selectbox(
        "Escolha o Setor",
        ["Saúde", "Educação"],
        index=None,
        placeholder="Clique para escolher entre Saúde ou Educação...",
    )

    if setor:
        st.markdown(f'''
            <div class="results-header">
                <span>Municípios do Setor: {setor}</span>
                <span style="opacity: 0.6;">RESULTADOS SUGERIDOS</span>
            </div>
        ''', unsafe_allow_html=True)

        # Configuração do Grid de Municípios
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

        # Renderização dos botões em Grid
        for i, (nome, path) in enumerate(municipios):
            with cols[i % 4]:
                if st.button(nome, key=f"btn_{nome}_{i}"):
                    if path:
                        st.switch_page(path)

    st.markdown('</div>', unsafe_allow_html=True)
