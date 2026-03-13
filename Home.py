import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA) ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide", initial_sidebar_state="expanded")

# --- 2. CSS PARA DESIGN IDÊNTICO À FOTO (MENU LATERAL) ---
st.markdown("""
    <style>
    /* Remove cabeçalho e lixo visual */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* COR DE FUNDO DA SIDEBAR (DARK DESIGN) */
    [data-testid="stSidebar"] {
        background-color: #1a1c24 !important;
    }

    /* ESTILO DOS BOTÕES - EXATAMENTE IGUAL À FOTO */
    div.stButton > button {
        background-color: transparent !important;
        color: #9ea0a5 !important;
        border: none !important;
        text-align: left !important;
        padding: 8px 16px !important;
        font-size: 15px !important;
        width: 100% !important;
        display: block !important;
        transition: all 0.3s ease !important;
    }

    /* ESTILO CÁPSULA PARA O BOTÃO HOME (ATIVO) */
    div.stButton > button[key="nav_home"] {
        background-color: #3d3f4b !important; /* Cor da cápsula da foto */
        color: white !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    /* EFEITO HOVER (ESCURECE AO PASSAR O MOUSE) */
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
    }
    
    div.stButton > button[key="nav_home"]:hover {
        background-color: #2e303a !important; /* Escurecida leve */
    }

    .st-emotion-cache-16idsys { padding-top: 2.5rem !important; }

    /* ESTILIZAÇÃO DO LOGOTIPO CENTRALIZADO */
    .centered-logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        max-width: 400px; /* Ajuste o tamanho conforme necessário */
        height: auto;
    }

    /* DETECÇÃO DE MODO CLARO/ESCURO PELO CSS */
    @media (prefers-color-scheme: dark) {
        .logo-claro { display: none !important; }
        .logo-escuro { display: block !important; }
    }
    @media (prefers-color-scheme: light) {
        .logo-escuro { display: none !important; }
        .logo-claro { display: block !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATERAL (SIDEBAR) ---
with st.sidebar:
    # Botão Home (Estilo Cápsula Ativo)
    if st.button("Home", key="nav_home"):
        st.rerun()
    
    # Botão Município (Estilo Texto Simples)
    if st.button("Bom Jesus da Penha", key="nav_bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")

# --- 4. CONTEÚDO CENTRAL DA HOME ---
st.markdown("<br><br>", unsafe_allow_html=True) # Espaçador top
col_c1, col_c2, col_c3 = st.columns([1, 2, 1])

with col_c2:
    # --- LOGOTIPO INTELIGENTE (MODO CLARO/ESCURO) ---
    # Usamos HTML puro para controlar a visibilidade via CSS
    # É essencial que os arquivos existam na raiz com esses nomes exatos.
    
    logo_branco_path = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
    logo_oficial_path = "Logos/LOGOTIPO IG2P - OFICIAL.jpg"

    if os.path.exists(logo_branco_path) and os.path.exists(logo_oficial_path):
        # Exibe ambas as imagens, o CSS controla qual aparece.
        st.markdown(f'<img src="{logo_branco_path}" class="centered-logo logo-escuro" alt="IG2P Modo Escuro">', unsafe_allow_html=True)
        st.markdown(f'<img src="{logo_oficial_path}" class="centered-logo logo-claro" alt="IG2P Modo Claro">', unsafe_allow_html=True)
    
    else:
        # Fallback caso os arquivos não existam (para não quebrar a página)
        st.markdown("<h1 style='text-align: center; font-size: 50px;'>IG2P</h1>", unsafe_allow_html=True)
        st.error(f"Erro: Verifique se os arquivos de logotipo existem em: {logo_branco_path} e {logo_oficial_path}")

    st.markdown("<br><h3 style='text-align: center; color: #888; font-weight: 400;'>Portal de Gestão de Recursos</h3>", unsafe_allow_html=True)
    st.divider()
    st.info("Utilize o menu lateral para selecionar o município.")