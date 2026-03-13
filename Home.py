import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide")

# --- CSS PARA FIXAR O MENU NA FAIXA DO TOPO ---
st.markdown("""
    <style>
    /* Remove padding superior padrão do Streamlit e esconde elementos inúteis */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stHeader"] {display: none;}
    
    /* REMOVE A SIDEBAR NA HOME */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stSidebarNav"] {display: none;}

    /* A FAIXA DO TOPO (NAVBAR) */
    .top-nav-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 70px; /* Altura da faixa cinza */
        background-color: #252525; /* Cor cinza escura da imagem exemplo */
        display: flex;
        align-items: center;
        padding-left: 50px;
        z-index: 999999;
        border-bottom: 1px solid #333;
    }

    /* ESTILO DOS BOTÕES PARA ENCAIXAREM NA FAIXA */
    div.stButton > button {
        background-color: transparent !important;
        color: #e0e0e0 !important;
        border: none !important;
        height: 70px !important; /* Mesma altura da faixa para alinhar */
        margin: 0 !important;
        border-radius: 0px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: 0.2s;
    }

    div.stButton > button:hover {
        background-color: #333333 !important;
        color: #00CC96 !important;
    }

    /* AJUSTE PARA O CONTEÚDO NÃO SUBIR PARA TRÁS DA BARRA */
    .main-content {
        margin-top: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVBAR NO TOPO ---
# Criamos a div da barra e usamos colunas do Streamlit dentro dela
st.markdown('<div class="top-nav-bar">', unsafe_allow_html=True)

# As colunas precisam ser ajustadas para ficarem juntas à esquerda
col_nav1, col_nav2, col_nav3, col_nav4, col_nav5, col_spacer = st.columns([0.6, 1.4, 1, 0.8, 1, 4])

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
    st.button("☰ Cidades", key="menu_cidades")

st.markdown('</div>', unsafe_allow_html=True)

# --- CONTEÚDO CENTRALIZADO ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    # Logotipo
    if os.path.exists("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg", use_container_width=True)
    elif os.path.exists("LOGOTIPO IG2P - OFICIAL.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL.jpg", use_container_width=True)
    
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>IG2P - Inteligência em Gestão Pública</p>", unsafe_allow_html=True)
    
    st.divider()
    st.info("Utilize o menu superior para escolher o município e visualizar os dados.")

st.markdown('</div>', unsafe_allow_html=True)