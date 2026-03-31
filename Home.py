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

# --- 3. CSS "EXTREMO" PARA POSICIONAMENTO ---
st.markdown("""
<style>
    /* Remove todo o preenchimento superior e lateral da página */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        max-width: 95% !important;
    }

    /* Fundo escuro sólido */
    .stApp {
        background-color: #0E1117 !important;
    }

    /* Ocultar UI nativa (Header, Deploy, etc) */
    header[data-testid="stHeader"], 
    .stDeployButton, 
    footer { 
        display: none !important; 
    }

    /* Posicionamento do Logo: Extremamente no topo e no canto */
    .logo-container {
        position: absolute;
        top: 10px;
        left: 10px;
        z-index: 999;
    }

    /* Ajuste do Selectbox para manter o padrão visual */
    div[data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-size: 14px !important;
        font-weight: 500;
    }

    /* Estilo para os botões de municípios */
    div.stButton > button {
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGOTIPO (EXTREMO CANTO SUPERIOR ESQUERDO) ---
# Usando HTML para garantir que ele ignore o grid do Streamlit
if os.path.exists(LOGO_PATH):
    # Converte imagem para base64 ou usa caminho direto se o Streamlit permitir no HTML
    # Para simplicidade e eficácia, usamos o componente de imagem dentro de uma div posicionada
    st.markdown(f'''
        <div class="logo-container">
            <img src="app/static/{LOGO_PATH}" width="160">
        </div>
    ''', unsafe_allow_html=True)
    # Fallback caso o static não esteja configurado, usamos o componente padrão colado no topo
    st.image(LOGO_PATH, width=160)
else:
    st.markdown('<div class="logo-container"><h2 style="color: white; margin: 0;">iG2P</h2></div>', unsafe_allow_html=True)

# --- 5. SELETOR CENTRALIZADO ---
# Espaçamento para descer o seletor em relação ao topo
st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

_, col_center, _ = st.columns([1.2, 1, 1.2])

with col_center:
    # Definimos apenas as opções reais
    opcoes_reais = ["Educação", "Saúde"]
    
    # O index=None faz com que ele inicie vazio, mostrando apenas o placeholder
    setor_escolhido = st.selectbox(
        "Selecione o Setor",
        options=opcoes_reais,
        index=None,
        placeholder="Clique para selecionar o setor",
        label_visibility="visible"
    )
    
    # Atualiza o estado global apenas se algo for escolhido
    if setor_escolhido:
        st.session_state.setor_selecionado = setor_escolhido

# --- 6. GRID DE MUNICÍPIOS (PRECISO E INSTANTÂNEO) ---
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

    # Renderização em grade
    cols = st.columns(5)
    for i, (nome, path) in enumerate(municipios):
        with cols[i % 5]:
            if st.button(nome, key=f"btn_{nome}_{i}", use_container_width=True):
                if path:
                    st.switch_page(path)