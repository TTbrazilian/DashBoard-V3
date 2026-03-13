import streamlit as st
import os
from PIL import Image

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CSS PARA DESIGN IDÊNTICO E REMOÇÃO TOTAL DE INTERAÇÃO NA IMAGEM ---
st.markdown("""
    <style>
    /* Remove elementos nativos */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* FUNDO DA SIDEBAR DARK */
    [data-testid="stSidebar"] {
        background-color: #1a1c24 !important;
    }

    /* ESTILO DOS BOTÕES EM CÁPSULA */
    div.stButton > button {
        background-color: transparent !important;
        color: #9ea0a5 !important;
        border: none !important;
        text-align: left !important;
        padding: 10px 18px !important;
        font-size: 15px !important;
        width: 100% !important;
        display: block !important;
        transition: all 0.3s ease !important;
    }

    /* BOTÃO ATIVO (HOME) */
    div.stButton > button[key="nav_home"] {
        background-color: #3d3f4b !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    /* EFEITO HOVER */
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
    }

    /* REMOVE DEFINITIVAMENTE O BOTÃO DE TELA CHEIA */
    /* Alvo: Botões de overlay, botões de tela cheia e containers de ícones sobre imagens */
    [data-testid="stImage"] button, 
    [data-testid="stHorizontalBlock"] button,
    [data-testid="StyledFullScreenButton"],
    .st-emotion-cache-15zrgzn,
    .st-emotion-cache-0 {
        display: none !important;
    }
    
    /* Desativa cliques e qualquer interação na imagem */
    [data-testid="stImage"] {
        pointer-events: none !important;
        display: flex !important;
        justify-content: center !important;
        margin-top: -50px !important;
    }

    .st-emotion-cache-16idsys { padding-top: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATERAL (SIDEBAR) ---
with st.sidebar:
    if st.button("Home", key="nav_home"):
        st.rerun()
    
    if st.button("Bom Jesus da Penha", key="nav_bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    if st.button("Município 2", key="nav_m2"):
        pass
        
    if st.button("Município 3", key="nav_m3"):
        pass

    st.markdown("<hr style='border-top: 1px solid #333;'>", unsafe_allow_html=True)

# --- 4. CONTEÚDO CENTRAL ---
col_l, col_c, col_r = st.columns([1, 1.2, 1])

with col_c:
    logo_path = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
    if not os.path.exists(logo_path):
        logo_path = "Logos/LOGOTIPO IG2P - OFICIAL.jpg"

    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        # O width=380 mantém o tamanho que você aprovou
        st.image(img, width=380)
    
    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='font-weight: 400; color: white; font-size: 28px; margin-top: -10px;'>Inteligência em Gestão</h1>
            <hr style='border-top: 1px solid #333; width: 100%; margin: 20px 0;'>
            <div style='background-color: #16263a; padding: 20px; border-radius: 8px; border-left: 5px solid #2196F3;'>
                <p style='color: #90CAF9; margin: 0; font-size: 16px;'>Utilize o menu lateral para selecionar o município.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)