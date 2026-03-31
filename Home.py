import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS (FIDELIDADE ABSOLUTA À IMAGEM) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

/* ---- BASE ---- */
.stApp { 
    background-color: #0C1004 !important; 
    font-family: 'Manrope', sans-serif; 
    color: #E0E5CE; 
}

/* Remover elementos padrão do Streamlit */
header[data-testid="stHeader"], 
[data-testid="stSidebar"], 
.stDeployButton, 
footer { 
    display: none !important; 
}

.block-container { 
    padding: 0 !important; 
    max-width: 100% !important; 
}

/* ---- HEADER ---- */
.brand-header {
    padding: 48px 64px 0 64px;
    display: flex; 
    align-items: center; 
    gap: 16px;
}
.brand-logo { 
    color: #BFFF00; 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    font-size: 28px; 
    font-weight: 800; 
    letter-spacing: -1px;
}
.brand-tagline { 
    color: #BFFF00; 
    font-size: 14px; 
    font-weight: 600; 
    opacity: 0.8;
}

/* ---- MAIN WRAP ---- */
.main-wrap { 
    max-width: 1400px; 
    margin: 0 auto; 
    padding: 0 64px; 
}

/* ---- HERO ---- */
.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif; 
    font-size: 96px; 
    font-weight: 800;
    line-height: 0.95; 
    margin-top: 80px; 
    margin-bottom: 24px; 
    color: white;
    letter-spacing: -3px;
}
.hero-highlight { 
    color: #BFFF00; 
}
.hero-subtitle {
    color: #8A9175; 
    font-size: 20px; 
    max-width: 640px; 
    margin-bottom: 80px; 
    line-height: 1.5;
    font-weight: 400;
}

/* ---- SECTION LABEL ---- */
.section-label {
    color: #BFFF00; 
    text-transform: uppercase; 
    letter-spacing: 4px; 
    font-size: 14px;
    font-weight: 700; 
    margin-bottom: 40px; 
    display: flex; 
    align-items: center; 
    gap: 20px;
}
.section-label::before { 
    content: ""; 
    width: 60px; 
    height: 3px; 
    background-color: #BFFF00; 
    flex-shrink: 0; 
}

/* ---- SECTOR CARDS ---- */
.sector-card {
    background-color: #111508;
    border: 1px solid rgba(191, 255, 0, 0.1);
    border-radius: 32px;
    padding: 48px;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
    min-height: 320px;
}

.sector-card.active {
    border-color: #BFFF00;
    background-color: rgba(191, 255, 0, 0.03);
    box-shadow: 0 0 40px rgba(191, 255, 0, 0.05);
}

.card-icon-box {
    width: 64px; 
    height: 64px; 
    background: rgba(191, 255, 0, 0.1); 
    border-radius: 16px;
    display: flex; 
    align-items: center; 
    justify-content: center; 
    font-size: 28px; 
    margin-bottom: 48px;
}

.card-title { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    font-size: 42px; 
    font-weight: 700; 
    margin-bottom: 12px; 
    color: white; 
}
.card-subtitle { 
    color: #8A9175; 
    font-size: 16px; 
    line-height: 1.6; 
    max-width: 380px; 
}

.card-bg-icon {
    position: absolute; 
    right: -20px; 
    bottom: -40px; 
    font-size: 200px;
    color: #BFFF00; 
    opacity: 0.03; 
    pointer-events: none;
}

/* ---- MUNICÍPIOS SECTION ---- */
.results-header {
    display: flex; 
    justify-content: space-between; 
    align-items: center;
    margin-top: 100px; 
    margin-bottom: 32px;
}
.results-header-title { 
    color: white; 
    font-size: 24px; 
    font-weight: 700; 
    font-family: 'Plus Jakarta Sans', sans-serif; 
}
.results-header-label { 
    color: #4A5A2A; 
    font-size: 12px; 
    text-transform: uppercase; 
    letter-spacing: 2px; 
    font-weight: 700; 
}

/* ---- BOTÕES MUNICÍPIOS ---- */
div[data-testid="stButton"] > button {
    width: 100% !important;
    background-color: #111508 !important;
    color: #E0E5CE !important;
    border: 1px solid rgba(191, 255, 0, 0.05) !important;
    padding: 18px 24px !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    font-family: 'Manrope', sans-serif !important;
    text-align: center !important;
}

div[data-testid="stButton"] > button:hover {
    color: #BFFF00 !important;
    border-color: rgba(191, 255, 0, 0.4) !important;
    background-color: rgba(191, 255, 0, 0.05) !important;
}

/* Overlay para botões invisíveis nos cards */
.overlay-button div[data-testid="stButton"] > button {
    opacity: 0 !important;
    height: 320px !important;
    margin-top: -320px !important;
    position: relative !important;
    z-index: 10 !important;
    border: none !important;
    cursor: pointer !important;
}

