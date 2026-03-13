import streamlit as st
import os
from PIL import Image

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="IG2P - Portal de Gestão", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CSS PADRONIZADO (IDÊNTICO AO DASHBOARD) ---
st.markdown("""
    <style>
    /* Remove elementos nativos */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* FUNDO DA SIDEBAR DARK */
    [data-testid="stSidebar"] {
        background-color: #1a1c24 !important;
    }

    /* ESTILO DOS BOTÕES EM CÁPSULA */
    div.stButton > button {
        background-color: transparent !important;
        color: #9ea0a5 !important;
        border: none !important;
        text-align: left !important;
        padding: 10px 18px !important;
        font-size: 15px !important;
        width: 100% !important;
        display: block !important;
        transition: all 0.3s ease !important;
    }

    /* BOTÃO ATIVO (HOME) */
    div.stButton > button[key="nav_home"] {
        background-color: #3d3f4b !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    /* EFEITO HOVER */
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
    }
    
    div.stButton > button[key="nav_home"]:hover {
        background-color: #2e303a !important; 
    }

    /* Respiro no topo da sidebar */
    .st-emotion-cache-16idsys { padding-top: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATERAL (SIDEBAR) - ESTRUTURA REPLICADA ---
with st.sidebar:
    # Botão Home (Ativo na Home Page)
    if st.button("🏠 Home", key="nav_home"):
        st.rerun()
    
    # Navegação de Municípios
    if st.button("🏙️ Bom Jesus da Penha", key="nav_bj"):
        st.switch_page("pages/1_Bom_Jesus_da_Penha.py")
    
    # Municípios Adicionais (Placeholders)
    if st.button("🏢 Município 2", key="nav_m2"):
        pass  # Adicionar switch_page quando a página existir
        
    if st.button("🏢 Município 3", key="nav_m3"):
        pass

    st.markdown("---")
    
    # Na Home, o cabeçalho de Filtros é removido conforme solicitado,
    # mantendo apenas a identidade visual da sidebar.
    st.info("Selecione um município acima para visualizar os dados.")

# --- 4. CONTEÚDO CENTRAL (IGUAL À HOME PADRÃO) ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Lógica de Logotipo
    logo_path = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"
    if not os.path.exists(logo_path):
        logo_path = "Logos/LOGOTIPO IG2P - OFICIAL.jpg"

    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        st.image(img, width=450)
    
    st.markdown("""
        <div style='text-align: center; margin-top: 20px;'>
            <h2 style='font-weight: 400; color: #E0E0E0;'>Portal de Gestão de Recursos</h2>
            <hr style='border-top: 1px solid #333; width: 80%; margin: 20px auto;'>
            <div style='background-color: #16263a; padding: 15px; border-radius: 5px; border-left: 5px solid #2196F3;'>
                <p style='color: #90CAF9; margin: 0;'>Utilize o menu lateral para navegar entre os dashboards.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)