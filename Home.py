import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Portal de Gestão", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CSS PARA REPLICAR O DESIGN DA FOTO E EFEITO HOVER ---
st.markdown("""
    <style>
    /* Remove o cabeçalho e elementos padrão */
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
        background-color: transparent !important; /* Fundo transparente por padrão */
        color: #9ea0a5 !important;
        border: none !important;
        text-align: left !important;
        padding: 8px 16px !important;
        font-size: 15px !important;
        width: 100% !important;
        display: block !important;
        transition: all 0.3s ease !important; /* Suaviza a escurecida */
    }

    /* BOTÃO SELECIONADO (O "BOM JESUS DA PENHA" DA FOTO) */
    div.stButton > button[key="btn_bj"] {
        background-color: #3d3f4b !important; /* Cor cinza da cápsula na foto */
        color: white !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    /* EFEITO HOVER (LEVE ESCURECIDA IGUAL AO DESIGN) */
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important; /* Leve destaque ao passar o mouse */
        color: white !important;
    }
    
    /* Hover específico para o botão que já está preenchido (escurece o fundo) */
    div.stButton > button[key="btn_bj"]:hover {
        background-color: #2e303a !important; /* Versão mais escura do cinza */
    }

    /* Ajuste de espaçamento no topo */
    .st-emotion-cache-16idsys { padding-top: 2.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR FIEL À FOTO ---
with st.sidebar:
    # Item Home (Apenas texto na foto)
    if st.button("Home", key="btn_home"):
        st.rerun()
    
    # Item Bom Jesus da Penha (Cápsula cinza destacada)
    if st.button("Bom Jesus da Penha", key="btn_bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")

# --- 4. CONTEÚDO CENTRAL ---
st.markdown("<br><br>", unsafe_allow_html=True)
col_c1, col_c2, col_c3 = st.columns([1, 2, 1])

with col_c2:
    st.markdown("<h1 style='text-align: center; font-size: 45px;'>IG2P</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #888;'>Portal de Gestão de Recursos</h3>", unsafe_allow_html=True)
    st.divider()
    st.info("Utilize o menu lateral para selecionar o município.")