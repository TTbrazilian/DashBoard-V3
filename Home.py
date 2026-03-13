import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="IG2P - Portal de Gestão", layout="wide", initial_sidebar_state="expanded")

# --- CSS PARA ESTILIZAR O CONTEÚDO ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Tira o espaço branco do topo já que não tem mais menu superior */
    .main .block-container {
        padding-top: 2rem !important;
    }

    /* Estilização básica da Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("📂 Navegação")
    
    # Opção Home
    if st.button("🏠 Home", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    # Submenu Municípios usando um expander para organizar
    with st.expander("📍 Municípios", expanded=True):
        if st.button("🏙️ Bom Jesus da Penha", use_container_width=True):
            st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
        
        # Adicione novos municípios aqui conforme necessário
        st.button("🏢 Município X (Em breve)", disabled=True, use_container_width=True)

# --- CONTEÚDO CENTRAL DA HOME ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Lógica do Logotipo
    logo_path = "LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
    if not os.path.exists(logo_path):
        logo_path = "LOGOTIPO IG2P - OFICIAL.jpg"
    
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.title("IG2P")

    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Inteligência em Gestão Pública</p>", unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    ### 👋 Bem-vindo ao Portal IG2P
    Utilize o **Menu Lateral** à esquerda para navegar:
    1. Clique em **Municípios** para expandir a lista.
    2. Selecione a cidade desejada para abrir o Dashboard completo.
    """)
    
    st.info("Os dados são atualizados periodicamente conforme os registros oficiais.")

# --- PRÓXIMO PASSO ---
# Agora que a Home está estável com o menu lateral, vamos voltar no dashboard?
# Qual gráfico de barras você quer que eu recupere lá? 
# O "Top 10 Investimentos" ou o "Comparativo Orçado x Saldo"?