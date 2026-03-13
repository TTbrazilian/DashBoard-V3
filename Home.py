import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide")

# --- CSS PARA DESIGN SUPERIOR E REMOÇÃO DE SIDEBAR NA HOME ---
st.markdown("""
    <style>
    /* Esconde elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* REMOVE A SIDEBAR APENAS NA HOME */
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* BARRA DE NAVEGAÇÃO SUPERIOR REAL */
    .nav-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #1a1a1a;
        padding: 10px 50px;
        display: flex;
        align-items: center;
        z-index: 999999;
        border-bottom: 2px solid #333;
    }

    /* ESTILIZAÇÃO DOS BOTÕES PARA PARECEREM MENU DE CATEGORIAS */
    div.stButton > button {
        background-color: #262626 !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        border-radius: 4px !important;
        padding: 8px 20px !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    div.stButton > button:hover {
        border-color: #00CC96 !important;
        color: #00CC96 !important;
        background-color: #333333 !important;
        transform: translateY(-2px);
    }

    /* AJUSTE DO CONTEÚDO PARA NÃO FICAR SOB A NAVBAR */
    .main-content {
        margin-top: 80px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTRUTURA DO MENU SUPERIOR ---
# Usamos colunas dentro de um container para simular a navbar da imagem
st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
col_nav1, col_nav2, col_nav3, col_nav4, col_spacer = st.columns([1, 1.5, 1, 1, 4])

with col_nav1:
    if st.button("🏠 HOME", use_container_width=True):
        st.rerun()

with col_nav2:
    if st.button("📍 BOM JESUS DA PENHA", use_container_width=True):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")

with col_nav3:
    st.button("🏢 CIDADE X", disabled=True, use_container_width=True)

with col_nav4:
    st.button("📊 GERAL", disabled=True, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- CONTEÚDO CENTRALIZADO ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1.2, 1])

with c2:
    # Tenta carregar o logotipo branco para combinar com o fundo dark
    if os.path.exists("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg", use_container_width=True)
    elif os.path.exists("LOGOTIPO IG2P - OFICIAL.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL.jpg", use_container_width=True)
    
    st.markdown("<h1 style='text-align: center; color: white; margin-top: 20px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>IG2P - Inteligência em Gestão Pública</p>", unsafe_allow_html=True)
    
    st.divider()
    
    st.info("💡 Bem-vindo! Utilize o menu superior para acessar os dashboards dos municípios.")

st.markdown('</div>', unsafe_allow_html=True)