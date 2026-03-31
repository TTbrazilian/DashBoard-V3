import streamlit as st

# Configurações da Página
st.set_page_config(
    page_title="Gestão Inteligente - Municípios do Setor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Neon Civic (CSS customizado para simular o design)
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #0C1004;
        color: #E0E5CE;
    }
    .stButton>button {
        background-color: #1D2113;
        color: #BFFF00;
        border: 1px solid #434933;
        border-radius: 8px;
        width: 100%;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #BFFF00;
        color: #0C1004;
        border-color: #BFFF00;
    }
    .sector-card {
        padding: 20px;
        border: 1px solid #434933;
        border-radius: 12px;
        background-color: #111508;
        cursor: pointer;
        text-align: center;
    }
    .active-sector {
        border-color: #BFFF00;
        box-shadow: 0 0 15px rgba(191, 255, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Dados de Municípios por Setor
municipios_data = {
    "Saúde": [
        ("Alpinópolis", "pages/Alpinópolis_Saúde.py"),
        ("Bom Jesus da Penha", "pages/Bom_Jesus_da_Penha_Saúde.py"),
        ("Cássia", "pages/Cássia_Saúde.py"),
        ("Delfinópolis", "pages/Delfinópolis_Saúde.py"),
        ("Itaú de Minas", "pages/Itaú_de_Minas_Saúde.py")
    ],
    "Educação": [
        ("Alpinópolis", "pages/Alpinópolis_Educação.py"),
        ("Bom Jesus da Penha", "pages/Bom_Jesus_da_Penha_Educação.py"),
        ("Cássia", "pages/Cássia_Educação.py"),
        ("Delfinópolis", "pages/Delfinópolis_Educação.py"),
        ("Itaú de Minas", "pages/Itaú_de_Minas_Educação.py")
    ]
}

# Título Principal
st.title("Inteligência em Gestão Pública")
st.write("Selecione o setor para visualizar os municípios disponíveis.")

# Lógica de Seleção de Setor
if 'setor_selecionado' not in st.session_state:
    st.session_state.setor_selecionado = "Saúde"

col1, col2 = st.columns(2)

with col1:
    if st.button("Educação", key="btn_educacao"):
        st.session_state.setor_selecionado = "Educação"
with col2:
    if st.button("Saúde", key="btn_saude"):
        st.session_state.setor_selecionado = "Saúde"

st.markdown(f"### Municípios do Setor: **{st.session_state.setor_selecionado}**")

# Exibição dos Municípios
setor = st.session_state.setor_selecionado
cols = st.columns(3)

for idx, (nome, link) in enumerate(municipios_data[setor]):
    with cols[idx % 3]:
        # No Streamlit real, o redirecionamento pode ser feito via st.switch_page
        # ou criando um link HTML se for para uma URL externa.
        if st.button(nome, key=f"mun_{idx}"):
            st.info(f"Encaminhando para: {link}")
            # st.switch_page(link) # Comando para navegar entre páginas no Streamlit
