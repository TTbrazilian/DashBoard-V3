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

    /* 2. Bloco de Identidade (Canto Superior Esquerdo) */
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
        width: 150px; 
        pointer-events: none;
        user-select: none;
    }
    .brand-text {
        color: white;
        font-size: 16px;
        font-weight: 400;
        margin-top: 5px;
    }

    /* 3. Banner Informativo Azul (Topo Centralizado) */
    .info-banner {
        background-color: #16263a;
        padding: 15px 30px;
        border-radius: 8px;
        border-left: 5px solid #2196F3;
        text-align: center;
        width: fit-content;
        margin: 20px auto 40px auto; 
    }
    .info-text {
        color: #90CAF9;
        margin: 0;
        font-size: 14px;
    }

    /* 4. Centralização do Menu de Botões com ajuste para baixo */
    .stApp {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    [data-testid="stVerticalBlock"] {
        align-items: center !important;
        justify-content: center !important;
        padding-top: 50px !important; /* Move o painel central um pouco para baixo */
    }

    .menu-container {
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
    }

    /* Estilo dos Botões */
    div.stButton > button {
        background-color: #3d3f4b !important;
        color: white !important;
        border: none !important;
        padding: 14px 20px !important;
        font-size: 16px !important;
        width: 100% !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #4e515f !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RENDERIZAÇÃO DA IDENTIDADE COM AS IMAGENS CORRETAS ---
# Referenciando os nomes de arquivos exatos solicitados
logo_path = "Logos/LOGOTIPO IG2P - OFICIAL.png" 

if not os.path.exists(logo_path):
    logo_path = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.png"

if os.path.exists(logo_path):
    img_base64 = get_image_base64(logo_path)
    st.markdown(
        f'''
        <div class="brand-container">
            <img src="data:image/png;base64,{img_base64}" class="logo-img">
            <p class="brand-text">Inteligência em Gestão</p>
        </div>
        ''',
        unsafe_allow_html=True
    )

# --- 4. BANNER AZUL NO TOPO CENTRALIZADO ---
st.markdown("""
    <div class="info-banner">
        <p class="info-text">Utilize os botões abaixo para acessar os indicadores.</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. MENU DE BOTÕES CENTRALIZADO ---
col_l, col_c, col_r = st.columns([1, 1.5, 1])

with col_c:
    st.markdown("<div class='menu-container'>", unsafe_allow_html=True)
    
    # Botões de navegação
    if st.button("🏙️ Bom Jesus da Penha"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    if st.button("🏢 Município 2"):
        pass
        
    if st.button("🏢 Município 3"):
        pass
        
    st.markdown("</div>", unsafe_allow_html=True)