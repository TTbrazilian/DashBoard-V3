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
        transition: all 0.3s ease !important; /* Suaviza a transição do hover */
    }

    /* BOTÃO ATIVO (ONDE O USUÁRIO ESTÁ) */
    div.stButton > button[key="nav_home"] {
        background-color: #3d3f4b !important; /* Cinza cápsula do dashboard */
        color: white !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    /* EFEITO HOVER - LEVE ESCURECIDA IGUAL À IMAGEM SOLICITADA */
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
    }
    
    /* Escurecimento específico para o botão que já está preenchido */
    div.stButton > button[key="nav_home"]:hover {
        background-color: #2e303a !important; 
    }

    /* Ajuste de respiro no topo da sidebar */
    .st-emotion-cache-16idsys { padding-top: 2rem !important; }

    /* Ajuste da imagem centralizada para não esticar */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botão Home (Marcado como Ativo)
    if st.button("Home", key="nav_home"):
        st.rerun()
    
    # Botão de Navegação para a página de dados
    if st.button("Bom Jesus da Penha", key="nav_bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    st.markdown("<hr style='border-top: 1px solid #333;'>", unsafe_allow_html=True)

# --- 4. CONTEÚDO CENTRAL (LOGOTIPO E TÍTULO) ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Carregamento do Logo (Prioriza a versão clara para fundo escuro)
    logo_path = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
    if not os.path.exists(logo_path):
        logo_path = "Logos/LOGOTIPO IG2P - OFICIAL.jpg"

    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        # Exibe o logo com largura controlada para ficar identico à imagem
        st.image(img, width=450)
    
    # Título e Instrução exatamente como na imagem de referência
    st.markdown("""
        <div style='text-align: center; margin-top: 20px;'>
            <h2 style='font-weight: 400; color: #E0E0E0;'>Portal de Gestão de Recursos</h2>
            <hr style='border-top: 1px solid #333; width: 80%; margin: 20px auto;'>
            <div style='background-color: #16263a; padding: 15px; border-radius: 5px; border-left: 5px solid #2196F3;'>
                <p style='color: #90CAF9; margin: 0;'>Utilize o menu lateral para selecionar o município.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)