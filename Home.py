import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA (Lógica Original) ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PARA DESIGN "FIEL À PRINT" (NEON, GRIDS E CARDS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&display=swap');

    .stApp {
        background-color: #060800 !important;
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }

    /* Remove elementos padrão */
    header[data-testid="stHeader"], [data-testid="stSidebar"], .stDeployButton, footer { 
        display: none !important; 
    }

    .brand-header {
        width: 100%;
        padding: 40px 48px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-logo { color: #a4fd4c; font-family: 'Manrope', sans-serif; font-size: 24px; font-weight: 900; }
    .brand-tagline { color: #a4fd4c; font-size: 14px; font-weight: 600; }

    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 48px 100px 48px;
    }

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
    }

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

    /* --- AJUSTE DOS CARDS COMO BOTÃO --- */
    .button-container {
        position: relative;
        width: 100%;
        height: 280px;
    }

    /* Botão invisível por cima de tudo */
    div:has(> button[key^="sector_"]) {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: 10;
    }
    div:has(> button[key^="sector_"]) button {
        width: 100% !important;
        height: 280px !important;
        opacity: 0 !important;
        cursor: pointer !important;
        border: none !important;
    }

    .sector-card {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(164, 253, 76, 0.1);
        border-radius: 24px;
        padding: 40px;
        transition: all 0.4s ease;
        overflow: hidden;
        z-index: 1;
    }

    .button-container:hover .sector-card {
        border-color: #a4fd4c;
        background-color: rgba(164, 253, 76, 0.05);
        transform: translateY(-8px);
    }

    .card-icon {
        width: 56px; height: 56px;
        background: rgba(164, 253, 76, 0.1);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px; margin-bottom: 40px;
    }

    .card-title { font-size: 32px; font-weight: 700; margin-bottom: 10px; }
    .card-subtitle { color: #a7b076; font-size: 14px; line-height: 1.5; }

    /* ÍCONES DE FUNDO */
    .card-bg-icon {
        position: absolute; right: -20px; bottom: -30px;
        font-size: 180px; color: #a4fd4c; opacity: 0.03;
        pointer-events: none;
    }

    /* --- BOTÕES MUNICÍPIOS (CORES PADRÃO) --- */
    div.stButton > button[key^="mun_"] {
        width: 100% !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: #a7b076 !important;
        border: 1px solid rgba(164, 253, 76, 0.1) !important;
        padding: 18px !important;
        border-radius: 10px !important;
        text-align: left !important;
        transition: 0.3s !important;
    }
    
    div.stButton > button[key^="mun_"]:hover {
        color: #a4fd4c !important;
        border-color: #a4fd4c !important;
        background-color: rgba(164, 253, 76, 0.08) !important;
    }

    .results-header {
        color: #a7b076; font-size: 12px; text-transform: uppercase;
        letter-spacing: 1px; margin-top: 64px; margin-bottom: 24px;
        border-bottom: 1px solid rgba(164, 253, 76, 0.1);
        padding-bottom: 16px; display: flex; justify-content: space-between;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<div class="brand-header"><span class="brand-logo">iG2P</span><span style="color:rgba(164,253,76,0.3); margin:0 10px;">|</span><span class="brand-tagline">Gestão Inteligente</span></div>', unsafe_allow_html=True)

# --- 4. CONTEÚDO PRINCIPAL (TODA A SUA LÓGICA) ---
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="hero-title">Inteligência em <span class="hero-highlight">Gestão Pública.</span></h1><p class="hero-subtitle">Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.</p>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Selecione o Setor</div>', unsafe_allow_html=True)
    col_edu, col_sau = st.columns(2)
    
    if 'setor_selecionado' not in st.session_state:
        st.session_state.setor_selecionado = None

    with col_edu:
        st.markdown('''<div class="button-container"><div class="sector-card"><div class="card-icon">🎓</div><div class="card-title">Educação</div><div class="card-subtitle">Índices de alfabetização, infraestrutura escolar e performance acadêmica regional.</div><div class="card-bg-icon">🎓</div></div></div>''', unsafe_allow_html=True)
        if st.button("Edu", key="sector_edu"):
            st.session_state.setor_selecionado = "Educação"
            
    with col_sau:
        # CRUZ VERMELHA aplicada aqui
        st.markdown('''<div class="button-container"><div class="sector-card"><div class="card-icon">🏥</div><div class="card-title">Saúde</div><div class="card-subtitle">Leitos disponíveis, tempo de espera e cobertura vacinal em tempo real.</div><div class="card-bg-icon">✚</div></div></div>''', unsafe_allow_html=True)
        if st.button("Sau", key="sector_sau"):
            st.session_state.setor_selecionado = "Saúde"

    # --- LISTA COMPLETA DE MUNICÍPIOS (SEM CORTES) ---
    if st.session_state.setor_selecionado:
        setor = st.session_state.setor_selecionado
        st.markdown(f'<div class="results-header"><span>Municípios do Setor: {setor}</span><span>RESULTADOS SUGERIDOS</span></div>', unsafe_allow_html=True)

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
                    if path: st.switch_page(path)

    st.markdown('</div>', unsafe_allow_html=True)