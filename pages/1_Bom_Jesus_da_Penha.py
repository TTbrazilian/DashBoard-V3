import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio  # Importação necessária para forçar a tradução
import os
import unicodedata
import plotly.graph_objects as go

st.set_page_config(page_title="Gestão de Recursos - Bom Jesus", layout="wide")

# --- TRADUÇÃO GLOBAL DO PLOTLY ---
pio.templates.default = "plotly_white"

# CONFIG_PT alterado para manter a barra mas remover as tooltips (textos de hover)
CONFIG_PT = {
    'displaylogo': False,
    'showTips': False,  # Esta linha desativa os balões de texto dos ícones
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
    # Busca o arquivo subindo um nível caso esteja na pasta pages
    caminho = os.path.join(diretorio_atual, '..', 'fichas.csv')
    if not os.path.exists(caminho):
        # Tenta na mesma pasta caso não esteja em subpasta
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
    
    # Gerencia o estado da busca para os botões funcionarem sem conflito
    if 'busca_input' not in st.session_state:
        st.session_state.busca_input = ""

    # Input de texto vinculado à chave do session_state
    busca = st.sidebar.text_input("Filtrar:", value=st.session_state.busca_input, key="filtro_manual")
    st.session_state.busca_input = busca

    # --- ADIÇÃO DOS BOTÕES DE CATEGORIA ---
    st.sidebar.write("Categorias:")
    categorias_unicas = sorted(df_raw['Categoria'].unique())
    for cat in categorias_unicas:
        if st.sidebar.button(cat, use_container_width=True):
            st.session_state.busca_input = cat
            st.rerun()

    if st.sidebar.button("Limpar Filtros", type="secondary"):
        st.session_state.busca_input = ""
        st.rerun()
    # --------------------------------------

    df_filtrado_global = df_raw.copy()
    if st.session_state.busca_input:
        termo = remover_acentos(st.session_state.busca_input)
        
        # Mapeamento para verificar se a busca é exatamente uma Categoria
        categorias_existentes = {remover_acentos(cat): cat for cat in df_raw['Categoria'].unique()}
        
        if termo in categorias_existentes:
            # Filtro restrito: Se digitar "MAC", traz apenas a categoria MAC
            mask = df_filtrado_global['Categoria'].apply(remover_acentos) == termo
        else:
            # Busca ampla caso não seja uma categoria exata
            mask = (
                df_filtrado_global['Categoria'].apply(remover_acentos).str.contains(termo, na=False)
            ) | (
                df_filtrado_global['Ficha'] == st.session_state.busca_input.strip()
            ) | (
                df_filtrado_global['Elemento'].apply(remover_acentos).str.contains(termo, na=False)
            ) | (
                df_filtrado_global['Fonte'].str.contains(st.session_state.busca_input.strip(), na=False)
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

    # --- GRÁFICO DE EVOLUÇÃO MENSAL ---
    st.subheader("📈 Evolução Mensal da Execução")
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    mensal_dados = [{"Mês": m, "Valor": df_filtrado_global[m].sum()} for m in meses if m in df_filtrado_global.columns]
    df_mensal = pd.DataFrame(mensal_dados)
    fig_evolucao = px.line(df_mensal, x='Mês', y='Valor', markers=True, color_discrete_sequence=["#00CC96"])
    fig_evolucao.update_layout(yaxis_tickprefix='R$ ', yaxis_tickformat=',.2f', separators=',.')
    st.plotly_chart(fig_evolucao, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")
    st.subheader("📦 Detalhamento por Elemento")

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

        if 'elemento_ativo' in st.session_state:
            ele = st.session_state['elemento_ativo']
            df_detalhe = df_filtrado_global[df_filtrado_global['Elemento'] == ele].sort_values('Orçado', ascending=False).copy()
            
            st.subheader(f"📊 Detalhamento de Fichas: {ele}")
            
            lista_elementos = [remover_acentos(e) for e in df_raw['Elemento'].unique()]
            busca_limpa = remover_acentos(st.session_state.busca_input)
            label_hover = "Categoria" if st.session_state.busca_input and (busca_limpa in lista_elementos) else ("Elemento" if st.session_state.busca_input else "Categoria")
            
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
    
    st.markdown("---")
    st.subheader("📊 Custeio x Capital")
    
    df_filtrado_global['Natureza'] = df_filtrado_global['Elemento'].apply(
        lambda x: 'Capital (Invest.)' if '4.4' in str(x) else 'Custeio (Manut.)'
    )
    
    df_natureza = df_filtrado_global.groupby('Natureza')['Orçado'].sum().reset_index()
    if 'Capital (Invest.)' not in df_natureza['Natureza'].values:
        nova_linha = pd.DataFrame({'Natureza': ['Capital (Invest.)'], 'Orçado': [0.0]})
        df_natureza = pd.concat([df_natureza, nova_linha], ignore_index=True)
    
    fig_natureza = px.pie(df_natureza, values='Orçado', names='Natureza', hole=.4,
                         color='Natureza',
                         color_discrete_map={'Custeio (Manut.)':'#00CC96', 'Capital (Invest.)':'#EF553B'})
    
    fig_natureza.update_layout(
        margin=dict(t=50, b=50, l=20, r=20),
        height=450,
        showlegend=True,
        separators=',.',
        legend=dict(
            itemclick="toggle",
            itemdoubleclick="toggleothers",
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=16)
        )
    )
    fig_natureza.update_traces(
        textinfo='percent',
        textposition='inside',
        hovertemplate="<b>Natureza:</b> %{label}<br><b>Valor Total:</b> R$ %{value:,.2f}<extra></extra>"
    )
    
    _, col_central_1, _ = st.columns([1, 2, 1])
    with col_central_1:
        st.plotly_chart(fig_natureza, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")
    st.subheader("🎯 % de Execução por Categoria")
    
    df_exec_final = df_filtrado_global.groupby('Categoria').agg({'Orçado': 'sum', 'Saldo': 'sum'}).reset_index()
    df_exec_final['Executado'] = df_exec_final['Orçado'] - df_exec_final['Saldo']
    df_exec_final['Perc'] = (df_exec_final['Executado'] / df_exec_final['Orçado'] * 100).fillna(0)
    df_exec_final = df_exec_final.sort_values('Perc', ascending=True)

    fig_exec_final = px.bar(df_exec_final, x='Perc', y='Categoria', orientation='h',
                          text='Perc', color='Perc', color_continuous_scale='Greens')
    
    fig_exec_final.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside',
        hovertemplate="<b>Categoria:</b> %{y}<br><b>Execução:</b> %{x:.2f}%<extra></extra>"
    )
    fig_exec_final.update_layout(
        xaxis_title="Liquidado (%)", yaxis_title="",
        coloraxis_showscale=False, height=400,
        separators=',.',
        margin=dict(l=200),
        xaxis=dict(range=[0, 120])
    )
    st.plotly_chart(fig_exec_final, use_container_width=True, config=CONFIG_PT)

    # --- NOVO GRÁFICO: COMPARATIVO ORÇADO X EXECUTADO POR CATEGORIA ---
    st.markdown("---")
    st.subheader("💰 Orçado vs Executado por Categoria")
    
    df_comp_cat = df_filtrado_global.groupby('Categoria').agg({'Orçado': 'sum', 'Saldo': 'sum'}).reset_index()
    df_comp_cat['Executado'] = df_comp_cat['Orçado'] - df_comp_cat['Saldo']
    
    df_melted = df_comp_cat.melt(id_vars='Categoria', value_vars=['Orçado', 'Executado'], 
                                var_name='Tipo', value_name='Valor')
    
    ordem_categorias = df_comp_cat.sort_values('Orçado', ascending=False)['Categoria'].tolist()

    fig_soma_cat = px.bar(
        df_melted, 
        x='Categoria', 
        y='Valor',
        color='Tipo',
        barmode='group',
        color_discrete_map={'Orçado': '#2196F3', 'Executado': '#00CC96'},
        category_orders={'Categoria': ordem_categorias},
        text='Valor'
    )
    
    fig_soma_cat.update_traces(
        texttemplate='R$ %{y:,.2f}',
        textposition='outside',
        hovertemplate="<b>Categoria:</b> %{x}<br><b>%{customdata[0]}:</b> R$ %{y:,.2f}<extra></extra>",
        customdata=df_melted[['Tipo']]
    )
    
    fig_soma_cat.update_layout(
        xaxis_title="",
        yaxis_title="Valor (R$)",
        height=500,
        legend_title="Legenda",
        separators=',.',
        yaxis=dict(range=[0, df_comp_cat['Orçado'].max() * 1.25])
    )
    st.plotly_chart(fig_soma_cat, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")
    st.subheader("📋 Relatório Detalhado")
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
            "Fonte": st.column_config.TextColumn("Fonte"),
        },
    )

else:
    st.error("Arquivo 'fichas.csv' não encontrado!")