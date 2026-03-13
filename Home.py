import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Função para converter imagem para base64 (necessário para o HTML)
# Isso permite carregar a imagem direto do arquivo local
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 2. CSS DEFINITIVO: DESIGN IDÊNTICO + REMOÇÃO TOTAL DE INTERAÇÃO ---
st.markdown("""
    <style>
    /* 1. Limpeza de interface nativa */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* 2. Sidebar Dark (Idêntica ao Dashboard de Bom Jesus) */
    [data-testid="stSidebar"] {
        background-color: #1a1c24 !important;
    }

    /* 3. Estilo dos botões da Sidebar */
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

    /* Botão Home Ativo */
    div.stButton > button[key="nav_home"] {
        background-color: #3d3f4b !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
    }

    /* Ajuste de espaçamento da sidebar */
    .st-emotion-cache-16idsys { padding-top: 2rem !important; }

    /* Estilo do Logo em HTML para evitar botões de tela cheia */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-top: -50px; /* Posição de cabeçalho */
    }
    .logo-img {
        width: 380px;
        pointer-events: none; /* Impede qualquer interação ou "bolinha" */
        user-select: none;
    }
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
    # Lógica de busca do logo - PRIORIZA A VERSÃO OFICIAL COM FUNDO ESCURO
    logo_path = "Logos/LOGOTIPO IG2P - OFICIAL.jpg"
    # Fallback caso a versão oficial não exista
    if not os.path.exists(logo_path):
        logo_path = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"

    if os.path.exists(logo_path):
        # Renderização via HTML puro para não criar o botão de fullscreen
        img_base64 = get_image_base64(logo_path)
        st.markdown(
            f'<div class="logo-container"><img src="data:image/jpeg;base64,{img_base64}" class="logo-img"></div>',
            unsafe_allow_html=True
        )
    
    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='font-weight: 400; color: white; font-size: 28px; margin-top: 0px;'>Inteligência em Gestão</h1>
            <hr style='border-top: 1px solid #333; width: 100%; margin: 20px 0;'>
            <div style='background-color: #16263a; padding: 20px; border-radius: 8px; border-left: 5px solid #2196F3;'>
                <p style='color: #90CAF9; margin: 0; font-size: 16px;'>Utilize o menu lateral para selecionar o município.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)