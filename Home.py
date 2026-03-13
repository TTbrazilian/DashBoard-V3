import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide")

# --- 2. CSS DEFINITIVO (ESTILO E-COMMERCE REAL) ---
st.markdown("""
    <style>
    /* Esconde cabeçalho e lixo do Streamlit */
    [data-testid="stHeader"], .stDeployButton {display: none !important;}
    [data-testid="stAppViewContainer"] {padding-top: 0px !important;}
    .main .block-container {padding: 0px !important;}

    /* A BARRA SUPERIOR CINZA ESCURO */
    .custom-nav {
        width: 100%;
        height: 60px;
        background-color: #262626;
        display: flex;
        align-items: center;
        padding: 0 50px;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 999999;
        border-bottom: 1px solid #333;
    }

    /* LINKS DO MENU */
    .nav-item {
        color: #e0e0e0;
        text-decoration: none;
        padding: 0 20px;
        font-size: 14px;
        font-family: sans-serif;
        font-weight: 500;
        height: 60px;
        display: flex;
        align-items: center;
        transition: 0.3s;
        cursor: pointer;
        border: none;
        background: none;
        white-space: nowrap; /* Impede o texto de quebrar linha */
    }

    .nav-item:hover {
        background-color: #333333;
        color: #00CC96;
    }

    /* AJUSTE DO CONTEÚDO PARA BAIXO DA BARRA */
    .hero-section {
        margin-top: 120px;
        text-align: center;
        padding: 20px;
    }
    
    [data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA DE NAVEGAÇÃO EM HTML ---
# Como o Streamlit não lida bem com cliques em HTML puro para mudar de página, 
# mantemos os botões mas dentro de uma estrutura que não quebra.

st.markdown('<div class="custom-nav">', unsafe_allow_html=True)

# Criamos uma linha horizontal de botões sem usar as colunas travadas do Streamlit
c_menu = st.container()
with c_menu:
    cols = st.columns([0.5, 1.2, 0.8, 0.7, 0.7, 5]) # Colunas bem distribuídas
    with cols[0]:
        if st.button("🏠 Home", key="h"): st.rerun()
    with cols[1]:
        if st.button("📍 Bom Jesus da Penha", key="bj"): st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    with cols[2]:
        st.button("🏢 Cidade X", disabled=True)
    with cols[3]:
        st.button("📊 Geral", disabled=True)
    with cols[4]:
        st.button("☰ Cidades")

st.markdown('</div>', unsafe_allow_html=True)

# --- 4. CONTEÚDO CENTRAL ---
st.markdown('<div class="hero-section">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg", width=450)
    elif os.path.exists("LOGOTIPO IG2P - OFICIAL.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL.jpg", width=450)
    
    st.markdown("<h1 style='color: white; font-size: 42px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; font-size: 18px;'>IG2P - Inteligência em Gestão Pública</p>", unsafe_allow_html=True)
    st.divider()
    st.info("Utilize o menu superior para escolher o município.")

st.markdown('</div>', unsafe_allow_html=True)