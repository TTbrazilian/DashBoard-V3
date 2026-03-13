import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide", initial_sidebar_state="expanded")

# --- CSS PARA LIMPEZA E ESTILO ---
st.markdown("""
    <style>
    /* Esconde elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Esconde a navegação automática de arquivos que o Streamlit cria no topo da sidebar */
    div[data-testid="stSidebarNav"] {display: none;}

    /* Tira o espaço branco do topo */
    .main .block-container {
        padding-top: 2rem !important;
    }

    /* Estilização da Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111;
    }
    
    /* Ajuste para o expander de municípios não ficar colado no topo */
    .sidebar-content {
        padding-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    
    # Botão Home isolado no topo
    if st.button("🏠 Home", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    # Seção única de Municípios
    with st.expander("📍 Municípios", expanded=True):
        if st.button("🏙️ Bom Jesus da Penha", use_container_width=True):
            st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
        
        st.button("🏢 Município X", disabled=True, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- CONTEÚDO CENTRAL DA HOME ---
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
    st.info("Utilize o menu lateral para selecionar o município e visualizar os dados.")