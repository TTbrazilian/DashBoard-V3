import streamlit as st
import os

# --- 1. CONFIGURAÇÃO INICIAL (DEVE SER A PRIMEIRA LINHA) ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide")

# --- 2. CSS "KILLER" PARA COLAR NO TOPO ABSOLUTO ---
st.markdown("""
    <style>
    /* Remove o cabeçalho branco/transparente nativo do Streamlit */
    [data-testid="stHeader"] {
        display: none !important;
    }

    /* Zera todas as margens e paddings do container principal */
    .main .block-container {
        padding-top: 0px !important;
        padding-left: 0px !important;
        padding-right: 0px !important;
        margin-top: 0px !important;
    }

    /* Esconde a sidebar e rodapé */
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* A BARRA DE NAVEGAÇÃO REAL (COLADA NO TOPO 0) */
    .nav-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 55px;
        background-color: #252525; /* Cinza escuro da sua imagem exemplo */
        z-index: 999999;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #333;
        padding-left: 20px;
    }

    /* BOTÕES ESTILO MENU DE CATEGORIAS */
    div.stButton > button {
        background-color: transparent !important;
        color: #e0e0e0 !important;
        border: none !important;
        height: 55px !important;
        margin: 0px !important;
        padding: 0px 25px !important;
        border-radius: 0px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: 0.3s ease;
    }

    div.stButton > button:hover {
        background-color: #333333 !important;
        color: #00CC96 !important;
    }

    /* ESPAÇADOR PARA O CONTEÚDO NÃO FICAR POR BAIXO DA BARRA */
    .content-spacer {
        margin-top: 80px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ESTRUTURA DA NAVBAR ---
# Criamos a div pai da navbar
st.markdown('<div class="nav-container">', unsafe_allow_html=True)

# Usamos colunas para posicionar os botões dentro da div
# Ajuste as proporções para os botões ficarem colados à esquerda
c1, c2, c3, c4, c5, c_expander = st.columns([0.6, 1.4, 0.8, 0.8, 0.8, 5])

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

# --- 4. ÁREA DE CONTEÚDO ---
st.markdown('<div class="content-spacer">', unsafe_allow_html=True)

col_main1, col_main2, col_main3 = st.columns([1, 2, 1])

with col_main2:
    # Lógica do Logotipo
    logo_path = "LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
    if not os.path.exists(logo_path):
        logo_path = "LOGOTIPO IG2P - OFICIAL.jpg"
    
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    
    st.markdown("<h1 style='text-align: center; margin-top: 30px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #777;'>IG2P - Inteligência em Gestão Pública</p>", unsafe_allow_html=True)
    
    st.divider()
    st.info("Utilize o menu superior para escolher o município e visualizar os dados.")

st.markdown('</div>', unsafe_allow_html=True)