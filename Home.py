import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Portal de Gestão", 
    layout="wide", 
    initial_sidebar_state="expanded" # Mantém aberto por padrão, mas o usuário pode fechar no botão >
)

# --- 2. CSS PARA LIMPAR E MANTER O CONTROLE ---
st.markdown("""
    <style>
    /* Esconde o cabeçalho nativo mas mantém o botão de fechar/abrir a sidebar */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* ESCONDE APENAS A LISTA DE ARQUIVOS QUE O STREAMLIT GERA */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Estilo da Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
    }

    /* Remove o botão de Deploy e outros lixos */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* Respiro para o conteúdo não colar no topo */
    .main .block-container {
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONTEÚDO DA SIDEBAR ---
# O Streamlit já coloca um botão de ">" no topo da sidebar para abrir/fechar.
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True) # Espaçador top
    
    # Botão Home
    if st.button("🏠 Home", use_container_width=True, key="home_nav"):
        st.rerun()
    
    st.markdown("---")
    
    # Menu de Municípios
    with st.expander("📍 Municípios", expanded=True):
        if st.button("🏙️ Bom Jesus da Penha", use_container_width=True, key="bj_nav"):
            st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
        
        st.button("🏢 Município X", disabled=True, use_container_width=True, key="x_nav")

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
    st.info("Utilize a barra lateral à esquerda (botão > no topo) para navegar.")