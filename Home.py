import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Esconde a sidebar na inicial
)

def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 2. CSS PARA POSICIONAMENTO E CENTRALIZAÇÃO ---
st.markdown("""
    <style>
    /* 1. Limpeza de interface e remoção da sidebar */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* 2. Logo fixo no canto superior esquerdo */
    .logo-header {
        position: absolute;
        top: -60px;
        left: -20px;
        z-index: 100;
    }
    .logo-img {
        width: 250px; /* Tamanho ajustado para o canto */
        pointer-events: none; /* Remove clique e ícone de tela cheia */
    }

    /* 3. Centralização total do Menu */
    .main .block-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 80vh; /* Centraliza verticalmente na tela */
    }

    .menu-container {
        width: 100%;
        max-width: 450px;
        text-align: center;
    }

    /* Estilo dos botões centralizados */
    div.stButton > button {
        background-color: #3d3f4b !important;
        color: white !important;
        border: none !important;
        padding: 15px 20px !important;
        font-size: 16px !important;
        width: 100% !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        background-color: #4e515f !important;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RENDERIZAÇÃO DO LOGO NO CANTO (SEM CLIQUE) ---
logo_path = "Logos/LOGOTIPO IG2P - OFICIAL.jpg" # Versão colorida
if not os.path.exists(logo_path):
    logo_path = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"

if os.path.exists(logo_path):
    img_base64 = get_image_base64(logo_path)
    # Renderizado apenas como imagem, sem a tag <a> de link
    st.markdown(
        f'<div class="logo-header"><img src="data:image/jpeg;base64,{img_base64}" class="logo-img"></div>',
        unsafe_allow_html=True
    )

# --- 4. MENU CENTRALIZADO ---
# Usando colunas para garantir o alinhamento no meio da página
col_l, col_c, col_r = st.columns([1, 1.5, 1])

with col_c:
    st.markdown("<div class='menu-container'>", unsafe_allow_html=True)
    
    # Título centralizado
    st.markdown("<h2 style='color: white; font-weight: 400; margin-bottom: 30px;'>Inteligência em Gestão</h2>", unsafe_allow_html=True)
    
    # Botões de navegação
    if st.button("🏙️ Bom Jesus da Penha"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    if st.button("🏢 Município 2"):
        pass
        
    if st.button("🏢 Município 3"):
        pass
        
    st.markdown("<hr style='border-top: 1px solid #333; margin: 30px 0;'>", unsafe_allow_html=True)
    
    # Bloco informativo azul
    st.markdown("""
        <div style='background-color: #16263a; padding: 18px; border-radius: 8px; border-left: 5px solid #2196F3;'>
            <p style='color: #90CAF9; margin: 0; font-size: 14px;'>Selecione um município para acessar os indicadores.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)