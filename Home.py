import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira linha do script) ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# --- 2. O DESIGN DO MENU (COPIE ESTE BLOCO) ---
st.markdown("""
    <style>
    /* Remove a navegação automática e o cabeçalho padrão */
    [data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stDeployButton {display:none;}

    /* COR DE FUNDO DA SIDEBAR (DARK) */
    [data-testid="stSidebar"] {
        background-color: #1a1c24 !important;
    }

    /* ESTILO BASE DOS BOTÕES (TEXTO CINZA, SEM BORDA) */
    div.stButton > button {
        background-color: transparent !important;
        color: #9ea0a5 !important;
        border: none !important;
        text-align: left !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        width: 100% !important;
        display: block !important;
        transition: background-color 0.3s ease !important;
    }

    /* ESTILO CÁPSULA - ITEM SELECIONADO (IGUAL À FOTO) */
    /* Usamos a chave 'nav_active' para identificar o botão que deve estar aceso */
    div.stButton > button[key="nav_home"] {
        background-color: #3d3f4b !important; /* Cinza azulado da foto */
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* EFEITO HOVER - ESCURECER AO PASSAR O MOUSE */
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
    }

    /* Hover específico para o botão que já está preenchido (fica mais escuro) */
    div.stButton > button[key="nav_home"]:hover {
        background-color: #2e303a !important;
    }

    /* Remove o espaço excessivo no topo da sidebar */
    .st-emotion-cache-16idsys { padding-top: 3rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ESTRUTURA DOS BOTÕES NA SIDEBAR ---
with st.sidebar:
    # Botão Home (Ativo na Home Page)
    if st.button("Home", key="nav_home"):
        st.rerun()
    
    # Botão Município (Texto simples, sem a cápsula)
    if st.button("Bom Jesus da Penha", key="nav_bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")

# --- DAQUI PARA BAIXO SEGUE O SEU CONTEÚDO ORIGINAL ---