import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PARA CENTRALIZAÇÃO E ESTILO ---
st.markdown("""
<style>
    /* Fundo escuro padrão */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Centralizar o conteúdo do seletor */
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 50px;
    }

    /* Ajuste para o Logo */
    .logo-container {
        text-align: left;
        width: 100%;
        margin-bottom: 40px;
    }

    /* Estilização do Selectbox para ficar mais limpo */
    div[data-baseweb="select"] {
        width: 300px !important;
        margin: 0 auto;
    }
    
    label[data-testid="stWidgetLabel"] {
        color: white !important;
        text-align: center;
        display: block;
        width: 100%;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGO (Conforme a imagem capturada) ---
# Se você tiver o arquivo local, use st.image("logo.png", width=150)
# Aqui estou simulando o posicionamento da imagem
col_logo, _ = st.columns([1, 4])
with col_logo:
    # Simulando o logo iG2Py com HTML/CSS para manter o estilo visual
    st.markdown("""
        <div style="font-family: sans-serif; color: white; line-height: 1;">
            <span style="font-size: 40px; font-weight: 800;">iG</span><br>
            <span style="font-size: 40px; font-weight: 800;">2P</span><span style="color: #00FF00; font-size: 50px;">✓</span><br>
            <span style="font-size: 14px; opacity: 0.8;">Inteligência em Gestão</span>
        </div>
    """, unsafe_allow_html=True)

st.write("---") # Linha divisória sutil

# --- 4. SELEÇÃO DE SETOR (Lógica mantida, design simplificado) ---
# Centralizando o seletor na tela
_, col_center, _ = st.columns([1, 1, 1])

with col_center:
    setor = st.selectbox(
        "Selecione o Setor",
        ["Educação", "Saúde"],
        index=0 if st.session_state.get('setor_selecionado') == "Educação" else 1,
        placeholder="Clique para escolher...",
    )
    st.session_state.setor_selecionado = setor

# --- 5. LÓGICA DE MUNICÍPIOS (Mantida do seu código) ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.subheader(f"Municípios do Setor: {setor}")

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

# Grid de botões para os municípios
cols_mun = st.columns(5)
for idx, (nome, path) in enumerate(municipios):
    with cols_mun[idx % 5]:
        if st.button(nome, key=f"btn_{nome}"):
            if path:
                st.switch_page(path)