import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CAMINHO DO LOGO ---
LOGO_PATH = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.png" 

# --- 3. CSS PARA DESIGN FIEL À FOTO ---
st.markdown("""
<style>
    /* Fundo escuro sólido */
    .stApp {
        background-color: #0E1117 !important;
    }

    /* Ocultar UI padrão */
    header[data-testid="stHeader"], 
    .stDeployButton, 
    footer { 
        display: none !important; 
    }

    /* Logo no topo com margem */
    [data-testid="stImage"] {
        margin-top: 10px;
        margin-left: 0px;
    }

    /* Estilo do Seletor (Dropdown) */
    div[data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-family: sans-serif;
        font-size: 14px !important;
        margin-bottom: 10px !important;
    }

    div[data-baseweb="select"] {
        background-color: #1F2329 !important;
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGOTIPO NO TOPO ESQUERDO ---
col_logo, _ = st.columns([1, 4])
with col_logo:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=160)
    else:
        st.markdown("<h2 style='color: white;'>iG2P</h2>", unsafe_allow_html=True)

# --- 5. SELETOR DE SETOR CENTRALIZADO ---
# Espaçamento para o centro da tela
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

_, col_center, _ = st.columns([1.2, 1, 1.2])

with col_center:
    # Opções com placeholder no índice 0
    opcoes = ["Clique para escolher...", "Educação", "Saúde"]
    
    # Busca o estado anterior ou define o padrão como 0 (Clique para escolher...)
    current_idx = 0
    if 'setor_selecionado' in st.session_state:
        if st.session_state.setor_selecionado in opcoes:
            current_idx = opcoes.index(st.session_state.setor_selecionado)

    setor_escolhido = st.selectbox(
        "Selecione o Setor",
        opcoes,
        index=current_idx
    )
    
    # Atualiza o estado
    st.session_state.setor_selecionado = setor_escolhido

# --- 6. EXIBIÇÃO CONDICIONAL DOS MUNICÍPIOS ---
# Só mostra a lista se o usuário escolheu algo diferente do placeholder
if setor_escolhido != "Clique para escolher...":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: white; font-family: sans-serif; font-size: 18px; font-weight: 400;'>Municípios do Setor: {setor_escolhido}</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid #31333F; margin-top: 0;'>", unsafe_allow_html=True)

    if setor_escolhido == "Saúde":
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

    # Grid de 5 colunas para os municípios
    cols = st.columns(5)
    for i, (nome, path) in enumerate(municipios):
        with cols[i % 5]:
            if st.button(nome, key=f"btn_{nome}", use_container_width=True):
                if path:
                    st.switch_page(path)