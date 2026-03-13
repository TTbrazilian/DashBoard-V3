import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Portal de Gestão", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CSS PARA REPLICAR FIELMENTE A FOTO ---
st.markdown("""
    <style>
    /* Remove o cabeçalho e lixo visual */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    
    /* ESCONDE A NAVEGAÇÃO AUTOMÁTICA E O TÍTULO "NAVEGAÇÃO" */
    [data-testid="stSidebarNav"] { display: none !important; }

    /* ESTILO DA SIDEBAR ESCURA */
    [data-testid="stSidebar"] {
        background-color: #1a1c24 !important; /* Tom exato da foto */
    }

    /* ESTILO DOS BOTÕES (ESTILO CÁPSULA DA FOTO) */
    div.stButton > button {
        background-color: transparent !important;
        color: #9ea0a5 !important; /* Cor do texto não selecionado */
        border: none !important;
        text-align: left !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        width: 100% !important;
        display: block !important;
    }

    /* BOTÃO SELECIONADO / ATIVO (IGUAL AO "BOM JESUS" NA FOTO) */
    div.stButton > button[key="btn_bj"] {
        background-color: #3d3f4b !important; /* Fundo cinza da cápsula */
        color: white !important; /* Texto branco em destaque */
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* Ajuste de espaçamento no topo da sidebar */
    .st-emotion-cache-16idsys { padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATERAL (SIDEBAR) EXATAMENTE COMO A FOTO ---
with st.sidebar:
    # Item "Home" (Texto simples, conforme a foto)
    if st.button("Home", key="btn_home_text"):
        st.rerun()
    
    # Item "Bom Jesus da Penha" (Estilo Cápsula Selecionada)
    if st.button("Bom Jesus da Penha", key="btn_bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    # Espaçador para futuros municípios (Escalabilidade)
    st.markdown("<br>", unsafe_allow_html=True)

# --- 4. CONTEÚDO CENTRAL DA HOME ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Exibe IG2P centralizado
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>IG2P</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Portal de Gestão de Recursos</h2>", unsafe_allow_html=True)
    
    st.divider()
    
    # Caixa de aviso azulada conforme o layout anterior
    st.info("Utilize o menu lateral para escolher o município e visualizar os dados.")