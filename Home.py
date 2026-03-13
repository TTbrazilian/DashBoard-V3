import streamlit as st
import os

st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide")

# --- CSS PARA MENU SUPERIOR E ESTILO ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    div[data-testid="stSidebarNav"] {display: none;} /* Esconde o menu lateral automático */
    
    /* Estilização dos botões para parecerem categorias de e-commerce */
    div.stButton > button {
        background-color: #1e1e1e;
        color: white;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    div.stButton > button:hover {
        border-color: #00CC96;
        color: #00CC96;
        background-color: #262730;
    }
    
    .top-nav {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        padding: 10px 0px;
        background-color: #0e1117;
        border-bottom: 1px solid #333;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MENU SUPERIOR (ESTILO CATEGORIAS) ---
with st.container():
    # Criamos colunas para os botões ficarem lado a lado (como na foto)
    # Adicione ou remova colunas conforme o número de municípios aumentar
    col1, col2, col3, col4, col5 = st.columns([1, 1.5, 1, 1, 1])
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.rerun() # Já estamos na Home

    with col2:
        if st.button("📍 Bom Jesus da Penha", use_container_width=True):
            st.switch_page("pages/1_Bom_Jesus_da_Penha.py")

    with col3:
        # Exemplo de como você adicionaria outro futuramente
        st.button("🏢 Município X", disabled=True, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- CONTEÚDO DA HOME ---
col1_c, col2_c, col3_c = st.columns([1, 2, 1])
with col2_c:
    if os.path.exists("LOGOTIPO IG2P - OFICIAL.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL.jpg", use_container_width=True)
    else:
        st.title("IG2P")

st.markdown("<h1 style='text-align: center;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
st.divider()
st.info("Utilize o menu superior para escolher o município e visualizar os dados.")