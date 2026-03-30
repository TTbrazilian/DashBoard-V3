import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA (CONSERVADO) ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PARA DESIGN "NEON LUMINARY" (AJUSTADO PARA FIDELIDADE TOTAL) ---
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
        font-size: 64px;
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
        height: 300px !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(164, 253, 76, 0.1) !important;
        border-radius: 24px !important;
        color: white !important;
        padding: 40px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        text-align: left !important;
        transition: all 0.4s ease !important;
    }

    /* Hack para o Streamlit aceitar \n e formatar o texto do card */
    div.stButton > button[key^="sector_"] p {
        font-family: 'Manrope', sans-serif !important;
        font-weight: 700 !important;
        font-size: 28px !important;
        margin: 0 !important;
        line-height: 1.3 !important;
        white-space: pre-wrap !important; /* Essencial para as quebras de linha */
    }

    /* Ícones Quadrados Flutuantes conforme a imagem */
    button[key="sector_edu"]::before {
        content: "🎓";
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        width: 56px;
        height: 56px;
        background: rgba(164, 253, 76, 0.1);
        border-radius: 12px;
        margin-bottom: 40px;
    }
    button[key="sector_sau"]::before {
        content: "🛡️";
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        width: 56px;
        height: 56px;
        background: rgba(164, 253, 76, 0.1);
        border-radius: 12px;
        margin-bottom: 40px;
    }

    div.stButton > button[key^="sector_"]:hover {
        border-color: #a4fd4c !important;
        background-color: rgba(164, 253, 76, 0.05) !important;
        transform: translateY(-8px) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
    }

    /* --- CARDS DE MUNICÍPIO (CONSERVADO E AJUSTADO) --- */
    div.stButton > button[key^="mun_"] {
        width: 100% !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: #a7b076 !important;
        border: 1px solid rgba(164, 253, 76, 0.08) !important;
        padding: 18px 20px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        text-align: left !important;
    }
    
    div.stButton > button[key^="mun_"]:hover {
        color: #a4fd4c !important;
        border-color: #a4fd4c !important;
        background-color: rgba(164, 253, 76, 0.05) !important;
    }

    .results-header {
        color: #a7b076;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 64px;
        margin-bottom: 24px;
        border-bottom: 1px solid rgba(164, 253, 76, 0.1);
        padding-bottom: 16px;
        display: flex;
        justify-content: space-between;
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

# --- 4. CONTEÚDO PRINCIPAL (LÓGICA CONSERVADA) ---
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Hero Section - Textos conforme imagem de referência
    st.markdown('''
        <h1 class="hero-title">Inteligência em <span class="hero-highlight">Gestão Pública.</span></h1>
        <p class="hero-subtitle">
            Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.
        </p>
    ''', unsafe_allow_html=True)

    # Grid de Setores
    st.markdown('<div class="section-label">Selecione o Setor</div>', unsafe_allow_html=True)
    col_edu, col_sau = st.columns(2)
    
    # Lógica de persistência de estado (CONSERVADA)
    if 'setor_selecionado' not in st.session_state:
        st.session_state.setor_selecionado = None

    with col_edu:
        # Texto formatado para o card
        if st.button("Educação\n\nÍndices de alfabetização, infraestrutura escolar e performance acadêmica regional.", key="sector_edu", use_container_width=True):
            st.session_state.setor_selecionado = "Educação"
            
    with col_sau:
        # Texto formatado para o card
        if st.button("Saúde\n\nLeitos disponíveis, tempo de espera e cobertura vacinal em tempo real.", key="sector_sau", use_container_width=True):
            st.session_state.setor_selecionado = "Saúde"

    # Lista de Municípios (Toda a lógica de dados e navegação original conservada)
    if st.session_state.setor_selecionado:
        setor = st.session_state.setor_selecionado
        
        st.markdown(f'''
            <div class="results-header">
                <span>Municípios do Setor: {setor}</span>
                <span style="opacity: 0.6;">RESULTADOS SUGERIDOS</span>
            </div>
        ''', unsafe_allow_html=True)

        # Usando 4 colunas como no seu código original para os municípios
        cols = st.columns(4)
        
        # Sua lógica de dados original (CONSERVADA)
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

        # Sua lógica de loop e switch_page (CONSERVADA)
        for i, (nome, path) in enumerate(municipios):
            with cols[i % 4]:
                if st.button(nome, key=f"mun_{nome}_{i}", use_container_width=True):
                    if path:
                        st.switch_page(path)

    st.markdown('</div>', unsafe_allow_html=True)