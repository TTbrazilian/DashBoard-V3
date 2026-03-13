import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Portal de Gestão", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CSS PARA REPLICAR A IMAGEM ---
st.markdown("""
    <style>
    /* Remove o cabeçalho branco e lixo visual */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    
    /* REMOVE A LISTA AUTOMÁTICA E O TÍTULO "NAVEGAÇÃO" */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* ESTILO DO BOTÃO HOME (IGUAL À FOTO) */
    div.stButton > button[key="btn_home_custom"] {
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 10px !important;
        border-radius: 8px !important;
    }

    /* ESTILO DA SIDEBAR ESCURA */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
    }

    /* Remove o espaçamento excessivo no topo da sidebar */
    .st-emotion-cache-16idsys {
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONTEÚDO DA SIDEBAR (CONFORME A FOTO) ---
with st.sidebar:
    # Botão Home Isolado
    st.button("🏠 Home", use_container_width=True, key="btn_home_custom")
    
    st.markdown("---") # Linha divisória fina conforme a foto
    
    # Lista de Municípios (Direto, sem título extra)
    # Usamos o expander para manter a organização escalável
    with st.expander("📍 Municípios", expanded=True):
        if st.button("🏙️ Bom Jesus da Penha", use_container_width=True, key="btn_bj"):
            st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
        
        # Aqui você adiciona os próximos municípios facilmente
        st.button("🏢 Município X", disabled=True, use_container_width=True, key="btn_x")

# --- 4. CONTEÚDO CENTRAL ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Logotipo
    logo_path = "LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
    if not os.path.exists(logo_path):
        logo_path = "LOGOTIPO IG2P - OFICIAL.jpg"
    
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>IG2P - Inteligência em Gestão Pública</p>", unsafe_allow_html=True)
    
    st.divider()
    st.info("Utilize o menu lateral para selecionar o município.")