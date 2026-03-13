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

# --- 2. CSS PARA DESIGN REFINADO ---
st.markdown("""
    <style>
    /* 1. Limpeza de interface */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* 2. Bloco de Identidade no Canto Superior Esquerdo */
    .brand-container {
        position: fixed;
        top: 30px;
        left: 30px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    .logo-img {
        width: 160px; /* Proporção ajustada */
        pointer-events: none;
        user-select: none;
        margin-bottom: 5px;
    }
    .brand-text {
        color: white;
        font-size: 18px; /* Fonte ajustada conforme solicitado */
        font-weight: 400;
        margin: 0;
        letter-spacing: 0.5px;
    }

    /* 3. Centralização Absoluta do Menu de Botões */
    .stApp {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    [data-testid="stVerticalBlock"] {
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }

    .menu-container {
        width: 100%;
        max-width: 420px;
        margin: 0 auto;
        text-align: center;
    }

    /* Botões centralizados e estilizados */
    div.stButton > button {
        background-color: #3d3f4b !important;
        color: white !important;
        border: none !important;
        padding: 14px 20px !important;
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

# --- 3. RENDERIZAÇÃO DA IDENTIDADE (LOGO ESCURO + TEXTO) ---
# Forçando a imagem escura conforme solicitado
logo_path = "Logos/LOGOTIPO IG2P - OFICIAL.jpg" 

if os.path.exists(logo_path):
    img_base64 = get_image_base64(logo_path)
    st.markdown(
        f'''
        <div class="brand-container">
            <img src="data:image/jpeg;base64,{img_base64}" class="logo-img">
            <p class="brand-text">Inteligência em Gestão</p>
        </div>
        ''',
        unsafe_allow_html=True
    )

# --- 4. CONTEÚDO DO MENU CENTRALIZADO ---
col_l, col_c, col_r = st.columns([1, 2, 1])

with col_c:
    st.markdown("<div class='menu-container'>", unsafe_allow_html=True)
    
    # Subtítulo do portal
    st.markdown("<p style='color: #9ea0a5; font-size: 14px; margin-bottom: 30px;'>Portal de Seleção de Municípios</p>", unsafe_allow_html=True)
    
    # Botões de navegação
    if st.button("🏙️ Bom Jesus da Penha"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    if st.button("🏢 Município 2"):
        pass
        
    if st.button("🏢 Município 3"):
        pass
        
    st.markdown("<hr style='border-top: 1px solid #333; margin: 30px 0;'>", unsafe_allow_html=True)
    
    # Bloco informativo centralizado
    st.markdown("""
        <div style='background-color: #16263a; padding: 18px; border-radius: 8px; border-left: 5px solid #2196F3;'>
            <p style='color: #90CAF9; margin: 0; font-size: 14px;'>Utilize os botões acima para acessar os indicadores.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)