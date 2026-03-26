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

    /* Brand Header - Não fixo */
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

    /* Estilização dos Botões de Setor (Cards Grandes) */
    .sector-card-container {
        margin-bottom: 48px;
    }
    
    /* Custom CSS para os botões de setor do Streamlit agirem como cards */
    div.stButton > button[key^="sector_"] {
        height: 240px !important;
        background-color: #0e1200 !important;
        border: 1px solid rgba(164, 253, 76, 0.1) !important;
        border-radius: 20px !important;
        color: white !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 16px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    div.stButton > button[key^="sector_"]:hover {
        border-color: #a4fd4c !important;
        background-color: #1a1f00 !important;
        transform: translateY(-8px) !important;
        box-shadow: 0 20px 40px rgba(164, 253, 76, 0.1) !important;
    }

    /* Municípios Grid */
    div.stButton > button[key^="mun_"] {
        width: 100% !important;
        background-color: #0c1000 !important;
        color: #a7b076 !important;
        border: 1px solid rgba(164, 253, 76, 0.05) !important;
        padding: 24px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    div.stButton > button[key^="mun_"]:hover {
        color: #a4fd4c !important;
        border-color: #a4fd4c !important;
        background-color: #1a1f00 !important;
    }

    .results-header {
        color: #a7b076;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 24px;
        margin-bottom: 24px;
        border-bottom: 1px solid rgba(164, 253, 76, 0.1);
        padding-bottom: 12px;
        display: flex;
        justify-content: space-between;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
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

# --- 4. CONTEÚDO ---
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Hero Section
    st.markdown('''
        <h1 class="hero-title">Inteligência em <span class="hero-highlight">Gestão Pública.</span></h1>
        <p class="hero-subtitle">
            Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.
        </p>
    ''', unsafe_allow_html=True)

    # Seleção de Setor
    st.markdown('<div class="section-label">Selecione o Setor</div>', unsafe_allow_html=True)
    
    # Grid de Setores (Botões Grandes)
    col_edu, col_sau = st.columns(2)
    
    with col_edu:
        if st.button("Educação", key="sector_edu", use_container_width=True):
            st.session_state.setor_selecionado = "Educação"
            
    with col_sau:
        if st.button("Saúde", key="sector_sau", use_container_width=True):
            st.session_state.setor_selecionado = "Saúde"

    # Exibição dos Municípios com base no setor
    if 'setor_selecionado' in st.session_state:
        setor = st.session_state.setor_selecionado
        
        st.markdown(f'''
            <div class="results-header">
                <span>Municípios do Setor: {setor}</span>
                <span style="opacity: 0.6;">RESULTADOS SUGERIDOS</span>
            </div>
        ''', unsafe_allow_html=True)

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
                if st.button(nome, key=f"mun_{nome}_{i}", use_container_width=True):
                    if path:
                        st.switch_page(path)

    st.markdown('</div>', unsafe_allow_html=True)