/* VER TODOS */
.ver-todos div[data-testid="stButton"] > button {
    background-color: transparent !important;
    color: #BFFF00 !important;
    border: 1px solid #BFFF00 !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

.ver-todos div[data-testid="stButton"] > button:hover {
    background-color: #BFFF00 !important;
    color: #0C1004 !important;
}
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'setor_selecionado' not in st.session_state:
    st.session_state.setor_selecionado = "Saúde"

# --- 4. HEADER ---
st.markdown("""
<div class="brand-header">
    <span class="brand-logo">iG2P</span>
    <span style="color:rgba(191,255,0,0.2);margin:0 4px;font-size:24px;font-weight:200;">|</span>
    <span class="brand-tagline">Gestão Inteligente</span>
</div>
""", unsafe_allow_html=True)

# --- 5. HERO ---
st.markdown("""
<div class="main-wrap">
  <h1 class="hero-title">Inteligência em<br><span class="hero-highlight">Gestão Pública.</span></h1>
  <p class="hero-subtitle">Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.</p>
  <div class="section-label">Selecione o Setor</div>
</div>
""", unsafe_allow_html=True)

# --- 6. CARDS DE SETOR ---
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
col_edu, col_sau = st.columns(2, gap="large")

with col_edu:
    is_active = "active" if st.session_state.setor_selecionado == "Educação" else ""
    st.markdown(f"""
    <div class="sector-card {is_active}">
        <div class="card-icon-box">🎓</div>
        <div class="card-title">Educação</div>
        <p class="card-subtitle">Índices de alfabetização, infraestrutura escolar e performance acadêmica regional.</p>
        <div class="card-bg-icon">🎓</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="overlay-button">', unsafe_allow_html=True)
    if st.button("Selecionar Educação", key="btn_edu_trigger"):
        st.session_state.setor_selecionado = "Educação"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_sau:
    is_active = "active" if st.session_state.setor_selecionado == "Saúde" else ""
    st.markdown(f"""
    <div class="sector-card {is_active}">
        <div class="card-icon-box">🛡️</div>
        <div class="card-title">Saúde</div>
        <p class="card-subtitle">Leitos disponíveis, tempo de espera e cobertura vacinal em tempo real.</p>
        <div class="card-bg-icon">✚</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="overlay-button">', unsafe_allow_html=True)
    if st.button("Selecionar Saúde", key="btn_sau_trigger"):
        st.session_state.setor_selecionado = "Saúde"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. LISTA DE MUNICÍPIOS (MANTENDO RIGOROSAMENTE A SUA LISTA) ---
setor = st.session_state.setor_selecionado

st.markdown(f"""
<div class="main-wrap">
  <div class="results-header">
    <span class="results-header-title">Municípios do Setor: {setor}</span>
    <span class="results-header-label">Resultados Sugeridos</span>
  </div>
</div>
""", unsafe_allow_html=True)

if setor == "Saúde":
    municipios = [
        ("Alpinópolis", "pages/Alpinópolis_Saúde.py"),
        ("Bom Jesus da Penha", "pages/Bom_Jesus_da_Penha_Saúde.py"),
        ("Cássia", "pages/Cássia_Saúde.py"),
        ("Delfinópolis", "pages/Delfinópolis_Saúde.py"),
        ("Itaú de Minas", "pages/Itaú_de_Minas_Saúde.py"),
    ]
else:
    municipios = [
        ("Alpinópolis", "pages/Alpinópolis_Educação.py"),
        ("Bom Jesus da Penha", "pages/Bom_Jesus_da_Penha_Educação.py"),
        ("Cássia", "pages/Cássia_Educação.py"),
        ("Delfinópolis", "pages/Delfinópolis_Educação.py"),
        ("Itaú de Minas", "pages/Itaú_de_Minas_Educação.py"),
    ]

st.markdown('<div class="main-wrap" style="padding-bottom:120px;">', unsafe_allow_html=True)
NUM_COLS = 6
for i in range(0, len(municipios), NUM_COLS):
    cols = st.columns(NUM_COLS, gap="small")
    chunk = municipios[i:i + NUM_COLS]
    for j, (nome, path) in enumerate(chunk):
        with cols[j]:
            if st.button(nome, key=f"mun_{nome}_{i+j}"):
                if path: st.info(f"Navegando para {path}")
    
    # Adicionar o botão "VER TODOS" na última coluna da primeira linha disponível
    last_chunk_len = len(chunk)
    if last_chunk_len < NUM_COLS:
        with cols[last_chunk_len]:
            st.markdown('<div class="ver-todos">', unsafe_allow_html=True)
            if st.button("VER TODOS", key="btn_ver_todos"):
                pass
            st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
