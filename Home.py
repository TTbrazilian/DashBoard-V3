import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA (Lógica Preservada) ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PARA DESIGN "FIEL À PRINT" (NEON, GRIDS E CARDS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&display=swap');

    /* Fundo e Reset */
    .stApp {
        background-color: #060800 !important;
        font-family: 'Inter', sans-serif;
        color: #ffffff;
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
    .brand-logo { color: #a4fd4c; font-family: 'Manrope', sans-serif; font-size: 24px; font-weight: 900; }
    .brand-tagline { color: #a4fd4c; font-size: 14px; font-weight: 600; }

    /* Container Principal */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 48px 100px 48px;
    }

    /* Hero Section */
    .hero-title {
        font-family: 'Manrope', sans-serif;
        font-size: 64px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 24px;
    }
    .hero-highlight { color: #a4fd4c; }
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

    /* --- CARDS DE SETOR COMO BOTÃO INTEGRAL --- */
    /* Faz o container do botão ter posição relativa para ancorar o design */
    div:has(> button[key^="sector_"]) {
        position: relative;
        height: 280px;
        width: 100%;
    }

    /* O botão do streamlit fica invisível e cobre 100% da área do card */
    div:has(> button[key^="sector_"]) button {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        z-index: 10 !important;
        cursor: pointer !important;
    }

    /* O container visual (Card) desenhado por baixo do botão */
    .sector-card {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(164, 253, 76, 0.1);
        border-radius: 24px;
        padding: 40px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        transition: all 0.4s ease;
        overflow: hidden;
    }

    /* Efeito de Hover no Card Visual */
    div:has(> button[key^="sector_"]):hover .sector-card {
        border-color: #a4fd4c !important;
        background-color: rgba(164, 253, 76, 0.05) !important;
        transform: translateY(-8px) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
    }

    .card-icon {
        width: 56px; height: 56px;
        background: rgba(164, 253, 76, 0.1);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px; margin-bottom: 40px;
    }

    .card-title { font-family: 'Manrope', sans-serif; font-size: 32px; font-weight: 700; margin-bottom: 10px; }
    .card-subtitle { color: #a7b076; font-size: 14px; line-height: 1.5; max-width: 85%; }

    /* ÍCONES OPACOS DE FUNDO */
    .card-bg-icon {
        position: absolute;
        right: -20px;
        bottom: -30px;
        font-size: 180px;
        color: #a4fd4c;
        opacity: 0.03;
        pointer-events: none;
        font-family: serif;
    }

    /* --- CARDS DE MUNICÍPIO (DESIGN NEON) --- */
    div.stButton > button[key^="mun_"] {
        width: 100% !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: #a7b076 !important;
        border: 1px solid rgba(164, 253, 76, 0.08) !important;
        padding: 18px 20px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        text-align: left !important;
        transition: all 0.3s ease !important;
    }
    
    div.stButton > button[key^="mun_"]:hover {
        color: #a4fd4c !important;
        border-color: #a4fd4c !important;
        background-color: rgba(164, 253, 76, 0.05) !important;
    }

    .results-header {
        color: #a7b076; font-size: 12px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1px;
        margin-top: 64px; margin-bottom: 24px;
        border-bottom: 1px solid rgba(164, 253, 76, 0.1);
        padding-bottom: 16px; display: flex; justify-content: space-between;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER (CONSERVADO) ---
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

# --- 4. CONTEÚDO PRINCIPAL (LÓGICA TOTALMENTE PRESERVADA) ---
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Hero Section
    st.markdown('''
        <h1 class="hero-title">Inteligência em <span class="hero-highlight">Gestão Pública.</span></h1>
        <p class="hero-subtitle">
            Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.
        </p>
    ''', unsafe_allow_html=True)

    # Grid de Setores
    st.markdown('<div class="section-label">Selecione o Setor</div>', unsafe_allow_html=True)
    col_edu, col_sau = st.columns(2)
    
    if 'setor_selecionado' not in st.session_state:
        st.session_state.setor_selecionado = None

    # --- SETOR EDUCAÇÃO (DESIGN FIEL + LÓGICA ORIGINAL) ---
    with col_edu:
        st.markdown('''
            <div class="sector-card">
                <div class="card-icon">🎓</div>
                <div class="card-title">Educação</div>
                <div class="card-subtitle">Índices de alfabetização, infraestrutura escolar e performance acadêmica regional.</div>
                <div class="card-bg-icon">🎓</div>
            </div>
            ''', unsafe_allow_html=True)
        # Botão invisível que executa sua lógica
        if st.button("Selecionar Educação", key="sector_edu", use_container_width=True):
            st.session_state.setor_selecionado = "Educação"
            
    # --- SETOR SAÚDE (CRUZ HOSPITALAR + LÓGICA ORIGINAL) ---
    with col_sau:
        st.markdown('''
            <div class="sector-card">
                <div class="card-icon">🏥</div>
                <div class="card-title">Saúde</div>
                <div class="card-subtitle">Leitos disponíveis, tempo de espera e cobertura vacinal em tempo real.</div>
                <div class="card-bg-icon">✚</div>
            </div>
            ''', unsafe_allow_html=True)
        # Botão invisível que executa sua lógica
        if st.button("Selecionar Saúde", key="sector_sau", use_container_width=True):
            st.session_state.setor_selecionado = "Saúde"

    # --- LISTA DE MUNICÍPIOS (LÓGICA ORIGINAL COMPLETA) ---
    if st.session_state.setor_selecionado:
        setor = st.session_state.setor_selecionado
        
        st.markdown(f'''
            <div class="results-header">
                <span>Municípios do Setor: {setor}</span>
                <span style="opacity: 0.6;">RESULTADOS SUGERIDOS</span>
            </div>
        ''', unsafe_allow_html=True)

        cols = st.columns(4) 
        
        # Sua lógica de dados 100% original:
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

        # Sua lógica de navegação original:
        for i, (nome, path) in enumerate(municipios):
            with cols[i % 4]:
                if st.button(nome, key=f"mun_{nome}_{i}", use_container_width=True):
                    if path:
                        st.switch_page(path)

    st.markdown('</div>', unsafe_allow_html=True)