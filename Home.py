import streamlit as st
import os

st.set_page_config(page_title="IG2P - Gestão Estratégica", layout="wide")

# Centralizar o logo
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    # Usando a versão fundo preto (ou a que você preferir)
    if os.path.exists("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg"):
        st.image("LOGOTIPO IG2P - OFICIAL - BRANCO.jpg", use_container_width=True)
    else:
        st.title("IG2P")

st.markdown("<h1 style='text-align: center;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
st.divider()

st.info("👈 Selecione um município no menu lateral para acessar os dados.")