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

# --- 3. CSS PARA QUALIDADE, POSICIONAMENTO E BLOQUEIO DE UI ---
st.markdown("""
<style>
    /* REMOVER MENU LATERAL E UI NATIVA */
    [data-testid="stSidebar"], 
    [data-testid="stSidebarNav"],
    header[data-testid="stHeader"],
    .stDeployButton,
    footer {
        display: none !important;
    }

    /* REMOVER BOTÃO DE TELA CHEIA E INTERAÇÕES DE IMAGEM */
    [data-testid="stImage"] button, 
    button[title="View fullscreen"] {
        display: none !important;
    }
    
    [data-testid="stImage"] img {
        pointer-events: none; /* Desabilita cliques e hover no logo */
        image-rendering: -webkit-optimize-contrast; /* Melhora nitidez em alguns navegadores */
        image-rendering: crisp-edges;
    }

    /* AJUSTE DE ESPAÇAMENTO DA PÁGINA */
    .block-container {
        padding-top: 0rem !important;
        padding-left: 1rem !important;
    }

    /* FUNDO ESCURO */
    .stApp {
        background-color: #0E1117 !important;
    }

    /* TEXTO ABAIXO DO LOGO */
    .brand-text {
        color: white;
        font-family: sans-serif;
        font-size: 14px;
        margin-top: -15px; /* Ajuste para colar no logo */
        margin-left: 5px;
        font-weight: 400;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGOTIPO E TEXTO (TOPO ESQUERDO) ---
col_brand, _ = st.columns([1, 4])
with col_brand:
    if os.path.exists(LOGO_PATH):
        # Renderização com largura fixa para preservar a densidade de pixels
        st.image(LOGO_PATH, width=170)
        st.markdown('<p class="brand-text">Inteligência em gestão</p>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="color: white; font-family: sans-serif; padding: 10px;">
                <h2 style="margin:0;">iG2P</h2>
                <p style="margin:0; font-size:14px;">Inteligência em gestão</p>
            </div>
        """, unsafe_allow_html=True)

# --- 5. SELETOR CENTRALIZADO ---
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

_, col_center, _ = st.columns([1.2, 1, 1.2])

with col_center:
    opcoes_reais = ["Educação", "Saúde"]
    
    setor_escolhido = st.selectbox(
        "Selecione o Setor",
        options=opcoes_reais,
        index=None,
        placeholder="Clique para selecionar o setor",
        label_visibility="visible"
    )

# --- 6. GRID DE MUNICÍPIOS ---
if setor_escolhido:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: white; font-size: 18px; font-weight: 400;'>Municípios do Setor: {setor_escolhido}</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid #31333F; margin-top: 0;'>", unsafe_allow_html=True)

    # Lógica de caminhos conforme o setor
    suffix = "Saúde" if setor_escolhido == "Saúde" else "Educação"
    municipios_nomes = ["Alpinópolis", "Bom Jesus da Penha", "Cássia", "Delfinópolis", "Itaú de Minas"]
    
    municipios = [(nome, f"pages/{nome.replace(' ', '_')}_{suffix}.py") for nome in municipios_nomes]

    cols = st.columns(5)
    for i, (nome, path) in enumerate(municipios):
        with cols[i % 5]:
            if st.button(nome, key=f"btn_{nome}_{i}", use_container_width=True):
                if path:
                    st.switch_page(path)