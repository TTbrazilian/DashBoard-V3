import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide", initial_sidebar_state="expanded")

# --- 2. CSS PARA CORRIGIR A VISIBILIDADE DA SIDEBAR ---
st.markdown("""
    <style>
    /* Esconde elementos padrão do cabeçalho */
    [data-testid="stHeader"] {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* ESCONDE APENAS A LISTA AUTOMÁTICA DE LINKS (O que causou o sumiço) */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* GARANTE QUE A SIDEBAR APAREÇA E TENHA COR */
    [data-testid="stSidebar"] {
        visibility: visible !important;
        background-color: #111111 !important;
    }

    /* Ajuste de respiro para os botões não colarem no topo */
    .st-emotion-cache-16idsys {
        padding-top: 3rem !important;
    }
    
    /* Centralização do conteúdo principal */
    .main .block-container {
        padding-top: 3rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONTEÚDO DA SIDEBAR ---
# Note que agora o conteúdo está fora de qualquer condicional para forçar a renderização
with st.sidebar:
    # Botão Home
    if st.button("🏠 Home", use_container_width=True, key="home_btn"):
        st.rerun()
    
    st.markdown("---")
    
    # Seção de Municípios
    with st.expander("📍 Municípios", expanded=True):
        if st.button("🏙️ Bom Jesus da Penha", use_container_width=True, key="bj_btn"):
            st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
        
        st.button("🏢 Município X", disabled=True, use_container_width=True, key="x_btn")

# --- 4. CONTEÚDO CENTRAL DA HOME ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Lógica do Logotipo
    logo_path = "LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
    if not os.path.exists(logo_path):
        logo_path = "LOGOTIPO IG2P - OFICIAL.jpg"
    
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>IG2P - Inteligência em Gestão Pública</p>", unsafe_allow_html=True)
    
    st.divider()
    st.info("Utilize o menu lateral à esquerda para navegar entre os municípios.")