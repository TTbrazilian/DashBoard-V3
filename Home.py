import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CAMINHO DO LOGO ---
# Altere para o nome do arquivo que deseja usar (BRANCO ou OFICIAL)
LOGO_PATH = "LOGOTIPO IG2P - OFICIAL.png" 

# --- 3. CSS PARA REPLICAR O DESIGN DA CAPTURA ---
st.markdown("""
<style>
    /* Fundo escuro conforme a imagem */
    .stApp {
        background-color: #0E1117 !important;
    }

    /* Ocultar elementos nativos do Streamlit */
    header[data-testid="stHeader"], 
    .stDeployButton, 
    footer { 
        display: none !important; 
    }

    /* Ajuste de margem superior para o logo */
    [data-testid="stImage"] {
        margin-top: 20px;
    }

    /* Estilização do Label do Selectbox */
    div[data-testid="stWidgetLabel"] p {
        color: white !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        margin-bottom: 8px !important;
    }

    /* Centralização visual do seletor */
    div[data-baseweb="select"] {
        background-color: #262730 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. LAYOUT DO LOGO (TOPO ESQUERDA) ---
col_logo, _ = st.columns([1, 4])
with col_logo:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=180)
    else:
        # Fallback caso o arquivo não seja encontrado no diretório
        st.error(f"Logo não encontrado: {LOGO_PATH}")

# --- 5. SELETOR CENTRALIZADO (ESTILO SEPARADO) ---
# Criamos um espaçamento vertical para centralizar como na foto
st.markdown("<br><br><br><br>", unsafe_allow_html=True)

_, col_center, _ = st.columns([1, 1, 1])

with col_center:
    # Lógica de seleção
    opcoes = ["Educação", "Saúde"]
    
    # Se já houver algo no session_state, mantemos a sincronia
    default_index = 0
    if 'setor_selecionado' in st.session_state:
        if st.session_state.setor_selecionado in opcoes:
            default_index = opcoes.index(st.session_state.setor_selecionado)

    setor = st.selectbox(
        "Selecione o Setor",
        opcoes,
        index=default_index,
        placeholder="Clique para escolher...",
        label_visibility="visible"
    )
    
    # Atualiza o estado global
    st.session_state.setor_selecionado = setor

# --- 6. GRID DE MUNICÍPIOS (LÓGICA MANTIDA) ---
# Adicionamos um espaço para a lista não grudar no seletor
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown(f"<h3 style='color: white; font-size: 18px;'>Municípios do Setor: {setor}</h3>", unsafe_allow_html=True)

if setor == "Saúde":
    municipios = [
        ("Alpinópolis", "pages/Alpinópolis_Saúde.py"),
        ("Bom Jesus da Penha", "pages/Bom_Jesus_da_Penha_Saúde.py"),
        ("Cássia", "pages/Cássia_Saúde.py"),
        ("Delfinópolis", "pages/Delfinópolis_Saúde.py"),
        ("Itaú de Minas", "pages/Itaú_de_Minas_Saúde.py"),
    ]
else:
    municipios = [
        ("Alpinópolis", "pages/Alpinópolis_Educação.py"),
        ("Bom Jesus da Penha", "pages/Bom_Jesus_da_Penha_Educação.py"),
        ("Cássia", "pages/Cássia_Educação.py"),
        ("Delfinópolis", "pages/Delfinópolis_Educação.py"),
        ("Itaú de Minas", "pages/Itaú_de_Minas_Educação.py"),
    ]

# Renderização dos botões em grid
cols = st.columns(5)
for i, (nome, path) in enumerate(municipios):
    with cols[i % 5]:
        if st.button(nome, key=f"btn_nav_{nome}"):
            if path:
                st.switch_page(path)