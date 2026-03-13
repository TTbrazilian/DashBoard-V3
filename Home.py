import streamlit as st
import os
from PIL import Image

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CSS PARA DESIGN IDÊNTICO AO DASHBOARD ---
st.markdown("""
    <style>
    /* Remove elementos nativos e cabeçalho fixo */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* FUNDO DA SIDEBAR DARK */
    [data-testid="stSidebar"] {
        background-color: #1a1c24 !important;
    }

    /* ESTILO DOS BOTÕES EM CÁPSULA (PADRÃO BOM JESUS) */
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
    
    div.stButton > button[key="nav_home"]:hover {
        background-color: #2e303a !important; 
    }

    /* Respiro no topo da sidebar */
    .st-emotion-cache-16idsys { padding-top: 2rem !important; }

    /* REMOVE TELA CHEIA E CENTRALIZA POSIÇÃO DO LOGO */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    [data-testid="stImage"] img {
        pointer-events: none; /* Desativa o clique e o ícone de tela cheia */
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATERAL (SIDEBAR) ---
with st.sidebar:
    if st.button("🏠 Home", key="nav_home"):
        st.rerun()
    
    if st.button("🏙️ Bom Jesus da Penha", key="nav_bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    if st.button("🏢 Município 2", key="nav_m2"):
        pass
        
    if st.button("🏢 Município 3", key="nav_m3"):
        pass

    st.markdown("---")
    st.info("Selecione um município acima para visualizar os dados.")

# --- 4. CONTEÚDO CENTRAL (POSIÇÃO EXATA DO LOGO) ---
# Colunas ajustadas para centralizar o logo exatamente como na foto
_, col_central, _ = st.columns([1, 2, 1])

with col_central:
    # Espaçamento para alinhar no topo como cabeçalho
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Caminho dos logos conforme sua estrutura
    logo_path = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
    if not os.path.exists(logo_path):
        logo_path = "Logos/LOGOTIPO IG2P - OFICIAL.jpg"

    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        # Largura ajustada para manter proporção de cabeçalho
        st.image(img, width=400)
    
    # Texto e Estilo conforme solicitado
    st.markdown("""
        <div style='text-align: center; margin-top: 10px;'>
            <h2 style='font-weight: 400; color: #E0E0E0; font-size: 26px;'>Inteligência em Gestão</h2>
            <hr style='border-top: 1px solid #333; width: 80%; margin: 20px auto;'>
            <div style='background-color: #16263a; padding: 15px; border-radius: 5px; border-left: 5px solid #2196F3;'>
                <p style='color: #90CAF9; margin: 0; font-size: 14px;'>Utilize o menu lateral para navegar entre os dashboards.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)