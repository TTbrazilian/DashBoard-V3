import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PARA TRANSFORMAR CARD EM BOTÃO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&display=swap');

    .stApp { background-color: #060800 !important; font-family: 'Inter', sans-serif; color: #ffffff; }
    header, [data-testid="stSidebar"], .stDeployButton, footer { display: none !important; }

    .main-container { max-width: 1200px; margin: 0 auto; padding: 0 48px 100px 48px; }
    
    /* Container relativo para que o botão possa flutuar sobre o card */
    .card-wrapper {
        position: relative;
        width: 100%;
        height: 280px; /* Mesma altura do seu card */
        margin-bottom: 20px;
    }

    /* O Card visual */
    .sector-card {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(164, 253, 76, 0.1);
        border-radius: 24px;
        padding: 40px;
        z-index: 1; /* Fica atrás */
        transition: all 0.4s ease;
    }

    /* O Botão real do Streamlit (Invisível mas clicável) */
    div[data-testid="stButton"] > button[key^="sector_"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 280px !important;
        background-color: transparent !important;
        color: transparent !important; /* Esconde o texto do botão */
        border: none !important;
        z-index: 10 !important; /* Fica na frente de tudo */
        cursor: pointer !important;
    }

    /* Efeito visual de hover no card quando o mouse está sobre o wrapper */
    .card-wrapper:hover .sector-card {
        border-color: #a4fd4c;
        background-color: rgba(164, 253, 76, 0.05);
        transform: translateY(-8px);
    }

    .card-icon { width: 56px; height: 56px; background: rgba(164, 253, 76, 0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 30px; }
    .card-title { font-size: 32px; font-weight: 700; margin-bottom: 8px; color: white; }
    .card-subtitle { color: #a7b076; font-size: 14px; line-height: 1.5; }
    .card-bg-icon { position: absolute; right: -20px; bottom: -30px; font-size: 180px; color: #a4fd4c; opacity: 0.03; pointer-events: none; }

    /* Estilo dos Botões de Municípios */
    div[data-testid="stButton"] > button[key^="mun_"] {
        width: 100% !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: #a7b076 !important;
        border: 1px solid rgba(164, 253, 76, 0.1) !important;
        padding: 16px !important;
        border-radius: 12px !important;
        text-align: left !important;
    }
    div[data-testid="stButton"] > button[key^="mun_"]:hover {
        color: #a4fd4c !important;
        border-color: #a4fd4c !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONTEÚDO ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Hero Section
st.markdown('<h1 style="font-size: 64px; font-weight: 800; margin-bottom: 24px;">Inteligência em <span style="color: #a4fd4c;">Gestão Pública.</span></h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #a7b076; font-size: 18px; margin-bottom: 64px;">Analise métricas em tempo real e tome decisões para transformar o futuro dos municípios.</p>', unsafe_allow_html=True)

st.markdown('<div style="color: white; text-transform: uppercase; letter-spacing: 2px; font-size: 14px; font-weight: 700; margin-bottom: 32px;">Selecione o Setor</div>', unsafe_allow_html=True)

if 'setor_selecionado' not in st.session_state:
    st.session_state.setor_selecionado = None

col1, col2 = st.columns(2)

# EDUCAÇÃO
with col1:
    st.markdown('''
        <div class="card-wrapper">
            <div class="sector-card">
                <div class="card-icon">🎓</div>
                <div class="card-title">Educação</div>
                <div class="card-subtitle">Índices de alfabetização e performance acadêmica.</div>
                <div class="card-bg-icon">🎓</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    # O botão invisível por cima do card
    if st.button("Edu", key="sector_edu"):
        st.session_state.setor_selecionado = "Educação"

# SAÚDE
with col2:
    st.markdown('''
        <div class="card-wrapper">
            <div class="sector-card">
                <div class="card-icon">🏥</div>
                <div class="card-title">Saúde</div>
                <div class="card-subtitle">Leitos disponíveis e cobertura vacinal em tempo real.</div>
                <div class="card-bg-icon">✚</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    # O botão invisível por cima do card
    if st.button("Sau", key="sector_sau"):
        st.session_state.setor_selecionado = "Saúde"

# MUNICÍPIOS (Lógica preservada)
if st.session_state.setor_selecionado:
    st.markdown(f"### Municípios do Setor: {st.session_state.setor_selecionado}")
    
    municipios = ["São Paulo", "Rio de Janeiro", "Curitiba", "Belo Horizonte", "Porto Alegre", "Fortaleza"]
    
    cols = st.columns(3)
    for idx, mun in enumerate(municipios):
        with cols[idx % 3]:
            if st.button(mun, key=f"mun_{mun}"):
                st.write(f"Selecionado: {mun}")

st.markdown('</div>', unsafe_allow_html=True)