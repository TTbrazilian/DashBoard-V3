import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide")

# --- CSS RADICAL PARA FIXAR NO TOPO ABSOLUTO ---
st.markdown("""
    <style>
    /* 1. ZERA TODO O ESPAÇAMENTO DO STREAMLIT */
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stAppViewContainer"] {padding-top: 0px !important;}
    .main .block-container {padding-top: 0px !important; padding-left: 0px !important; padding-right: 0px !important;}
    
    /* 2. ESCONDE SIDEBAR E ELEMENTOS PADRÃO */
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* 3. A FAIXA DO TOPO (ESTILO E-COMMERCE) */
    .nav-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        background-color: #252525; /* A cor cinza escuro do topo */
        z-index: 999999;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #333;
    }

    /* 4. ESTILIZAÇÃO DOS BOTÕES PARA ENCAIXAREM NA FAIXA */
    div.stButton > button {
        background-color: transparent !important;
        color: #e0e0e0 !important;
        border: none !important;
        height: 60px !important;
        margin: 0 !important;
        border-radius: 0px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: 0.2s;
    }

    div.stButton > button:hover {
        background-color: #333333 !important;
        color: #00CC96 !important;
    }

    /* 5. AJUSTE DO CONTEÚDO PARA NÃO FICAR ESCONDIDO */
    .content-area {
        margin-top: 100px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTRUTURA DA NAVBAR ---
# Criamos o container que o CSS vai "pegar" e jogar para o topo
st.markdown('<div class="nav-wrapper">', unsafe_allow_html=True)

# Definimos colunas com larguras menores para os botões ficarem próximos
# O primeiro número (0.2) é um recuo para a esquerda
c_left, c1, c2, c3, c4, c5, c_spacer = st.columns([0.2, 0.6, 1.3, 0.8, 0.7, 0.8, 4])

with c1:
    if st.button("🏠 Home", key="home"):
        st.rerun()
with c2:
    if st.button("📍 Bom Jesus da Penha", key="bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
with c3:
    st.button("🏢 Cidade X", disabled=True)
with c4:
    st.button("📊 Geral", disabled=True)
with c5:
    st.button("☰ Cidades")

st.markdown('</div>', unsafe_allow_html=True)

# --- ÁREA DO CONTEÚDO ---
st.markdown('<div class="content-area">', unsafe_allow_html=True)

col_c1, col_c2, col_c3 = st.columns([1, 2, 1])

with col_c2:
    # Logotipo
    if os.path.exists("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg", use_container_width=True)
    elif os.path.exists("LOGOTIPO IG2P - OFICIAL.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL.jpg", use_container_width=True)
    
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>IG2P - Inteligência em Gestão Pública</p>", unsafe_allow_html=True)
    
    st.divider()
    st.info("Utilize o menu superior para escolher o município e visualizar os dados.")

st.markdown('</div>', unsafe_allow_html=True)