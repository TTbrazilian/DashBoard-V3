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

# --- MENU SUPERIOR ---
with st.container():
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        # Usamos um selectbox que parece um botão de menu
        municipio_selecionado = st.selectbox(
            "📍 Selecionar Município",
            ["Home", "Bom Jesus da Penha"],
            index=0,
            key="nav_menu"
        )

# Redirecionamento lógico
if municipio_selecionado == "Bom Jesus da Penha":
    st.switch_page("pages/1_Bom_Jesus_da_Penha.py")

# --- CONTEÚDO DA HOME ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("LOGOTIPO IG2P - OFICIAL.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL.jpg", use_container_width=True)
    else:
        st.title("IG2P")

st.markdown("<h1 style='text-align: center;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
st.divider()
st.info("Utilize o menu superior para escolher o município e visualizar os dados.")