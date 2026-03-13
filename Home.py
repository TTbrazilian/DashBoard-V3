import streamlit as st
import os

# Configuração da página - centralizada aqui para o portal todo
st.set_page_config(
    page_title="IG2P - Gestão Estratégica", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO PARA CENTRALIZAR O CONTEÚDO ---
st.markdown("""
    <style>
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .stImage {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # --- LOGOTIPO ---
    # Colunas para centralizar a imagem no meio da tela
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Tenta carregar a imagem com fundo branco/transparente para a Home
        # Se preferir a de fundo preto, mude o nome do arquivo abaixo
        nome_logo = "LOGOTIPO IG2P - OFICIAL.jpg"
        
        if os.path.exists(nome_logo):
            st.image(nome_logo, use_container_width=True)
        else:
            st.title("IG2P")

    # --- TEXTO DE BOAS-VINDAS ---
    st.markdown("<h1 style='text-align: center;'>Portal de Gestão de Recursos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>Inteligência em Gestão Pública e Privada</p>", unsafe_allow_html=True)
    
    st.divider()

    # --- INSTRUÇÕES ---
    st.markdown("### 📍 Navegação")
    st.info("Para acessar os dados de um município específico, utilize o **menu ao lado esquerdo**.")
    
    # Grid de Municípios (Exemplo visual para quando você adicionar mais)
    st.subheader("Municípios Atendidos")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.success("✅ **Bom Jesus da Penha**")
    with c2:
        st.write("⏳ *Em breve...*")
    with c3:
        st.write("⏳ *Em breve...*")

if __name__ == "__main__":
    main()