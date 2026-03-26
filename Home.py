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
    /* Limpeza total de interface */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stDeployButton { display:none; }
    footer { visibility: hidden; }

    /* Cursor de botão no Selectbox */
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

    /* CENTRALIZAÇÃO FORÇADA */
    .stApp { align-items: center !important; }
    
    [data-testid="stVerticalBlock"] {
        width: 100% !important;
        max-width: 350px !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    /* Ajuste do Selectbox */
    div[data-testid="stSelectbox"], div[data-testid="stSelectbox"] > div {
        width: 100% !important;
    }

    /* Caixa azul informativa */
    .info-banner {
        background-color: #16263a;
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 5px solid #2196F3;
        text-align: center;
        width: 100%;
        margin: 20px 0;
    }
    .info-text { color: #90CAF9; margin: 0; font-size: 14px; font-weight: 500; }

    /* --- AJUSTE DEFINITIVO DOS BOTÕES --- */
    /* Força o container do widget a ocupar toda a largura disponível (500px) */
    div[data-testid="stVerticalBlock"] > div:has(button) {
        width: 100% !important;
    }

    /* Estilização do botão em si */
    button[kind="secondary"], button[kind="primary"] {
        width: 100% !important;
        min-width: 100% !important;
        display: block !important;
        background-color: #3d3f4b !important;
        color: white !important;
        border: none !important;
        padding: 14px 20px !important;
        font-size: 16px !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }

    button:hover { 
        background-color: #4e515f !important; 
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGOTIPO (MODO ESCURO - BRANCO) ---
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
# Espaçador para descer o conteúdo
st.write("<br><br><br>", unsafe_allow_html=True)

# O Streamlit agora centraliza automaticamente tudo o que for colocado aqui
setor = st.selectbox(
    "Selecione o Setor",
    ["Saúde", "Educação"],
    index=None,
    placeholder="Clique para escolher...",
)

if setor:
    # Texto da caixa azul conforme solicitado
    texto_caixa = f"{setor}: Selecione o município abaixo"
    
    st.markdown(f"""
        <div class="info-banner">
            <p class="info-text">{texto_caixa}</p>
        </div>
    """, unsafe_allow_html=True)

    if setor == "Saúde":
       
        if st.button("Alpinópolis"):
            st.switch_page("pages/Alpinópolis_Saúde.py")

        if st.button("Bom Jesus da Penha"):
            st.switch_page("pages/Bom_Jesus_da_Penha_Saúde.py")

        if st.button("Cássia"):
            st.switch_page("pages/Cássia_Saúde.py")

        if st.button("Delfinópolis"):
            st.switch_page("pages/Delfinópolis_Saúde.py")
        
        if st.button("Itaú de Minas"):
            st.switch_page("pages/Itaú_de_Minas_Saúde.py")

    elif setor == "Educação":
        if st.button("Alpinópolis"):
            st.switch_page("pages/Alpinópolis_Educação.py")
            
        if st.button("Município Educação B"):
            pass