import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Inteligência em Gestão", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Começa recolhida para focar no centro
)

def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 2. CSS PARA LAYOUT CENTRALIZADO E LOGO FIXO ---
st.markdown("""
    <style>
    /* Remove elementos nativos */
    header[data-testid="stHeader"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    [data-testid="stSidebarNav"] { display: none !important; }

    /* Centralização do conteúdo */
    .main .block-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 2rem;
    }

    /* Estilo do Logo como Link */
    .logo-link {
        transition: transform 0.3s ease;
        cursor: pointer;
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .logo-link:hover {
        transform: scale(1.02);
    }
    .logo-img {
        width: 400px;
        pointer-events: auto;
    }

    /* Menu Centralizado */
    .menu-container {
        width: 100%;
        max-width: 500px;
        text-align: center;
    }

    /* Botões customizados estilo dashboard */
    div.stButton > button {
        background-color: #3d3f4b !important;
        color: white !important;
        border: none !important;
        padding: 15px 20px !important;
        font-size: 18px !important;
        width: 100% !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
        transition: background 0.3s ease !important;
    }
    div.stButton > button:hover {
        background-color: #4e515f !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RENDERIZAÇÃO DO LOGO (BOTÃO HOME) ---
logo_path = "Logos/LOGOTIPO IG2P - OFICIAL.jpg"
if not os.path.exists(logo_path):
    logo_path = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"

if os.path.exists(logo_path):
    img_base64 = get_image_base64(logo_path)
    # O link "/" faz voltar para a Home Page
    st.markdown(
        f'<a href="/" target="_self" class="logo-link"><img src="data:image/jpeg;base64,{img_base64}" class="logo-img"></a>',
        unsafe_allow_html=True
    )

st.markdown("<h2 style='text-align: center; color: white; font-weight: 400;'>Inteligência em Gestão</h2>", unsafe_allow_html=True)
st.markdown("<hr style='width: 400px; margin: 20px auto; border-top: 1px solid #333;'>", unsafe_allow_html=True)

# --- 4. MENU DE NAVEGAÇÃO CENTRAL ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<div class='menu-container'>", unsafe_allow_html=True)
    
    if st.button("🏙️ Bom Jesus da Penha"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    if st.button("🏢 Município 2"):
        pass
        
    if st.button("🏢 Município 3"):
        pass
        
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
        <div style='background-color: #16263a; padding: 20px; border-radius: 8px; border-left: 5px solid #2196F3; margin-top: 30px;'>
            <p style='color: #90CAF9; margin: 0; font-size: 15px; text-align: center;'>Selecione um município para acessar o painel de dados.</p>
        </div>
    """, unsafe_allow_html=True)

# --- 5. INSTRUÇÃO PARA AS OUTRAS PÁGINAS ---
# Para que o logo apareça no topo da sidebar nas outras páginas, 
# você deve colar o código do LOGO no início de cada arquivo .py em /pages.