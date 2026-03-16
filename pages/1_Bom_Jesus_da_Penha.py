import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import unicodedata
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="Gestão de Recursos - Bom Jesus", layout="wide")

# --- TRADUÇÃO GLOBAL DO PLOTLY ---
pio.templates.default = "plotly_white"

CONFIG_PT = {
    'displaylogo': False,
    'showTips': False,
    'modeBarButtonsToolTipNames': {}
}

# --- FUNÇÕES UTILITÁRIAS ---
def remover_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower().strip()

def limpar_valor(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "-", "R$ 0,00", "0"]:
        return 0.0
    s_valor = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try: return float(s_valor)
    except: return 0.0

def formar_real(valor):
    if valor is None: return "R$ 0,00"
    a_la_us = f"{valor:,.2f}"
    a_la_br = a_la_us.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {a_la_br}"

@st.cache_data
def load_data():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(diretorio_atual, '..', 'fichas.csv')
    if not os.path.exists(caminho):
        caminho = os.path.join(diretorio_atual, 'fichas.csv')
        if not os.path.exists(caminho): return None
        
    df = pd.read_csv(caminho, sep=None, engine='python', encoding='utf-8', header=1)
    df.columns = [str(c).strip() for c in df.columns]
    
    if 'Ficha' in df.columns:
        df['Ficha'] = df['Ficha'].astype(str).str.replace('.0', '', regex=False).str.strip()

    if 'Fonte' in df.columns:
        df['Fonte'] = df['Fonte'].astype(str).str.replace('.0', '', regex=False).str.strip()

    cols_para_limpar = ['Orçado', 'Saldo', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    for col in df.columns:
        if any(k in col for k in cols_para_limpar):
            df[col] = df[col].apply(limpar_valor)
    return df

# --- CARREGAMENTO E FILTRAGEM ---
df_raw = load_data()

if df_raw is not None:
    st.sidebar.header("🔍 Filtros")
    
    if 'busca' not in st.session_state:
        st.session_state.busca = ""

    busca = st.sidebar.text_input("Filtrar:", value=st.session_state.busca)
    st.session_state.busca = busca

    if 'Categoria' in df_raw.columns:
        st.sidebar.write("---")
        st.sidebar.write("Categorias:")
        cats = sorted(df_raw['Categoria'].dropna().unique())
        for c in cats:
            if st.sidebar.button(c, use_container_width=True, key=f"cat_{c}"):
                st.session_state.busca = c
                st.rerun()
        
        if st.sidebar.button("Limpar Filtros", type="secondary", use_container_width=True):
            st.session_state.busca = ""
            st.rerun()

    df_filtrado_global = df_raw.copy()
    if st.session_state.busca:
        termo = remover_acentos(st.session_state.busca)
        categorias_existentes = {remover_acentos(cat): cat for cat in df_raw['Categoria'].unique() if pd.notna(cat)}
        
        if termo in categorias_existentes:
            mask = df_filtrado_global['Categoria'].apply(remover_acentos) == termo
        else:
            mask = (
                df_filtrado_global['Categoria'].apply(remover_acentos).str.contains(termo, na=False)
            ) | (
                df_filtrado_global['Ficha'] == st.session_state.busca.strip()
            ) | (
                df_filtrado_global['Elemento'].apply(remover_acentos).str.contains(termo, na=False)
            ) | (
                df_filtrado_global['Fonte'].str.contains(st.session_state.busca.strip(), na=False)
            )
        df_filtrado_global = df_filtrado_global[mask]

    st.title("📊 Bom Jesus da Penha - Saúde")
    st.markdown("---")

    orcado_total = df_filtrado_global['Orçado'].sum()
    saldo_total = df_filtrado_global['Saldo'].sum()
    executado = orcado_total - saldo_total
    perc_exec = (executado / orcado_total * 100) if orcado_total > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Previsão (Orçado)", formar_real(orcado_total))
    with c2: st.metric("Saldo Disponível", formar_real(saldo_total))
    with c3: st.metric("Executado (Liquidado)", formar_real(executado))
    with c4: st.metric("% de Execução", f"{perc_exec:.2f}%".replace('.', ','))

    st.subheader("📈 Evolução Mensal da Execução")
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    mensal_dados = [{"Mês": m, "Valor": df_filtrado_global[m].sum()} for m in meses if m in df_filtrado_global.columns]
    df_mensal = pd.DataFrame(mensal_dados)
    fig_evolucao = px.line(df_mensal, x='Mês', y='Valor', markers=True, color_discrete_sequence=["#00CC96"])
    fig_evolucao.update_layout(yaxis_tickprefix='R$ ', yaxis_tickformat=',.2f', separators=',.')
    st.plotly_chart(fig_evolucao, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")
    
    # 1. Marcador HTML fixo
    st.markdown('<div id="alvo-detalhamento"></div>', unsafe_allow_html=True)
    st.subheader("📦 Detalhamento por Elemento")

    # (CSS de animação mantido)
    st.markdown("""
        <style>
        @keyframes subirBarra {
            from { clip-path: inset(100% 0 0 0); }
            to { clip-path: inset(0% 0 0 0); }
        }
        .js-plotly-plot .point path {
            animation: subirBarra 0.8s cubic-bezier(0.25, 1, 0.5, 1) forwards;
            clip-path: inset(100% 0 0 0);
        }
        </style>
    """, unsafe_allow_html=True)

    elementos_disponiveis = sorted([str(x) for x in df_filtrado_global['Elemento'].dropna().unique()])

    if elementos_disponiveis:
        st.write("Selecione um elemento para visualizar o detalhamento:")
        cols_botoes = st.columns(4)
        for i, elemento in enumerate(elementos_disponiveis):
            with cols_botoes[i % 4]:
                if st.button(elemento, use_container_width=True, key=f"btn_{i}"):
                    st.session_state['elemento_ativo'] = elemento
                    # 2. Quando clica, marca que precisa rolar
                    st.session_state['scroll_necessario'] = True
                    st.rerun()

        if 'elemento_ativo' in st.session_state:
            # 3. Se o scroll for necessário, executa o script com delay
            if st.session_state.get('scroll_necessario'):
                components.html(
                    """
                    <script>
                    setTimeout(function() {
                        var element = window.parent.document.getElementById('alvo-detalhamento');
                        if (element) {
                            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    }, 300); // Aguarda 300ms para o Streamlit renderizar o conteúdo
                    </script>
                    """,
                    height=0
                )
                # Reseta para não rolar em cada interação posterior
                st.session_state['scroll_necessario'] = False

            ele = st.session_state['elemento_ativo']
            df_detalhe = df_filtrado_global[df_filtrado_global['Elemento'] == ele].sort_values('Orçado', ascending=False).copy()
            
            st.subheader(f"📊 Detalhamento de Fichas: {ele}")
            
            # (Restante da lógica do gráfico detalhado mantida exatamente igual...)
            lista_elementos = [remover_acentos(e) for e in df_raw['Elemento'].unique() if pd.notna(e)]
            busca_limpa = remover_acentos(st.session_state.busca)
            label_hover = "Categoria" if st.session_state.busca and (busca_limpa in lista_elementos) else ("Elemento" if st.session_state.busca else "Categoria")
            
            fig_detalhe = px.bar(
                df_detalhe, x='Ficha', y='Orçado',
                color_discrete_sequence=["#00CC96"],
                custom_data=[label_hover, 'Fonte']
            )

            fig_detalhe.update_traces(
                hovertemplate=f"<b>{label_hover}:</b> %{{customdata[0]}}<br><b>Fonte:</b> %{{customdata[1]}}<br><b>Valor:</b> R$ %{{y:,.2f}}<extra></extra>",
                text=df_detalhe['Orçado'].apply(formar_real),
                textposition='outside',
                cliponaxis=False,
                width=0.8 if len(df_detalhe) < 12 else 0.5
            )

            fig_detalhe.update_layout(
                xaxis_type='category', height=550, separators=',.',
                yaxis=dict(range=[0, df_detalhe['Orçado'].max() * 1.30]),
                margin=dict(t=80, b=50, l=50, r=50)
            )

            st.plotly_chart(fig_detalhe, use_container_width=True, theme=None, config=CONFIG_PT)
            
            if st.button("⬅️ Voltar para Visão Geral"):
                del st.session_state['elemento_ativo']
                st.rerun()
    
    # --- Continuação dos outros gráficos (Custeio, Execução, etc) ---
    st.markdown("---")
    # ... (O código original continua aqui sem alterações)