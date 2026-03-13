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

# --- 2. CSS PARA DESIGN E POSICIONAMENTO ---
st.markdown("""
    <style>
    /* Limpeza de interface */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

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
    .logo-img {
        width: 150px; 
        pointer-events: none;
    }
    .brand-text {
        color: white;
        font-size: 16px;
        margin-top: 5px;
    }

    /* Centralização do conteúdo */
    .stApp {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Estilização do seletor de setor no topo central */
    .stSelectbox {
        max-width: 300px;
        margin: 0 auto 20px auto;
    }

    /* Caixa azul informativa colada aos botões */
    .info-banner {
        background-color: #16263a;
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 5px solid #2196F3;
        text-align: center;
        width: 100%;
        margin-bottom: 15px;
    }
    .info-text {
        color: #90CAF9;
        margin: 0;
        font-size: 14px;
    }

    /* Botões dos municípios */
    div.stButton > button {
        background-color: #3d3f4b !important;
        color: white !important;
        border: none !important;
        padding: 14px 20px !important;
        font-size: 16px !important;
        width: 100% !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGOTIPO NO CANTO (MODO ESCURO) ---
# Usando a versão branca conforme solicitado para contraste
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

# --- 4. FLUXO DE NAVEGAÇÃO CENTRALIZADO ---
col_l, col_c, col_r = st.columns([1, 1.5, 1])

with col_c:
    st.write("<br><br>", unsafe_allow_html=True) # Ajuste fino de altura
    
    # 1º Passo: Seleção do Setor (Funciona como o botão solicitado)
    setor = st.selectbox(
        "Selecione o Setor",
        ["-", "Saúde", "Educação"],
        index=0,
        help="Escolha uma área para visualizar os municípios disponíveis."
    )

    # 2º Passo: Exibição condicional baseada na escolha
    if setor != "-":
        # Caixa azul logo acima dos botões
        st.markdown(f"""
            <div class="info-banner">
                <p class="info-text">Indicadores de {setor}: Selecione um município abaixo.</p>
            </div>
        """, unsafe_allow_html=True)

        if setor == "Saúde":
            # Botão Bom Jesus aparece apenas em Saúde
            if st.button("🏙️ Bom Jesus da Penha"):
                st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
            
            if st.button("🏢 Município Saúde 2"):
                pass

        elif setor == "Educação":
            # Lista específica para Educação
            if st.button("🏢 Município Educação A"):
                pass
            if st.button("🏢 Município Educação B"):
                pass
    else:
        # Mensagem neutra antes da seleção
        st.markdown("""
            <div style='text-align: center; color: #9ea0a5; margin-top: 20px;'>
                Aguardando seleção de setor...
            </div>
        """, unsafe_allow_html=True)