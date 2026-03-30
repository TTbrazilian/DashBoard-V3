import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA (Sua Lógica Original) ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. CSS (AJUSTES VISUAIS E FIX DE BOTÕES) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&display=swap');

    .stApp { background-color: #060800 !important; font-family: 'Inter', sans-serif; color: #ffffff; }
    header, [data-testid="stSidebar"], .stDeployButton, footer { display: none !important; }

    .brand-header { padding: 40px 48px; display: flex; align-items: center; gap: 12px; }
    .brand-logo { color: #a4fd4c; font-family: 'Manrope', sans-serif; font-size: 24px; font-weight: 900; }
    .main-container { max-width: 1200px; margin: 0 auto; padding: 0 48px 100px 48px; }

    /* Hero Section */
    .hero-title { font-family: 'Manrope', sans-serif; font-size: 64px; font-weight: 800; line-height: 1.1; margin-bottom: 24px; }
    .hero-highlight { color: #a4fd4c; }
    .hero-subtitle { color: #a7b076; font-size: 18px; max-width: 700px; margin-bottom: 64px; }

    .section-label { color: white; text-transform: uppercase; letter-spacing: 2px; font-size: 14px; font-weight: 700; margin-bottom: 32px; display: flex; align-items: center; gap: 16px; }
    .section-label::before { content: ""; width: 40px; height: 2px; background-color: #a4fd4c; }

    /* --- CARDS COMO BOTÕES (CORREÇÃO DE CLIQUE) --- */
    .button-container { position: relative; width: 100%; height: 280px; }

    /* Garante que o botão do Streamlit fique invisível e cubra o card todo */
    div[data-testid="stButton"] > button[key^="sector_"] {
        position: absolute !important;
        top: 0 !important; left: 0 !important;
        width: 100% !important; height: 280px !important;
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 100 !important;
        cursor: pointer !important;
    }

    .sector-card {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(164, 253, 76, 0.1);
        border-radius: 24px; padding: 40px;
        transition: all 0.4s ease; z-index: 1;
    }

    .button-container:hover .sector-card {
        border-color: #a4fd4c;
        background-color: rgba(164, 253, 76, 0.05);
        transform: translateY(-8px);
    }

    .card-icon { width: 56px; height: 56px; background: rgba(164, 253, 76, 0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 30px; }
    .card-title { font-size: 32px; font-weight: 700; margin-bottom: 8px; color: white; }
    .card-subtitle { color: #a7b076; font-size: 14px; line-height: 1.5; }
    .card-bg-icon { position: absolute; right: -20px; bottom: -30px; font-size: 180px; color: #a4fd4c; opacity: 0.03; pointer-events: none; }

    /* --- BOTÕES MUNICÍPIOS NEON --- */
    div[data-testid="stButton"] > button[key^="mun_"] {
        width: 100% !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: #a7b076 !important;
        border: 1px solid rgba(164, 253, 76, 0.1) !important;
        padding: 18px !important; border-radius: 12px !important;
        text-align: left !important; transition: 0.3s !important;
    }
    div[data-testid="stButton"] > button[key^="mun_"]:hover {
        color: #a4fd4c !important;
        border-color: #a4fd4c !important;
        background-color: rgba(164, 253, 76, 0.08) !important;
    }

    .results-header { color: #a7b076; font-size: 12px; text-transform: uppercase; margin-top: 60px; margin-bottom: 24px; border-bottom: 1px solid rgba(164, 253, 76, 0.1); padding-bottom: 12px; display: flex; justify-content: space-between; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<div class="brand-header"><span class="brand-logo">iG2P</span></div>', unsafe_allow_html=True)

# --- 4. CONTEÚDO PRINCIPAL (Funcionalidades Preservadas) ---
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Inteligência em <span class="hero-highlight">Gestão Pública.</span></h1><p class="hero-subtitle">Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.</p>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Selecione o Setor</div>', unsafe_allow_html=True)
    
    if 'setor_selecionado' not in st.session_state:
        st.session_state.setor_selecionado = None

    col_edu, col_sau = st.columns(2)
    
    with col_edu:
        st.markdown('''<div class="button-container"><div class="sector-card"><div class="card-icon">🎓</div><div class="card-title">Educação</div><div class="card-subtitle">Índices de alfabetização, infraestrutura escolar e performance acadêmica regional.</div><div class="card-bg-icon">🎓</div></div></div>''', unsafe_allow_html=True)
        # O botão agora tem um label vazio e está escondido pelo CSS por cima do card
        if st.button(" ", key="sector_edu"):
            st.session_state.setor_selecionado = "Educação"
            
    with col_sau:
        st.markdown('''<div class="button-container"><div class="sector-card"><div class="card-icon">🏥</div><div class="card-title">Saúde</div><div class="card-subtitle">Leitos disponíveis, tempo de espera e cobertura vacinal em tempo real.</div><div class="card-bg-icon">✚</div></div></div>''', unsafe_allow_html=True)
        if st.button(" ", key="sector_sau"):
            st.session_state.setor_selecionado = "Saúde"

    # --- LÓGICA DE MUNICÍPIOS (Sua Lista Original) ---
    if st.session_state.setor_selecionado:
        setor = st.session_state.setor_selecionado
        st.markdown(f'<div class="results-header"><span>Municípios do Setor: {setor}</span><span>RESULTADOS SUGERIDOS</span></div>', unsafe_allow_html=True)

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

        # Mantendo o grid original de 4 colunas
        for i in range(0, len(municipios), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(municipios):
                    nome, path = municipios[i + j]
                    with cols[j]:
                        if st.button(nome, key=f"mun_{nome}_{i+j}", use_container_width=True):
                            if path: st.switch_page(path)

    st.markdown('</div>', unsafe_allow_html=True)