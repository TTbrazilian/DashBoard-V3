import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 2. CSS PARA CENTRALIZAÇÃO TOTAL E LOGO FIXO ---
st.markdown("""
    <style>
    /* 1. Limpeza de interface e remoção da sidebar */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* 2. Logo fixo no canto superior esquerdo */
    .logo-header {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 1000;
    }
    .logo-img {
        width: 180px; /* Tamanho reduzido conforme solicitado */
        pointer-events: none;
        user-select: none;
    }

    /* 3. Centralização Absoluta do Menu */
    .stApp {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    [data-testid="stVerticalBlock"] {
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        width: 100% !important;
    }

    .menu-container {
        width: 100%;
        max-width: 450px;
        margin: 0 auto;
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

# --- 3. LÓGICA DE IMAGEM POR MODO (ESCURO/CLARO) ---
# O Streamlit não tem um gatilho nativo simples para trocar variáveis Python por tema, 
# então usamos a lógica de arquivos baseada na preferência padrão do sistema.
logo_escuro = "Logos/LOGOTIPO IG2P - OFICIAL.jpg" # Versão preta para modo escuro
logo_claro = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.jpg" # Versão branca para modo claro

# Verifica qual arquivo carregar (Prioriza a versão preta conforme solicitado)
path_to_use = logo_escuro if os.path.exists(logo_escuro) else logo_claro

if os.path.exists(path_to_use):
    img_base64 = get_image_base64(path_to_use)
    st.markdown(
        f'<div class="logo-header"><img src="data:image/jpeg;base64,{img_base64}" class="logo-img"></div>',
        unsafe_allow_html=True
    )

# --- 4. CONTEÚDO COMPLETAMENTE CENTRALIZADO ---
# Usamos colunas apenas para criar um container centralizado e responsivo
col_l, col_c, col_r = st.columns([1, 2, 1])

with col_c:
    st.markdown("<div class='menu-container'>", unsafe_allow_html=True)
    
    # Título centralizado
    st.markdown("<h1 style='color: white; font-weight: 400; font-size: 32px; margin-bottom: 10px;'>Inteligência em Gestão</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ea0a5; margin-bottom: 40px;'>Portal de Seleção de Municípios</p>", unsafe_allow_html=True)
    
    # Botões de navegação
    if st.button("🏙️ Bom Jesus da Penha"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    if st.button("🏢 Município 2"):
        pass
        
    if st.button("🏢 Município 3"):
        pass
        
    st.markdown("<hr style='border-top: 1px solid #333; margin: 30px 0;'>", unsafe_allow_html=True)
    
    # Bloco informativo azul centralizado
    st.markdown("""
        <div style='background-color: #16263a; padding: 18px; border-radius: 8px; border-left: 5px solid #2196F3; text-align: center;'>
            <p style='color: #90CAF9; margin: 0; font-size: 14px;'>Utilize os botões acima para selecionar o painel desejado.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)