import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&display=swap');

/* ---- BASE ---- */
.stApp { background-color: #060800 !important; font-family: 'Inter', sans-serif; color: #fff; }
header[data-testid="stHeader"], [data-testid="stSidebar"], .stDeployButton, footer { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ---- HEADER ---- */
.brand-header {
    padding: 36px 48px 0 48px;
    display: flex; align-items: center; gap: 12px;
}
.brand-logo { color: #a4fd4c; font-family: 'Manrope', sans-serif; font-size: 24px; font-weight: 900; }
.brand-tagline { color: #a4fd4c; font-size: 14px; font-weight: 600; opacity: 0.7; }

/* ---- MAIN WRAP ---- */
.main-wrap { max-width: 1200px; margin: 0 auto; padding: 0 48px 100px 48px; }

/* ---- HERO ---- */
.hero-title {
    font-family: 'Manrope', sans-serif; font-size: 72px; font-weight: 800;
    line-height: 1.05; margin-top: 48px; margin-bottom: 20px; color: white;
}
.hero-highlight { color: #a4fd4c; }
.hero-subtitle {
    color: #a7b076; font-size: 17px; max-width: 580px; margin-bottom: 64px; line-height: 1.6;
}

/* ---- SECTION LABEL ---- */
.section-label {
    color: white; text-transform: uppercase; letter-spacing: 3px; font-size: 13px;
    font-weight: 700; margin-bottom: 28px; display: flex; align-items: center; gap: 16px;
}
.section-label::before { content: ""; width: 40px; height: 2px; background-color: #a4fd4c; flex-shrink: 0; }

/* ---- SECTOR CARDS ---- */
.cards-row { display: flex; gap: 24px; }

.sector-card {
    flex: 1;
    background-color: rgba(255,255,255,0.03);
    border: 1px solid rgba(164,253,76,0.12);
    border-radius: 24px;
    padding: 40px;
    cursor: pointer;
    transition: all 0.35s ease;
    position: relative;
    overflow: hidden;
    min-height: 260px;
    box-sizing: border-box;
    text-decoration: none;
    display: block;
}
.sector-card:hover {
    border-color: rgba(164,253,76,0.6);
    background-color: rgba(164,253,76,0.05);
    transform: translateY(-8px);
}
.card-icon {
    width: 56px; height: 56px; background: rgba(164,253,76,0.12); border-radius: 12px;
    display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 40px;
}
.card-title { font-family: 'Manrope',sans-serif; font-size: 34px; font-weight: 700; margin-bottom: 10px; color: white; }
.card-subtitle { color: #a7b076; font-size: 14px; line-height: 1.55; max-width: 340px; }
.card-bg-icon {
    position: absolute; right: -10px; bottom: -40px; font-size: 160px;
    color: #a4fd4c; opacity: 0.04; pointer-events: none; user-select: none;
}

/* ---- MUNICÍPIOS HEADER ---- */
.results-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 56px; margin-bottom: 20px;
    padding-bottom: 16px; border-bottom: 1px solid rgba(164,253,76,0.1);
}
.results-header-title { color: white; font-size: 18px; font-weight: 600; font-family: 'Manrope',sans-serif; }
.results-header-label { color: #4a5a2a; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }

/* ---- BOTÕES MUNICÍPIOS (todos os st.button nesta tela) ---- */
div[data-testid="stButton"] > button {
    width: 100% !important;
    background-color: rgba(255,255,255,0.03) !important;
    color: #a7b076 !important;
    border: 1px solid rgba(164,253,76,0.12) !important;
    padding: 14px 20px !important;
    border-radius: 12px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stButton"] > button:hover {
    color: #a4fd4c !important;
    border-color: rgba(164,253,76,0.5) !important;
    background-color: rgba(164,253,76,0.07) !important;
}
div[data-testid="stButton"] > button:focus { box-shadow: none !important; }

/* ---- BOTÃO VER TODOS: último botão na linha de municípios ---- */
.ver-todos div[data-testid="stButton"] > button {
    background-color: #a4fd4c !important;
    color: #060800 !important;
    border: none !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}
.ver-todos div[data-testid="stButton"] > button:hover {
    background-color: #c0ff70 !important;
    color: #060800 !important;
}
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'setor_selecionado' not in st.session_state:
    st.session_state.setor_selecionado = None

# --- 4. HEADER ---
st.markdown("""
<div class="brand-header">
    <span class="brand-logo">iG2P</span>
    <span style="color:rgba(164,253,76,0.3);margin:0 10px;font-size:20px;">|</span>
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
# Estratégia: renderizamos o card visualmente em HTML e logo abaixo um st.button
# com texto invisível. O CSS do botão é resetado para ficar transparente e grande,
# mas SEM position:absolute (que quebrava antes). Em vez disso, usamos margin-top
# negativo para subir o botão sobre o card.
st.markdown('<div class="main-wrap" style="padding-bottom:0;">', unsafe_allow_html=True)
st.markdown('<div class="cards-row">', unsafe_allow_html=True)

# Injetamos CSS especial APENAS para os dois botões de setor
st.markdown("""
<style>
/* Botões de setor: invisíveis e subindo sobre o card HTML acima */
div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"] > div:last-child div[data-testid="stButton"] > button {
    opacity: 0 !important;
    height: 260px !important;
    margin-top: -268px !important;
    position: relative !important;
    z-index: 20 !important;
    background: transparent !important;
    border: none !important;
    cursor: pointer !important;
}
</style>
""", unsafe_allow_html=True)

col_edu, col_sau = st.columns(2, gap="large")

with col_edu:
    st.markdown("""
    <div class="sector-card">
        <div class="card-icon">🎓</div>
        <div class="card-title">Educação</div>
        <div class="card-bg-icon">🎓</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("edu_click", key="sector_edu"):
        st.session_state.setor_selecionado = "Educação"
        st.rerun()

with col_sau:
    st.markdown("""
    <div class="sector-card">
        <div class="card-icon">🏥</div>
        <div class="card-title">Saúde</div>
        <div class="card-bg-icon">✚</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("sau_click", key="sector_sau"):
        st.session_state.setor_selecionado = "Saúde"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # fecha cards-row
st.markdown('</div>', unsafe_allow_html=True)  # fecha main-wrap

# --- 7. LISTA DE MUNICÍPIOS ---
if st.session_state.setor_selecionado:
    setor = st.session_state.setor_selecionado

    st.markdown(f"""
    <div class="main-wrap" style="padding-bottom:0; padding-top:0;">
      <div class="results-header">
        <span class="results-header-title">Municípios do Setor</span>
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
            ("Município Educação B", None),
            ("Município Educação C", None),
            ("Município Educação D", None),
        ]

    NUM_COLS = 6
    total = len(municipios)

    st.markdown('<div class="main-wrap" style="padding-top:0;">', unsafe_allow_html=True)

    for i in range(0, total, NUM_COLS):
        chunk = municipios[i:i + NUM_COLS]
        is_last = (i + NUM_COLS >= total)
        cols = st.columns(NUM_COLS, gap="small")

        for j, (nome, path) in enumerate(chunk):
            with cols[j]:
                if st.button(nome, key=f"mun_{nome}_{i+j}"):
                    if path:
                        st.switch_page(path)

        if is_last:
            next_slot = len(chunk)
            if next_slot < NUM_COLS:
                with cols[next_slot]:
                    st.markdown('<div class="ver-todos">', unsafe_allow_html=True)
                    if st.button("VER TODOS", key="btn_ver_todos"):
                        pass  # lógica futura
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                extra = st.columns(NUM_COLS, gap="small")
                with extra[NUM_COLS - 1]:
                    st.markdown('<div class="ver-todos">', unsafe_allow_html=True)
                    if st.button("VER TODOS", key="btn_ver_todos"):
                        pass  # lógica futura
                    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)