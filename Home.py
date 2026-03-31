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

# --- 3. CSS PARA POSICIONAMENTO E ESTILO ---
st.markdown("""
<style>
    /* Fundo escuro sólido */
    .stApp {
        background-color: #0E1117 !important;
    }

    /* Ocultar UI nativa */
    header[data-testid="stHeader"], 
    .stDeployButton, 
    footer { 
        display: none !important; 
    }

    /* Forçar o logo para o canto superior esquerdo absoluto */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }
    
    .logo-container {
        margin-top: -30px; /* Sobe o logo para o topo */
        margin-left: -50px; /* Encosta o logo na esquerda */
    }

    /* Estilo do Seletor */
    div[data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGOTIPO (CANTO SUPERIOR ESQUERDO) ---
col_logo, _ = st.columns([1, 4])
with col_logo:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=160)
    else:
        st.markdown("<h2 style='color: white; margin: 0;'>iG2P</h2>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. SELETOR CENTRALIZADO ---
st.markdown("<br><br><br><br>", unsafe_allow_html=True)

_, col_center, _ = st.columns([1.2, 1, 1.2])

with col_center:
    # Opções conforme solicitado
    opcoes = ["Clique para selecionar o setor", "Educação", "Saúde"]
    
    # Mantém o estado atual se já houver uma escolha
    if 'setor_selecionado' not in st.session_state:
        st.session_state.setor_selecionado = opcoes[0]

    setor_escolhido = st.selectbox(
        "Selecione o Setor",
        opcoes,
        index=opcoes.index(st.session_state.setor_selecionado) if st.session_state.setor_selecionado in opcoes else 0,
        label_visibility="visible"
    )
    
    # Atualização instantânea do estado
    if setor_escolhido != st.session_state.setor_selecionado:
        st.session_state.setor_selecionado = setor_escolhido
        st.rerun()

# --- 6. GRID DE MUNICÍPIOS (LÓGICA MANTIDA E INSTANTÂNEA) ---
if st.session_state.setor_selecionado != "Clique para selecionar o setor":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: white; font-size: 18px; font-weight: 400;'>Municípios do Setor: {st.session_state.setor_selecionado}</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid #31333F; margin-top: 0;'>", unsafe_allow_html=True)

    # Definição das listas baseada no setor
    if st.session_state.setor_selecionado == "Saúde":
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

    # Renderização em grade
    cols = st.columns(5)
    for i, (nome, path) in enumerate(municipios):
        with cols[i % 5]:
            if st.button(nome, key=f"btn_{nome}_{i}", use_container_width=True):
                if path:
                    st.switch_page(path)