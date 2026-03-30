import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PARA FIDELIDADE TOTAL AO DESIGN "ULTRA CLEAN" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&display=swap');

    /* Fundo e Reset */
    .stApp {
        background-color: #060800 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Remove elementos padrão do Streamlit */
    header[data-testid="stHeader"], [data-testid="stSidebar"], .stDeployButton, footer { 
        display: none !important; 
    }

    /* Brand Header */
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

    /* Hero Section */
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
    }
    .hero-subtitle {
        color: #a7b076; 
        font-size: 18px; 
        max-width: 700px; 
        margin-bottom: 64px;
        line-height: 1.6;
    }

    /* Seção Label */
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

    /* --- CARDS DE SETOR (Educação / Saúde) --- */
    div.stButton > button[key^="sector_"] {
        height: 320px !important;
        background-color: rgba(164, 253, 76, 0.02) !important;
        border: 1px solid rgba(164, 253, 76, 0.1) !important;
        border-radius: 32px !important;
        color: white !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        padding: 48px !important;
        text-align: left !important;
        overflow: hidden !important;
    }

    /* Ícones dentro dos botões */
    div.stButton > button[key^="sector_"]::before {
        font-size: 28px;
        background: rgba(164, 253, 76, 0.1);
        padding: 16px;
        border-radius: 16px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    button[key="sector_edu"]::before { content: "🎓"; }
    button[key="sector_sau"]::before { content: "🏥"; }

    /* Hover nos Cards */
    div.stButton > button[key^="sector_"]:hover {
        border-color: #a4fd4c !important;
        background-color: rgba(164, 253, 76, 0.08) !important;
        transform: translateY(-12px) !important;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4) !important;
    }

    /* Estilo Selecionado */
    div.stButton > button[key^="sector_"].selected {
        border-color: #a4fd4c !important;
        background-color: rgba(164, 253, 76, 0.1) !important;
    }

    /* --- CARDS DE MUNICÍPIO --- */
    div.stButton > button[key^="mun_"] {
        width: 100% !important;
        background-color: #0c1000 !important;
        color: #a7b076 !important;
        border: 1px solid rgba(164, 253, 76, 0.05) !important;
        padding: 24px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        height: auto !important;
    }
    
    div.stButton > button[key^="mun_"]:hover {
        color: #a4fd4c !important;
        border-color: #a4fd4c !important;
        background-color: #1a1f00 !important;
        transform: scale(1.03);
    }

    .results-header {
        color: #a7b076;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 80px;
        margin-bottom: 32px;
        border-bottom: 1px solid rgba(164, 253, 76, 0.1);
        padding-bottom: 20px;
        display: flex;
        justify-content: space-between;
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
        <h1 class="hero-title">Inteligência em <br><span class="hero-highlight">Gestão Pública.</span></h1>
        <p class="hero-subtitle">
            Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.
        </p>
    ''', unsafe_allow_html=True)

    # Grid de Setores
    st.markdown('<div class="section-label">Selecione o Setor</div>', unsafe_allow_html=True)
    col_edu, col_sau = st.columns(2)
    
    if 'setor_selecionado' not in st.session_state:
        st.session_state.setor_selecionado = None

    with col_edu:
        btn_label_edu = "Educação"
        if st.button(btn_label_edu, key="sector_edu", use_container_width=True):
            st.session_state.setor_selecionado = "Educação"
            
    with col_sau:
        btn_label_sau = "Saúde"
        if st.button(btn_label_sau, key="sector_sau", use_container_width=True):
            st.session_state.setor_selecionado = "Saúde"

    # Lista de Municípios
    if st.session_state.setor_selecionado:
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
                ("Município Educação B", None),
                ("Município Educação C", None),
                ("Município Educação D", None)
            ]

        for i, (nome, path) in enumerate(municipios):
            with cols[i % 4]:
                if st.button(nome, key=f"mun_{nome}_{i}", use_container_width=True):
                    if path:
                        st.switch_page(path)

    st.markdown('</div>', unsafe_allow_html=True)
