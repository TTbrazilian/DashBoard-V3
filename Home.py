import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS GLOBAL (FIDELIDADE PIXEL-PERFECT) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

/* Fundo global e Fontes */
.stApp {
    background-color: #080A04 !important;
}

/* Ocultar UI nativa do Streamlit */
header[data-testid="stHeader"], 
[data-testid="stSidebar"], 
.stDeployButton, 
footer { 
    display: none !important; 
}

/* Ajuste de espaçamento da tela */
.block-container {
    padding-top: 3rem !important;
    padding-bottom: 5rem !important;
    max-width: 1200px !important;
}

/* Colunas precisam ser relativas para o hack dos cards funcionar */
[data-testid="column"] {
    position: relative;
}

/* Estilo Base dos Botões de Municípios */
[data-testid="stButton"] button {
    background-color: #0F140A !important;
    color: #EAEFD3 !important;
    border: 1px solid #192010 !important;
    border-radius: 8px !important;
    padding: 16px 12px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    font-family: 'Manrope', sans-serif !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

[data-testid="stButton"] button:hover {
    border-color: #8CE02A !important;
    background-color: #121A0C !important;
}
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'setor_selecionado' not in st.session_state:
    st.session_state.setor_selecionado = "Educação" # Default

# --- 4. HEADER & HERO ---
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 5rem;">
    <span style="color: #8CE02A; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 20px;">iG2P</span>
    <span style="color: #8CE02A; margin: 0 16px; opacity: 0.3;">|</span>
    <span style="color: #8CE02A; font-family: 'Manrope', sans-serif; font-weight: 600; font-size: 14px;">Gestão Inteligente</span>
</div>

<h1 style="color: #EAEFD3; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 72px; font-weight: 800; line-height: 1.05; margin: 0 0 24px 0; letter-spacing: -2px;">
    Inteligência em<br>
    <span style="color: #8CE02A;">Gestão Pública.</span>
</h1>
<p style="color: #848B6E; font-family: 'Manrope', sans-serif; font-size: 18px; line-height: 1.6; max-width: 600px; margin: 0 0 4rem 0;">
    Analise métricas em tempo real e tome decisões baseadas em dados para transformar o futuro dos municípios.
</p>

<div style="display: flex; align-items: center; margin-bottom: 2rem;">
    <div style="width: 40px; height: 2px; background-color: #8CE02A; margin-right: 16px;"></div>
    <span style="color: #848B6E; font-family: 'Manrope', sans-serif; font-size: 12px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase;">Selecione o Setor</span>
</div>
""", unsafe_allow_html=True)

# --- 5. CARDS DE SETOR ---
col1, col2 = st.columns(2, gap="large")

# Controle visual de Ativação
is_edu = st.session_state.setor_selecionado == "Educação"
edu_border = "#8CE02A" if is_edu else "#192010"
edu_bg = "#11180A" if is_edu else "#0F140A"

is_sau = st.session_state.setor_selecionado == "Saúde"
sau_border = "#8CE02A" if is_sau else "#192010"
sau_bg = "#11180A" if is_sau else "#0F140A"

# Ícones SVG idênticos à foto
svg_edu = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#8CE02A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>'''
svg_sau = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#8CE02A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M8 11h8M12 7v8"/></svg>'''

with col1:
    st.markdown(f"""
    <style>
    /* Oculta o botão real do Streamlit por cima do card HTML usando absolute positioning */
    div[data-testid="column"]:nth-child(1) [data-testid="stButton"] button {{
        position: absolute !important; top: 0; left: 0; width: 100% !important; height: 100% !important;
        opacity: 0 !important; z-index: 10 !important; cursor: pointer !important;
    }}
    </style>
    <div style="background-color: {edu_bg}; border: 1px solid {edu_border}; border-radius: 24px; padding: 40px; position: relative; overflow: hidden; height: 320px; transition: all 0.3s ease;">
        <div style="background-color: #161D0C; width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 32px;">
            {svg_edu}
        </div>
        <h2 style="color: white; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 32px; font-weight: 700; margin: 0 0 12px 0;">Educação</h2>
        <p style="color: #848B6E; font-family: 'Manrope', sans-serif; font-size: 15px; margin: 0; max-width: 90%; line-height: 1.6;">Índices de alfabetização, infraestrutura escolar e performance acadêmica regional.</p>
        <div style="position: absolute; right: -30px; bottom: -30px; width: 220px; height: 220px; opacity: 0.03; color: #8CE02A;">
            {svg_edu.replace('width="24" height="24"', 'width="100%" height="100%"')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Selecionar Educação", key="btn_edu_trigger"):
        st.session_state.setor_selecionado = "Educação"
        st.rerun()

with col2:
    st.markdown(f"""
    <style>
    div[data-testid="column"]:nth-child(2) [data-testid="stButton"] button {{
        position: absolute !important; top: 0; left: 0; width: 100% !important; height: 100% !important;
        opacity: 0 !important; z-index: 10 !important; cursor: pointer !important;
    }}
    </style>
    <div style="background-color: {sau_bg}; border: 1px solid {sau_border}; border-radius: 24px; padding: 40px; position: relative; overflow: hidden; height: 320px; transition: all 0.3s ease;">
        <div style="background-color: #161D0C; width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 32px;">
            {svg_sau}
        </div>
        <h2 style="color: white; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 32px; font-weight: 700; margin: 0 0 12px 0;">Saúde</h2>
        <p style="color: #848B6E; font-family: 'Manrope', sans-serif; font-size: 15px; margin: 0; max-width: 90%; line-height: 1.6;">Leitos disponíveis, tempo de espera e cobertura vacinal em tempo real.</p>
        <div style="position: absolute; right: -30px; bottom: -30px; width: 220px; height: 220px; opacity: 0.03; color: #8CE02A;">
            {svg_sau.replace('width="24" height="24"', 'width="100%" height="100%"')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Selecionar Saúde", key="btn_sau_trigger"):
        st.session_state.setor_selecionado = "Saúde"
        st.rerun()

# --- 6. LISTA DE MUNICÍPIOS ---
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 5rem; margin-bottom: 2rem;">
    <h3 style="color: white; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 18px; font-weight: 700; margin: 0;">Municípios do Setor</h3>
    <span style="color: #848B6E; font-family: 'Manrope', sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase;">Resultados Sugeridos</span>
</div>
""", unsafe_allow_html=True)

setor = st.session_state.setor_selecionado

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

# Grid de 6 colunas
NUM_COLS = 6
for i in range(0, len(municipios), NUM_COLS):
    cols = st.columns(NUM_COLS, gap="small")
    chunk = municipios[i:i + NUM_COLS]
    
    for j, (nome, path) in enumerate(chunk):
        with cols[j]:
            if st.button(nome, key=f"mun_{nome}_{i+j}"):
                if path: st.switch_page(path)
    
    # Botão VER TODOS formatado na última coluna vazia dinamicamente
    if len(chunk) < NUM_COLS:
        idx_ver_todos = len(chunk)
        with cols[idx_ver_todos]:
            # CSS injetado especificamente para pintar o texto do botão "Ver Todos" de verde
            css_col_nth = idx_ver_todos + 1
            st.markdown(f"""
            <style>
            div[data-testid="column"]:nth-child({css_col_nth}) [data-testid="stButton"] button p {{
                color: #8CE02A !important;
                font-size: 12px !important;
                font-weight: 800 !important;
                letter-spacing: 1.5px !important;
                text-transform: uppercase;
            }}
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("VER TODOS", key="btn_ver_todos"):
                pass  # Lógica para ver todos