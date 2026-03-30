import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PARA CARD TOTALMENTE CLICÁVEL (SEM BOTÃO EM BAIXO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&display=swap');

    .stApp { background-color: #060800 !important; font-family: 'Inter', sans-serif; color: #ffffff; }
    header, [data-testid="stSidebar"], .stDeployButton, footer { display: none !important; }

    .main-container { max-width: 1200px; margin: 0 auto; padding: 0 48px 100px 48px; }

    /* Container do Card */
    .card-container {
        position: relative;
        height: 280px;
        width: 100%;
        display: grid;
        place-items: stretch;
    }

    /* O Card Visual (Fundo) */
    .sector-card {
        grid-area: 1 / 1; /* Ocupa a mesma célula do grid que o botão */
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(164, 253, 76, 0.1);
        border-radius: 24px;
        padding: 40px;
        transition: all 0.4s ease;
        z-index: 1;
        pointer-events: none; /* Deixa o clique passar para o botão */
    }

    /* O Botão do Streamlit (Frente e Invisível) */
    div[data-testid="stButton"] > button[key^="sector_"] {
        grid-area: 1 / 1; /* Ocupa a mesma célula do grid que o card */
        width: 100% !important;
        height: 280px !important;
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 2 !important; /* Fica na frente para capturar o clique */
        cursor: pointer !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Hover no container reflete no card */
    .card-container:hover .sector-card {
        border-color: #a4fd4c;
        background-color: rgba(164, 253, 76, 0.05);
        transform: translateY(-8px);
    }

    .card-icon { width: 56px; height: 56px; background: rgba(164, 253, 76, 0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 30px; }
    .card-title { font-size: 32px; font-weight: 700; margin-bottom: 8px; color: white; }
    .card-subtitle { color: #a7b076; font-size: 14px; line-height: 1.5; }

    /* Estilo dos Municípios (Neon) */
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
        background-color: rgba(164, 253, 76, 0.08) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONTEÚDO PRINCIPAL ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<h1 style="font-size: 64px; font-weight: 800; margin-bottom: 24px;">Inteligência em <span style="color: #a4fd4c;">Gestão Pública.</span></h1>', unsafe_allow_html=True)

if 'setor_selecionado' not in st.session_state:
    st.session_state.setor_selecionado = None

col_edu, col_sau = st.columns(2)

# EDUCAÇÃO
with col_edu:
    st.markdown('''
        <div class="card-container">
            <div class="sector-card">
                <div class="card-icon">🎓</div>
                <div class="card-title">Educação</div>
                <div class="card-subtitle">Índices de alfabetização, infraestrutura escolar e performance regional.</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("Educação", key="sector_edu"):
        st.session_state.setor_selecionado = "Educação"

# SAÚDE
with col_sau:
    st.markdown('''
        <div class="card-container">
            <div class="sector-card">
                <div class="card-icon">🏥</div>
                <div class="card-title">Saúde</div>
                <div class="card-subtitle">Leitos disponíveis, tempo de espera e cobertura vacinal em tempo real.</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("Saúde", key="sector_sau"):
        st.session_state.setor_selecionado = "Saúde"

# --- MUNICÍPIOS (Lógica de exibição preservada) ---
if st.session_state.setor_selecionado:
    setor = st.session_state.setor_selecionado
    st.markdown(f"### Municípios do Setor: {setor}")
    
    # Lista de municípios baseada no setor (Sua lógica original)
    if setor == "Saúde":
        municipios = ["Alpinópolis", "Bom Jesus da Penha", "Cássia", "Delfinópolis", "Itaú de Minas"]
    else:
        municipios = ["São Paulo", "Rio de Janeiro", "Curitiba", "Belo Horizonte"]

    for i in range(0, len(municipios), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(municipios):
                nome = municipios[i+j]
                with cols[j]:
                    if st.button(nome, key=f"mun_{nome}"):
                        st.write(f"Abrindo dashboard de {nome}...")

st.markdown('</div>', unsafe_allow_html=True)