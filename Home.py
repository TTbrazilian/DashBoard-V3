import streamlit as st
import os
from PIL import Image

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide", initial_sidebar_state="expanded")

# --- 2. CSS PARA DESIGN IDÊNTICO À FOTO (MENU LATERAL) ---
st.markdown("""
    <style>
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* SIDEBAR ESCURA CONFORME PADRÃO SOLICITADO */
    [data-testid="stSidebar"] {
        background-color: #1a1c24 !important;
    }

    /* ESTILO DOS BOTÕES - DESIGN DE CÁPSULA ARREDONDADA */
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

    /* ITEM HOME ATIVO (CÁPSULA CINZA) */
    div.stButton > button[key="nav_home"] {
        background-color: #3d3f4b !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* EFEITO HOVER - ESCURECER */
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
    }
    
    div.stButton > button[key="nav_home"]:hover {
        background-color: #2e303a !important;
    }

    .st-emotion-cache-16idsys { padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATERAL (SIDEBAR) ---
with st.sidebar:
    if st.button("Home", key="nav_home"):
        st.rerun()
    
    if st.button("Bom Jesus da Penha", key="nav_bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    st.markdown("---")

# --- 4. LÓGICA DO LOGOTIPO (MODO CLARO vs ESCURO) ---
# Caminhos baseados na sua estrutura de pastas
path_logo_branco = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
path_logo_oficial = "Logos/LOGOTIPO IG2P - OFICIAL.jpg"

def get_logo():
    # Detecta o tema atual do Streamlit (claro ou escuro)
    # Nota: 'theme' funciona melhor se definido no config.toml, 
    # caso contrário, usamos a detecção de arquivo como fallback
    try:
        if st.get_option("theme.base") == "dark":
            return path_logo_branco
        return path_logo_oficial
    except:
        return path_logo_branco # Default para o design escuro que você prefere

# --- 5. CONTEÚDO CENTRAL ---
st.markdown("<br>", unsafe_allow_html=True)
col_1, col_2, col_3 = st.columns([1, 2, 1])

with col_2:
    # Exibição do Logo referenciando os nomes de arquivo corretos
    logo_atual = get_logo()
    
    if os.path.exists(logo_atual):
        img = Image.open(logo_atual)
        st.image(img, use_container_width=True)
    else:
        # Fallback caso o caminho da pasta Logos esteja diferente
        st.warning(f"Logotipo não encontrado em: {logo_atual}")

    st.markdown("<h3 style='text-align: center; color: #888; font-weight: 400;'>Portal de Gestão de Recursos</h3>", unsafe_allow_html=True)
    st.divider()
    st.info("Utilize o menu lateral para selecionar o município.")