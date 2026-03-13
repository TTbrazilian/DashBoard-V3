import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide")

# --- CSS PARA COPIAR O LAYOUT DE NAVBAR PROFISSIONAL (IMAGEM 2) ---
st.markdown("""
    <style>
    /* Esconde elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* REMOVE A SIDEBAR NA HOME */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stSidebarNav"] {display: none;}

    /* BARRA DE NAVEGAÇÃO SUPERIOR REAL (100% LARGURA) */
    .top-nav-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #252525; /* Cor exata do exemplo */
        padding: 0px 60px;
        display: flex;
        align-items: center;
        z-index: 999999;
        height: 55px;
        border-bottom: 1px solid #333;
    }

    /* ESTILO DOS BOTÕES DA NAVBAR (SEM BORDA, ESTILO TEXTO) */
    div.stButton > button {
        background-color: transparent !important;
        color: #e0e0e0 !important;
        border: none !important;
        padding: 0px 20px !important;
        height: 55px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        border-radius: 0px !important;
        transition: all 0.2s ease !important;
    }

    /* HOVER IGUAL AO EXEMPLO */
    div.stButton > button:hover {
        background-color: #333333 !important;
        color: #00CC96 !important;
    }

    /* AJUSTE DO CORPO DA PÁGINA */
    .main-body {
        margin-top: 100px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVBAR SUPERIOR ---
# HTML para garantir o posicionamento fixo do container
st.markdown('<div class="top-nav-container">', unsafe_allow_html=True)
col_nav1, col_nav2, col_nav3, col_nav4, col_nav5, col_spacer = st.columns([0.8, 1.5, 1, 1, 1, 4])

with col_nav1:
    if st.button("🏠 Home", key="home"):
        st.rerun()
with col_nav2:
    if st.button("📍 Bom Jesus da Penha", key="bj_penha"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
with col_nav3:
    st.button("🏢 Cidade X", disabled=True, key="cidade_x")
with col_nav4:
    st.button("📊 Geral", disabled=True, key="geral")
with col_nav5:
    st.button("☰ Cidades", key="cidades_menu")
st.markdown('</div>', unsafe_allow_html=True)

# --- CONTEÚDO CENTRAL ---
st.markdown('<div class="main-body">', unsafe_allow_html=True)

col_c1, col_c2, col_c3 = st.columns([1, 2, 1])

with col_c2:
    # Logotipo
    if os.path.exists("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg", use_container_width=True)
    elif os.path.exists("LOGOTIPO IG2P - OFICIAL.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL.jpg", use_container_width=True)
    
    st.markdown("<h1 style='margin-top: 20px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888;'>IG2P - Inteligência em Gestão Pública</p>", unsafe_allow_html=True)
    
    st.divider()
    st.info("Utilize o menu superior para escolher o município e visualizar os dados.")

st.markdown('</div>', unsafe_allow_html=True)