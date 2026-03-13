import streamlit as st
import os
from PIL import Image

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Portal de Gestão", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CSS PARA DESIGN FIEL À IMAGEM ---
st.markdown("""
    <style>
    /* Remove elementos nativos desnecessários */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* SIDEBAR ESCURA (DESIGN DARK) */
    [data-testid="stSidebar"] {
        background-color: #1a1c24 !important;
    }

    /* BOTÕES EM ESTILO CÁPSULA (IGUAL À FOTO) */
    div.stButton > button {
        background-color: transparent !important;
        color: #9ea0a5 !important;
        border: none !important;
        text-align: left !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        width: 100% !important;
        display: block !important;
        transition: all 0.3s ease !important;
    }

    /* DESTAQUE PARA O BOTÃO HOME (ATIVO) */
    div.stButton > button[key="nav_home"] {
        background-color: #3d3f4b !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* EFEITO HOVER (ESCURECE AO PASSAR O MOUSE) */
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
    }
    
    div.stButton > button[key="nav_home"]:hover {
        background-color: #2e303a !important;
    }

    /* AJUSTE DE ESPAÇAMENTO SUPERIOR */
    .st-emotion-cache-16idsys { padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navegação manual conforme design solicitado
    if st.button("Home", key="nav_home"):
        st.rerun()
    
    if st.button("Bom Jesus da Penha", key="nav_bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    st.markdown("---")

# --- 4. CONTEÚDO CENTRAL COM LOGOTIPO DINÂMICO ---
col_1, col_2, col_3 = st.columns([1, 2, 1])

with col_2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Definição dos caminhos dos logos
    logo_branco = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
    logo_oficial = "Logos/LOGOTIPO IG2P - OFICIAL.jpg"
    
    # Lógica simples para escolher o logo (Prioriza branco no design dark)
    # Tenta detectar o modo do sistema ou usa o branco como padrão para o fundo escuro
    logo_para_exibir = logo_branco if os.path.exists(logo_branco) else logo_oficial

    if os.path.exists(logo_para_exibir):
        img = Image.open(logo_para_exibir)
        st.image(img, use_container_width=True)
    else:
        st.error("Logotipo não encontrado na pasta Logos.")

    st.markdown("<h3 style='text-align: center; color: #888; font-weight: 400; margin-top: 10px;'>Portal de Gestão de Recursos</h3>", unsafe_allow_html=True)
    st.divider()
    st.info("Utilize o menu lateral para selecionar o município.")