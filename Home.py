import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Portal de Gestão", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CSS PARA LIMPAR A SIDEBAR E MANTER O CONTROLE ---
st.markdown("""
    <style>
    /* Esconde o cabeçalho nativo mas mantém o botão de fechar/abrir a sidebar */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* ESCONDE A LISTA AUTOMÁTICA DE ARQUIVOS (Links que o Streamlit gera) */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Estilo da Sidebar (Fundo escuro conforme as fotos) */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
    }

    /* Remove o botão de Deploy e lixos visuais */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* Espaçamento para o conteúdo não colar no topo */
    .main .block-container {
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATERAL (SIDEBAR) CUSTOMIZADO ---
with st.sidebar:
    # Espaçador inicial
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botão Home (Sempre no topo, conforme pedido)
    if st.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.rerun()
    
    st.markdown("---")
    
    # Seção escalável de Municípios
    # Usar o expander permite adicionar dezenas de nomes sem poluir o visual
    with st.expander("📍 Municípios", expanded=True):
        if st.button("🏙️ Bom Jesus da Penha", use_container_width=True, key="nav_bj"):
            st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
        
        # Futuros municípios entram aqui seguindo o mesmo padrão:
        # if st.button("🏙️ Nome do Municipio", use_container_width=True):
        #     st.switch_page("pages/2_Nome_Do_Arquivo.py")
        
        st.button("🏢 Município X (Em breve)", disabled=True, use_container_width=True)

# --- 4. CONTEÚDO CENTRAL DA HOME ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Lógica do Logotipo (Branco ou Original)
    logo_path = "LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
    if not os.path.exists(logo_path):
        logo_path = "LOGOTIPO IG2P - OFICIAL.jpg"
    
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>IG2P - Inteligência em Gestão Pública</p>", unsafe_allow_html=True)
    
    st.divider()
    st.info("Utilize o menu lateral para selecionar o município e visualizar os dados.")