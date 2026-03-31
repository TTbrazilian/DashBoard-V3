import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed" # Tenta iniciar fechado
)

# --- 2. CAMINHO DO LOGO ---
LOGO_PATH = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.png" 

# --- 3. CSS PARA REMOVER MENU LATERAL E AJUSTAR POSICIONAMENTO ---
st.markdown("""
<style>
    /* REMOVER MENU LATERAL E UI NATIVA */
    [data-testid="stSidebar"], 
    [data-testid="stSidebarNav"],
    header[data-testid="stHeader"],
    .stDeployButton,
    footer {
        display: none !important;
        width: 0px !important;
    }

    /* AJUSTE DE ESPAÇAMENTO DA PÁGINA SEM SIDEBAR */
    .block-container {
        padding-top: 0rem !important;
        padding-left: 1rem !important;
        margin-left: 0px !important;
    }

    /* FUNDO ESCURO */
    .stApp {
        background-color: #0E1117 !important;
    }

    /* LOGO EXTREMAMENTE NO TOPO E CANTO */
    .logo-container {
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 1000;
    }

    /* ESTILO DO SELETOR */
    div[data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-size: 14px !important;
        font-weight: 500;
    }

    div[data-baseweb="select"] {
        background-color: #1F2329 !important;
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGOTIPO (POSIÇÃO ABSOLUTA) ---
if os.path.exists(LOGO_PATH):
    st.markdown(f'''
        <div class="logo-container">
            <img src="app/static/{LOGO_PATH}" width="160">
        </div>
    ''', unsafe_allow_html=True)
    # Fallback para renderização padrão colada no topo
    st.image(LOGO_PATH, width=160)
else:
    st.markdown('<div class="logo-container"><h2 style="color: white; margin: 0;">iG2P</h2></div>', unsafe_allow_html=True)

# --- 5. SELETOR CENTRALIZADO ---
st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

_, col_center, _ = st.columns([1.2, 1, 1.2])

with col_center:
    opcoes_reais = ["Educação", "Saúde"]
    
    # index=None garante que comece sem nada selecionado (mostrando o placeholder)
    setor_escolhido = st.selectbox(
        "Selecione o Setor",
        options=opcoes_reais,
        index=None,
        placeholder="Clique para selecionar o setor",
        label_visibility="visible"
    )

# --- 6. GRID DE MUNICÍPIOS (ENCAMINHAMENTO) ---
if setor_escolhido:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: white; font-size: 18px; font-weight: 400;'>Municípios do Setor: {setor_escolhido}</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid #31333F; margin-top: 0;'>", unsafe_allow_html=True)

    if setor_escolhido == "Saúde":
        municipios = [
            ("Alpinópolis", "pages/Alpinópolis_Saúde.py"),
            ("Bom Jesus da Penha", "pages/Bom_Jesus_da_Penha_Saúde.py"),
            ("Cássia", "pages/Cássia_Saúde.py"),
            ("Delfinópolis", "pages/Delfinópolis_Saúde.py"),
            ("Itaú de Minas", "pages/Itaú_de_Minas_Saúde.py"),
        ]
    else: # Educação
        municipios = [
            ("Alpinópolis", "pages/Alpinópolis_Educação.py"),
            ("Bom Jesus da Penha", "pages/Bom_Jesus_da_Penha_Educação.py"),
            ("Cássia", "pages/Cássia_Educação.py"),
            ("Delfinópolis", "pages/Delfinópolis_Educação.py"),
            ("Itaú de Minas", "pages/Itaú_de_Minas_Educação.py"),
        ]

    # Renderização em grade para encaminhamento
    cols = st.columns(5)
    for i, (nome, path) in enumerate(municipios):
        with cols[i % 5]:
            # Quando clicado, ele encaminha para a página específica
            if st.button(nome, key=f"btn_{nome}_{i}", use_container_width=True):
                if path:
                    st.switch_page(path)