import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide")

# --- CSS PARA COPIAR O LAYOUT DA SEGUNDA IMAGEM (TOP NAVBAR REAL) ---
st.markdown("""
    <style>
    /* Esconde elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* REMOVE A SIDEBAR E O ESPAÇAMENTO LATERAL NA HOME */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
    section[data-testid="stSidebar"] {width: 0px;}

    /* BARRA DE NAVEGAÇÃO SUPERIOR (ESTILO E-COMMERCE PROFISSIONAL) */
    .top-nav-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #252525; /* Cinza escuro da imagem */
        padding: 0px 40px;
        display: flex;
        align-items: center;
        z-index: 999999;
        height: 60px;
        border-bottom: 1px solid #333;
    }

    /* ESTILIZAÇÃO DOS BOTÕES DENTRO DA NAVBAR */
    div.stButton > button {
        background-color: transparent !important;
        color: #e0e0e0 !important;
        border: none !important;
        padding: 0px 20px !important;
        height: 60px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        border-radius: 0px !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* EFEITO DE HOVER IGUAL AO EXEMPLO */
    div.stButton > button:hover {
        background-color: #333333 !important;
        color: #00CC96 !important; /* Verde IG2P */
    }

    /* CONTEÚDO PRINCIPAL CENTRALIZADO */
    .main-body {
        margin-top: 100px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVBAR SUPERIOR (CONTAINER DE BOTÕES) ---
# Usamos colunas com espaçamento zero para os botões encostarem um no outro
with st.container():
    # Simulando a div da navbar via markdown para o estilo fixed
    st.markdown('<div class="top-nav-container">', unsafe_allow_html=True)
    
    # Criamos colunas para os botões (ajuste o número de colunas conforme necessário)
    c1, c2, c3, c4, c5, c_spacer = st.columns([1, 1.5, 1, 1, 1, 4])
    
    with c1:
        if st.button("🏠 Home", key="btn_home"):
            st.rerun()
    with c2:
        if st.button("📍 Bom Jesus da Penha", key="btn_bj"):
            st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    with c3:
        st.button("🏢 Município X", disabled=True)
    with c4:
        st.button("📊 Geral", disabled=True)
    with c5:
        # Botão especial simulando o "Categorias" do exemplo
        st.button("☰ Cidades", key="btn_cat")
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- CONTEÚDO CENTRAL DA PÁGINA ---
st.markdown('<div class="main-body">', unsafe_allow_html=True)

col_logo, col_text = st.columns([1, 1])

with st.container():
    st.write("") # Espaçador
    st.write("")
    
    # Exibição do Logotipo Branco (melhor para o tema dark)
    if os.path.exists("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg", width=400)
    else:
        st.image("LOGOTIPO IG2P - OFICIAL.jpg", width=400)

    st.markdown("<h1 style='text-align: center; margin-top: 30px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Selecione uma unidade federativa no menu superior para começar.</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # Box de aviso estilizado
    st.info("💡 Dica: O sistema é atualizado automaticamente com base nos dados do SIGP.")

st.markdown('</div>', unsafe_allow_html=True)