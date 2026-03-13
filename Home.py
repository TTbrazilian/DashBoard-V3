import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide")

# --- 2. CSS DE FORÇA BRUTA PARA O TOPO ABSOLUTO ---
st.markdown("""
    <style>
    /* Remove o cabeçalho nativo e força o container a subir */
    [data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Zera o padding do container principal e da aplicação */
    .stApp {
        margin-top: -60px !important;
    }
    
    .main .block-container {
        padding-top: 0px !important;
        padding-left: 0px !important;
        padding-right: 0px !important;
    }

    /* BARRA DE NAVEGAÇÃO (NAVBAR) FIXADA NO TOPO 0 */
    .nav-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 55px;
        background-color: #262626 !important; /* Cinza escuro da imagem */
        z-index: 9999999;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #333;
    }

    /* BOTÕES DENTRO DA NAVBAR */
    div.stButton > button {
        background-color: transparent !important;
        color: #e0e0e0 !important;
        border: none !important;
        height: 55px !important;
        margin: 0px !important;
        padding: 0px 30px !important;
        border-radius: 0px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    div.stButton > button:hover {
        background-color: #333333 !important;
        color: #00CC96 !important;
    }

    /* ESCONDE SIDEBAR NA HOME */
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}

    /* CONTEÚDO PARA NÃO FICAR EMBAIXO DA BARRA */
    .content-body {
        margin-top: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. NAVBAR ---
# Criando a div que o CSS vai forçar para o topo
st.markdown('<div class="nav-wrapper">', unsafe_allow_html=True)

# Colunas para alinhar os botões à esquerda
c1, c2, c3, c4, c5, c_spacer = st.columns([0.6, 1.4, 0.8, 0.8, 0.8, 5])

with c1:
    if st.button("🏠 Home"):
        st.rerun()
with c2:
    if st.button("📍 Bom Jesus da Penha"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
with c3:
    st.button("🏢 Cidade X", disabled=True)
with c4:
    st.button("📊 Geral", disabled=True)
with c5:
    st.button("☰ Cidades")

st.markdown('</div>', unsafe_allow_html=True)

# --- 4. CONTEÚDO CENTRAL ---
st.markdown('<div class="content-body">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg", use_container_width=True)
    elif os.path.exists("LOGOTIPO IG2P - OFICIAL.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL.jpg", use_container_width=True)
    
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.divider()
    st.info("Utilize o menu superior para escolher o município.")

st.markdown('</div>', unsafe_allow_html=True)