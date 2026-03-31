import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PARA DESIGN "FIEL À PRINT" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&display=swap');

    .stApp {
        background-color: #060800 !important;
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }

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
    .brand-tagline { color: #a4fd4c; font-size: 14px; font-weight: 600; opacity: 0.7; }

    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 48px 100px 48px;
    }

    .hero-title {
        font-family: 'Manrope', sans-serif;
        font-size: 72px;
        font-weight: 800;
        line-height: 1.05;
        margin-bottom: 20px;
        color: white;
    }
    .hero-highlight { color: #a4fd4c; }
    .hero-subtitle {
        color: #a7b076; 
        font-size: 17px; 
        max-width: 580px; 
        margin-bottom: 64px;
        line-height: 1.6;
    }

    .section-label {
        color: white;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 32px;
        display: flex; align-items: center; gap: 16px;
    }
    .section-label::before {
        content: ""; width: 40px; height: 2px; background-color: #a4fd4c;
    }

    /* --- FIX: CARDS SOBREPOSTOS --- */
    .button-wrapper {
        position: relative;
        width: 100%;
        height: 280px;
    }

    .sector-card {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(164, 253, 76, 0.1);
        border-radius: 24px;
        padding: 40px;
        transition: all 0.4s ease;
        z-index: 1;
        pointer-events: none;
    }

    /* O botão invisível do Streamlit */
    div[data-testid="stButton"] > button[key^="sector_"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 280px !important;
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10 !important;
        cursor: pointer !important;
        margin: 0 !important;
    }

    .button-wrapper:hover .sector-card {
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

    .card-title { font-size: 32px; font-weight: 700; margin-bottom: 10px; color: white; }
    .card-subtitle { color: #a7b076; font-size: 14px; line-height: 1.5; }
    .card-bg-icon { position: absolute; right: 20px; bottom: -30px; font-size: 180px; color: #a4fd4c; opacity: 0.03; pointer-events: none; }

    /* --- MUNICÍPIOS --- */
    div[data-testid="stButton"] > button[key^="mun_"] {
        width: 100% !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: #a7b076 !important;
        border: 1px solid rgba(164, 253, 76, 0.1) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        text-align: center !important;
    }
    div[data-testid="stButton"] > button[key^="mun_"]:hover {
        color: #a4fd4c !important;
        border-color: #a4fd4c !important;
        background-color: rgba(164, 253, 76, 0.1) !important;
    }

    /* --- BOTÃO VER TODOS --- */
    div[data-testid="stButton"] > button[key="btn_ver_todos"] {
        width: 100% !important;
        background-color: #a4fd4c !important;
        color: #060800 !important;
        border: none !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        text-align: center !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stButton"] > button[key="btn_ver_todos"]:hover {
        background-color: #b8fd6a !important;
    }

    /* --- HEADER MUNICÍPIOS --- */
    .results-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 64px;
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1px solid rgba(164, 253, 76, 0.1);
    }
    .results-header-title {
        color: white;
        font-size: 18px;
        font-weight: 600;
        font-family: 'Manrope', sans-serif;
    }
    .results-header-label {
        color: #5a6a3a;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<div class="brand-header"><span class="brand-logo">iG2P</span><span style="color:rgba(164,253,76,0.3); margin:0 10px;">|</span><span class="brand-tagline">Gestão Inteligente</span></div>', unsafe_allow_html=True)

# --- 4. CONTEÚDO PRINCIPAL ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<h1 class="hero-title">Inteligência em<br><span class="hero-highlight">Gestão Pública.</span></h1><p class="hero-subtitle">Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.</p>', unsafe_allow_html=True)

st.markdown('<div class="section-label">Selecione o Setor</div>', unsafe_allow_html=True)

if 'setor_selecionado' not in st.session_state:
    st.session_state.setor_selecionado = None

col_edu, col_sau = st.columns(2)

with col_edu:
    st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
    st.markdown('''
        <div class="sector-card">
            <div class="card-icon">🎓</div>
            <div class="card-title">Educação</div>
            <div class="card-subtitle">Índices de alfabetização, infraestrutura escolar e performance acadêmica regional.</div>
            <div class="card-bg-icon">🎓</div>
        </div>
    ''', unsafe_allow_html=True)
    if st.button(" ", key="sector_edu"):
        st.session_state.setor_selecionado = "Educação"
    st.markdown('</div>', unsafe_allow_html=True)

with col_sau:
    st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
    st.markdown('''
        <div class="sector-card">
            <div class="card-icon">🏥</div>
            <div class="card-title">Saúde</div>
            <div class="card-subtitle">Leitos disponíveis, tempo de espera e cobertura vacinal em tempo real.</div>
            <div class="card-bg-icon">✚</div>
        </div>
    ''', unsafe_allow_html=True)
    if st.button(" ", key="sector_sau"):
        st.session_state.setor_selecionado = "Saúde"
    st.markdown('</div>', unsafe_allow_html=True)

# --- LISTA DE MUNICÍPIOS ---
if st.session_state.setor_selecionado:
    setor = st.session_state.setor_selecionado

    # Header atualizado para o estilo da imagem
    st.markdown(
        '<div class="results-header">'
        '<span class="results-header-title">Municípios do Setor</span>'
        '<span class="results-header-label">Resultados Sugeridos</span>'
        '</div>',
        unsafe_allow_html=True
    )

    if setor == "Saúde":
        municipios = [
            ("Alpinópolis", "pages/Alpinópolis_Saúde.py"),
            ("Bom Jesus da Penha", "pages/Bom_Jesus_da_Penha_Saúde.py"),
            ("Cássia", "pages/Cássia_Saúde.py"),
            ("Delfinópolis", "pages/Delfinópolis_Saúde.py"),
            ("Itaú de Minas", "pages/Itaú_de_Minas_Saúde.py")
        ]
    else:
        municipios = [
            ("Alpinópolis", "pages/Alpinópolis_Educação.py"),
            ("Município Educação B", None),
            ("Município Educação C", None),
            ("Município Educação D", None)
        ]

    # Grade de 6 colunas com "VER TODOS" no último slot disponível
    NUM_COLS = 6
    total = len(municipios)

    for i in range(0, total, NUM_COLS):
        chunk = municipios[i:i + NUM_COLS]
        is_last = (i + NUM_COLS >= total)
        cols = st.columns(NUM_COLS)

        for j, (nome, path) in enumerate(chunk):
            with cols[j]:
                if st.button(nome, key=f"mun_{nome}_{i+j}"):
                    if path:
                        st.switch_page(path)

        # Botão "VER TODOS" no próximo slot da última linha
        if is_last:
            next_slot = len(chunk)
            if next_slot < NUM_COLS:
                with cols[next_slot]:
                    if st.button("VER TODOS", key="btn_ver_todos"):
                        pass  # lógica futura
            else:
                # Linha cheia: nova linha com o botão no último slot
                extra_cols = st.columns(NUM_COLS)
                with extra_cols[NUM_COLS - 1]:
                    if st.button("VER TODOS", key="btn_ver_todos"):
                        pass  # lógica futura

st.markdown('</div>', unsafe_allow_html=True)