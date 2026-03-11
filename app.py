import streamlit as st
import pandas as pd
import plotly.express as px
import os
import unicodedata

st.set_page_config(page_title="Gestão de Recursos - Bom Jesus", layout="wide")

# --- CONFIGURAÇÃO DE TRADUÇÃO DO PLOTLY ---
CONFIG_PT = {
    'locale': 'pt-BR',
    'displaylogo': False,
    'modeBarButtonsToolTipNames': {
        'toImage': 'Baixar como PNG',
        'zoom2d': 'Zoom',
        'pan2d': 'Mover',
        'select2d': 'Seleção retangular',
        'lasso2d': 'Seleção laço',
        'zoomIn2d': 'Aproximar',
        'zoomOut2d': 'Afastar',
        'autoScale2d': 'Ajuste automático',
        'resetScale2d': 'Redefinir escala',
        'hoverClosestCartesian': 'Mostrar mais próximo',
        'hoverCompareCartesian': 'Comparar dados'
    }
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
    caminho = os.path.join(diretorio_atual, 'fichas.csv')
    if not os.path.exists(caminho): return None
    df = pd.read_csv(caminho, sep=None, engine='python', encoding='utf-8', header=1)
    df.columns = [str(c).strip() for c in df.columns]
    
    if 'Ficha' in df.columns:
        df['Ficha'] = df['Ficha'].astype(str).str.replace('.0', '', regex=False).str.strip()

    cols_para_limpar = ['Orçado', 'Saldo', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho']
    for col in df.columns:
        if any(k in col for k in cols_para_limpar):
            df[col] = df[col].apply(limpar_valor)
    return df

# --- CARREGAMENTO E FILTRAGEM GLOBAL ---
df_raw = load_data()

if df_raw is not None:
    st.sidebar.header("🔍 Filtros")
    busca = st.sidebar.text_input("Filtrar Fichas/Categorias:")

    df_filtrado_global = df_raw.copy()
    if busca:
        termo = remover_acentos(busca)
        mask = (
            df_filtrado_global['Categoria'].apply(remover_acentos) == termo
        ) | (
            df_filtrado_global['Ficha'] == busca.strip()
        ) | (
            df_filtrado_global['Elemento'].apply(remover_acentos) == termo
        )
        df_filtrado_global = df_filtrado_global[mask]

    st.title("📊 Bom Jesus da Penha - Saúde")
    st.markdown("---")

    # --- KPIs ---
    orcado_total = df_filtrado_global['Orçado'].sum()
    saldo_total = df_filtrado_global['Saldo'].sum()
    executado = orcado_total - saldo_total
    perc_exec = (executado / orcado_total * 100) if orcado_total > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Previsão (Orçado)", formar_real(orcado_total))
    with c2: st.metric("Saldo Disponível", formar_real(saldo_total))
    with c3: st.metric("Executado (Liquidado)", formar_real(executado))
    with c4: st.metric("% de Execução", f"{perc_exec:.2f}%".replace('.', ','))

    # --- ANÁLISE 2: EVOLUÇÃO MENSAL ---
    st.subheader("📈 Evolução Mensal da Execução")
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho']
    mensal_dados = [{"Mês": m, "Valor": df_filtrado_global[m].sum()} for m in meses if m in df_filtrado_global.columns]
    df_mensal = pd.DataFrame(mensal_dados)
    fig_evolucao = px.line(df_mensal, x='Mês', y='Valor', markers=True, color_discrete_sequence=["#00CC96"])
    fig_evolucao.update_layout(yaxis_tickprefix='R$ ', yaxis_tickformat=',.2f', separators=',.')
    st.plotly_chart(fig_evolucao, use_container_width=True, config=CONFIG_PT)

    # --- ANÁLISE 3: DETALHAMENTO POR ELEMENTO ---
    st.markdown("---")
    st.subheader("📦 Detalhamento por Elemento")

    st.markdown("""<style>
        @keyframes barraSobe { from { opacity: 0; transform: scaleY(0); transform-origin: bottom; } to { opacity: 1; transform: scaleY(1); transform-origin: bottom; } }
        .js-plotly-plot .point path { animation: barraSobe 1.2s cubic-bezier(0.4, 0, 0.2, 1) forwards; opacity: 0; }
        .js-plotly-plot .point path:nth-child(1) { animation-delay: 0.1s; }
    </style>""", unsafe_allow_html=True)

    elementos_disponiveis = sorted([str(x) for x in df_filtrado_global['Elemento'].dropna().unique()])

    if elementos_disponiveis:
        st.write("Selecione um elemento para visualizar o detalhamento:")
        cols_botoes = st.columns(4) 
        for i, elemento in enumerate(elementos_disponiveis):
            with cols_botoes[i % 4]:
                if st.button(elemento, use_container_width=True, key=f"btn_{i}"):
                    st.session_state['elemento_ativo'] = elemento

        if 'elemento_ativo' in st.session_state:
            ele = st.session_state['elemento_ativo']
            df_detalhe = df_filtrado_global[df_filtrado_global['Elemento'] == ele].sort_values('Orçado', ascending=False)
            
            st.subheader(f"📊 Detalhamento de Fichas: {ele}")
            label_hover = "Elemento" if busca else "Categoria"
            
            fig_detalhe = px.bar(df_detalhe, x='Ficha', y='Orçado', text='Orçado',
                                 color_discrete_sequence=["#00CC96"], 
                                 custom_data=[label_hover])

            fig_detalhe.update_traces(
                hovertemplate=f"<b>{label_hover}:</b> %{{customdata[0]}}<br><b>Valor:</b> R$ %{{y:,.2f}}<extra></extra>",
                texttemplate='R$ %{text:,.2f}', textposition='outside', cliponaxis=False,
                width=0.8 if len(df_detalhe) < 12 else 0.5
            )
            fig_detalhe.update_layout(xaxis_type='category', height=550, separators=',.',
                                      yaxis=dict(range=[0, df_detalhe['Orçado'].max() * 1.30]),
                                      margin=dict(t=80, b=50, l=50, r=50))
            st.plotly_chart(fig_detalhe, use_container_width=True, theme=None, config=CONFIG_PT)
            
            if st.button("⬅️ Voltar para Visão Geral"):
                del st.session_state['elemento_ativo']
                st.rerun()

    # --- ANÁLISE 4: RELATÓRIO TÉCNICO ---
    st.markdown("---")
    st.subheader("📋 Relatório Detalhado (Estilo Relatório)")
    df_relatorio = df_filtrado_global.copy()
    
    for col_val in ['Orçado', 'Saldo']:
        df_relatorio[col_val + '_F'] = df_relatorio[col_val].apply(formar_real)

    st.data_editor(
        df_relatorio[['Categoria', 'Ficha', 'Elemento', 'Fonte', 'Orçado_F', 'Saldo_F']],
        use_container_width=True, hide_index=True, disabled=True,
        column_config={
            "Orçado_F": "Orçado", 
            "Saldo_F": "Saldo",
            "Elemento": st.column_config.TextColumn("Elemento", width="large"),
            "Ficha": st.column_config.TextColumn("Ficha"),
        },
    )

else:
    st.error("Arquivo 'fichas.csv' não encontrado!")