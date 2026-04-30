import streamlit as st
import os
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. FUNÇÃO PARA CARREGAR IMAGEM SEM PERDA ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

LOGO_PATH = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.png"
logo_base64 = get_image_base64(LOGO_PATH)

# --- 3. CSS PARA IDENTIDADE VISUAL, BLOQUEIO DE ESCRITA E CENTRALIZAÇÃO ---
st.markdown(f"""
<style>
    /* Remover Sidebar e UI nativa */
    [data-testid="stSidebar"], 
    header[data-testid="stHeader"],
    .stDeployButton,
    footer {{
        display: none !important;
    }}

    /* IMPEDIR ESCRITA NO SELECTBOX (Apenas clique) */
    div[data-baseweb="select"] input {{
        caret-color: transparent !important;
        cursor: pointer !important;
        pointer-events: none !important;
    }}

    /* Fundo escuro sólido */
    .stApp {{
        background-color: #0E1117 !important;
    }}

    /* Container da Página */
    .block-container {{
        padding-top: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
    }}

    /* Posicionamento do Logo e Texto no Canto Superior */
    .brand-box {{
        position: absolute;
        top: 20px;
        left: 20px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        z-index: 1000;
    }}

    .brand-box img {{
        width: 160px;
        height: auto;
        image-rendering: -webkit-optimize-contrast;
    }}

    .brand-box p {{
        color: white;
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 14px;
        margin: -5px 0 0 5px !important;
        padding: 0 !important;
        white-space: nowrap;
    }}

    /* Centralização do título dos municípios */
    .municipio-header {{
        color: white; 
        font-size: 18px; 
        text-align: center;
        width: 100%;
        margin-top: 40px;
        font-family: sans-serif;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. RENDERIZAÇÃO DO LOGO E SUBTÍTULO ---
if logo_base64:
    st.markdown(f"""
        <div class="brand-box">
            <img src="data:image/png;base64,{logo_base64}">
            <p>Inteligência em Gestão</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="brand-box">
            <h2 style="color:white; margin:0;">iG2P</h2>
            <p>Inteligência em Gestão</p>
        </div>
    """, unsafe_allow_html=True)

# --- 5. SELETOR CENTRALIZADO ---
st.markdown("<br><br><br><br><br><br><br>", unsafe_allow_html=True)

_, col_center, _ = st.columns([1.2, 1, 1.2])

with col_center:
    opcoes_reais = ["Educação", "Saúde"]
    
    setor_escolhido = st.selectbox(
        "Selecione o Setor",
        options=opcoes_reais,
        index=None,
        placeholder="Clique para escolher...",
        label_visibility="visible"
    )

# --- 6. GRID DE MUNICÍPIOS CENTRALIZADO ---
if setor_escolhido:
    st.markdown(f'<p class="municipio-header">Municípios do Setor: {setor_escolhido}</p>', unsafe_allow_html=True)
    
    # Definição das listas específicas por setor
    if setor_escolhido == "Educação":
        nomes = [
            "Alpinópolis", "Cássia", "Capetinga", "Claraval", "Delfinópolis", 
            "Ibiraci", "Itaú", "Pratápolis", "Restinga", "São João Batista Do Glória", 
            "São José da Barra", "São Roque de Minas", "São Tomás de Aquino", "Itamogi"
        ]
        suffix = "Educação"
    else: # Saúde
        nomes = ["Alpinópolis", "Bom Jesus da Penha", "Cássia", "Delfinópolis", "Itaú de Minas"]
        suffix = "Saúde"
    
    # Centralização das caixas com margens laterais iguais
    _, col_buttons, _ = st.columns([0.1, 0.8, 0.1])
    
    with col_buttons:
        # Criar colunas (5 por linha)
        cols = st.columns(5)
        for i, nome in enumerate(nomes):
            with cols[i % 5]:
                file_name = nome.replace(' ', '_')
                path = f"pages/{file_name}_{suffix}.py"
                
                if st.button(nome, key=f"btn_{nome}_{i}", use_container_width=True):
                    # ── GUARDA O SETOR NA SESSÃO ──────────────────────────────
                    # Cada página de município lê st.session_state['setor_ativo']
                    # e oculta da barra lateral os municípios do outro setor.
                    st.session_state['setor_ativo'] = setor_escolhido
                    # ─────────────────────────────────────────────────────────
                    try:
                        st.switch_page(path)
                    except Exception as e:
                        st.error(f"Página não encontrada: {path}")