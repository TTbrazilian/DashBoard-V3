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

# --- 2. CSS PARA CENTRALIZAÇÃO ABSOLUTA ---
st.markdown("""
    <style>
    /* Limpeza de interface */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* Cursor de botão no Selectbox e trava de escrita */
    div[data-baseweb="select"] { cursor: pointer !important; }
    div[data-baseweb="select"] input { caret-color: transparent !important; cursor: pointer !important; }

    /* Identidade Canto Superior Esquerdo */
    .brand-container {
        position: fixed;
        top: 30px;
        left: 30px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    .logo-img { width: 150px; pointer-events: none; }
    .brand-text { color: white; font-size: 16px; margin-top: 5px; }

    /* Forçar centralização de todos os blocos do Streamlit */
    [data-testid="stVerticalBlock"] {
        align-items: center !important;
        gap: 0rem !important;
    }

    /* Container principal centralizado */
    .main-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        max-width: 550px; /* Largura ideal para os elementos */
        margin: 0 auto;
        padding-top: 80px;
    }

    /* Estilização do Selectbox centralizado */
    div[data-testid="stSelectbox"] {
        width: 100% !important;
        max-width: 450px !important;
        margin-bottom: 25px !important;
    }

    /* Caixa azul informativa centralizada */
    .info-banner {
        background-color: #16263a;
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 5px solid #2196F3;
        text-align: center;
        width: 100%;
        max-width: 550px;
        margin-bottom: 20px;
    }
    .info-text { color: #90CAF9; margin: 0; font-size: 14px; font-weight: 500; }

    /* Estilo e centralização dos Botões */
    div.stButton {
        width: 100%;
        display: flex;
        justify-content: center;
    }
    div.stButton > button {
        background-color: #3d3f4b !important;
        color: white !important;
        border: none !important;
        padding: 14px 20px !important;
        font-size: 16px !important;
        width: 100% !important; 
        max-width: 450px; /* Mesma largura do selectbox para simetria */
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    div.stButton > button:hover { background-color: #4e515f !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGOTIPO ---
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

# --- 4. CONTEÚDO CENTRALIZADO ---
# Criamos uma div única para envolver todo o conteúdo e garantir o centro
st.markdown('<div class="main-content">', unsafe_allow_html=True)

setor = st.selectbox(
    "Selecione o Setor",
    ["Saúde", "Educação"],
    index=None,
    placeholder="Clique para escolher...",
)

if setor:
    # Texto da caixa azul conforme solicitado
    texto_caixa = f"{setor}: Selecione o municipio abaixo"
    
    st.markdown(f"""
        <div class="info-banner">
            <p class="info-text">{texto_caixa}</p>
        </div>
    """, unsafe_allow_html=True)

    if setor == "Saúde":
        if st.button("🏙️ Bom Jesus da Penha"):
            st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
        
        if st.button("🏢 Município Saúde 2"):
            pass

    elif setor == "Educação":
        if st.button("🏢 Município Educação A"):
            pass
        if st.button("🏢 Município Educação B"):
            pass

st.markdown('</div>', unsafe_allow_html=True)