import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Portal de Gestão", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CSS PARA PADRONIZAÇÃO DO MENU LATERAL (SIDEBAR) ---
st.markdown("""
    <style>
    /* Remove o cabeçalho branco e lixo visual nativo */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    
    /* COR DE FUNDO DA SIDEBAR (DARK DESIGN) */
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

    /* ITEM SELECIONADO / ATIVO (Destaque conforme imagem de referência) */
    div.stButton > button[key="nav_home"] {
        background-color: #3d3f4b !important; /* Cor da cápsula ativa */
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* EFEITO AO PASSAR O MOUSE (HOVER) */
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
    }
    
    div.stButton > button[key="nav_home"]:hover {
        background-color: #2e303a !important; /* Escurecimento leve no hover */
    }

    /* Ajuste de respiro no topo da sidebar */
    .st-emotion-cache-16idsys { padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ESTRUTURA DE NAVEGAÇÃO PADRONIZADA ---
with st.sidebar:
    # Espaçador superior
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botão Home (Marcado como ativo na Home Page)
    if st.button("Home", key="nav_home"):
        st.rerun()
    
    # Botão do Município (Estilo texto simples quando não selecionado)
    if st.button("Bom Jesus da Penha", key="nav_bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    # Linha divisória fina para separar navegação de futuros filtros
    st.markdown("---")

# --- 4. CONTEÚDO CENTRAL DA HOME ---
# Centralizando o conteúdo principal conforme o layout das imagens
col_l, col_c, col_r = st.columns([1, 2, 1])

with col_c:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 50px; margin-bottom: 0;'>IG2P</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-weight: 400; margin-top: 0;'>Portal de Gestão de Recursos</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Inteligência em Gestão Pública</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # Caixa de orientação estilizada conforme as imagens enviadas
    st.info("Utilize o menu lateral para selecionar o município e visualizar os dados consolidados.")