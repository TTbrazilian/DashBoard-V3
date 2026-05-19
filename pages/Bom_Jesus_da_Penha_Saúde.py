import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import unicodedata
import plotly.graph_objects as go
import streamlit.components.v1 as components
from random import random

st.set_page_config(page_title="Gestão de Recursos - Bom Jesus", layout="wide")

pio.templates.default = "plotly_white"

CONFIG_PT = {
    'displaylogo': False,
    'showTips': False,
}

# ── FUNÇÕES UTILITÁRIAS ───────────────────────────────────────────────────────
def remover_acentos(texto):
    if not texto: return ""
    return "".join(
        c for c in unicodedata.normalize('NFD', str(texto))
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()

def limpar_valor(valor):
    if pd.isna(valor) or str(valor).strip() in ["","−","-","R$ 0,00","0","#REF!"]:
        return 0.0
    s = str(valor).replace('R$','').replace(' ','').replace('.','').replace(',','.')
    try:
        if '(' in s and ')' in s: s = '-' + s.replace('(','').replace(')','')
        return float(s)
    except: return 0.0

def formar_real(valor):
    if valor is None: return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",","X").replace(".",",").replace("X",".")

# ── CARGA DE DADOS ────────────────────────────────────────────────────────────
# Especificidades Bom Jesus da Penha:
# • Bom_Jesus_da_Penha.csv: cabeçalho duplo — header=1 gera colunas corretas.
#   Colunas mensais triplicadas: sem sufixo=Empenhado, .1=Liquidado, .2=Pago.
#   Coluna 'Abril .1' tem espaço antes do ponto (tratado no rename_liquidado).
# • Categorias: Secretaria, Atenção Primária, MAC, Farmácia, Vigilância.
# • Capital identificado por elemento 'Equipamentos e Materiais Permanentes'.
# • Meses disponíveis com liquidação: Janeiro, Fevereiro, Março.
# • Bom_Jesus_da_Penha_DF.csv: estrutura limpa com cols Tipo/Nomenclatura/Fonte.
#   Linha de cabeçalho repetida (Tipo='Tipo') → filtrada.
@st.cache_data
def load_data():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))

    def _buscar(nome):
        candidatos = [
            os.path.join(diretorio_atual, '..', 'zSaúde', nome),
            os.path.join(diretorio_atual, 'zSaúde', nome),
            nome,
        ]
        for p in candidatos:
            if os.path.exists(p): return p
        return None

    path_f  = _buscar("Bom Jesus da Penha.csv")
    path_r  = _buscar("Bom Jesus da Penha R.csv")
    path_df = _buscar("Bom Jesus da Penha DF.csv")
    if not path_f: return None, None, None

    # ── FICHAS ───────────────────────────────────────────────────────────────
    # header=1: primeira linha = meses (Empenhado/Liquidado/Pago), segunda = col names
    df = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=1)
    df.columns = [str(c).strip() for c in df.columns]

    # Limpeza numérica de todas as colunas relevantes
    for col in df.columns:
        if any(k in col for k in [
            'Orçado','Creditado','Anulado','Saldo',
            'Janeiro','Fevereiro','Março','Abril','Maio','Junho',
            'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro','Total'
        ]):
            df[col] = df[col].apply(limpar_valor)

    df['Ficha']    = df['Ficha'].astype(str).str.replace('.0','',regex=False).str.strip()
    df['Fonte']    = df['Fonte'].astype(str).str.replace('.0','',regex=False).str.strip()
    df['Categoria'] = df['Categoria'].astype(str).str.strip()
    df['Elemento']  = df['Elemento'].astype(str).str.strip()

    # Renomeia colunas mensais de Liquidado (.1) para nomes limpos
    # 'Abril .1' tem espaço → tratado via rename explícito
    rename_liq = {
        'Janeiro.1':  'Janeiro_Liq',
        'Fevereiro.1':'Fevereiro_Liq',
        'Março.1':    'Março_Liq',
        'Abril .1':   'Abril_Liq',
        'Maio.1':     'Maio_Liq',
        'Junho.1':    'Junho_Liq',
        'Julho.1':    'Julho_Liq',
        'Agosto.1':   'Agosto_Liq',
        'Setembro.1': 'Setembro_Liq',
        'Outubro.1':  'Outubro_Liq',
        'Novembro.1': 'Novembro_Liq',
        'Dezembro.1': 'Dezembro_Liq',
        'Total.1':    'Total_Liq',
    }
    df = df.rename(columns={k: v for k, v in rename_liq.items() if k in df.columns})

    # Natureza: Capital vs Custeio (sem dependência do código de elemento)
    CAPITAL_ELEM = [
        'Equipamentos e Materiais Permanentes',
        'Obras e Instalações',
        'Aquisição de Imóveis',
    ]
    df['Natureza'] = df['Elemento'].apply(
        lambda x: 'Capital (Invest.)' if x in CAPITAL_ELEM else 'Custeio (Manut.)'
    )

    # ── RECEITAS ─────────────────────────────────────────────────────────────
    df_r = None
    if path_r:
        df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=0)
        df_r.columns = [str(c).strip() for c in df_r.columns]
        MESES = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                 'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
        for col in df_r.columns:
            if col.strip() in MESES + ['Total','Orçado Receitas']:
                df_r[col] = df_r[col].apply(limpar_valor)

    # ── DESPESAS POR FONTE ────────────────────────────────────────────────────
    df_df = None
    if path_df:
        df_df = pd.read_csv(path_df, sep=None, engine='python', encoding='utf-8')
        df_df.columns = [str(c).strip() for c in df_df.columns]
        # Remove linha de cabeçalho repetida (Tipo == 'Tipo')
        df_df = df_df[~df_df['Tipo'].isin(['Tipo'])].copy()
        df_df['Tipo']  = df_df['Tipo'].str.strip()
        df_df['Fonte'] = df_df['Fonte'].astype(str).str.replace('.0','',regex=False).str.strip()
        for col in df_df.columns:
            if col in ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                       'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro','Total']:
                df_df[col] = df_df[col].apply(limpar_valor)

    return df, df_r, df_df

df_raw, df_r, df_df = load_data()

# ── INTERFACE ─────────────────────────────────────────────────────────────────
if df_raw is not None:

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    st.sidebar.header("🔍 Filtros")

    if 'busca' not in st.session_state:
        st.session_state.busca = ""

    busca = st.sidebar.text_input("Filtrar:", value=st.session_state.busca)
    st.session_state.busca = busca

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

    # Oculta municípios de Educação da sidebar
    components.html("""
        <script>
        (function() {
            function esconderEducacao() {
                try {
                    var nav = window.parent.document.querySelector('[data-testid="stSidebarNav"]');
                    if (!nav) return;
                    nav.querySelectorAll('li').forEach(function(item) {
                        if (item.textContent.indexOf('Educação') !== -1) {
                            item.style.setProperty('display', 'none', 'important');
                        }
                    });
                } catch(e) {}
            }
            esconderEducacao();
            [200, 600, 1200].forEach(t => setTimeout(esconderEducacao, t));
        })();
        </script>
    """, height=0)

    # ── FILTRO GLOBAL ─────────────────────────────────────────────────────────
    df_filtrado_global = df_raw.copy()
    if st.session_state.busca:
        termo = remover_acentos(st.session_state.busca)
        categorias_existentes = {
            remover_acentos(cat): cat
            for cat in df_raw['Categoria'].unique() if pd.notna(cat)
        }
        if termo in categorias_existentes:
            mask = df_filtrado_global['Categoria'].apply(remover_acentos) == termo
        else:
            mask = (
                df_filtrado_global['Categoria'].apply(remover_acentos).str.contains(termo, na=False)
                | (df_filtrado_global['Ficha'] == st.session_state.busca.strip())
                | df_filtrado_global['Elemento'].apply(remover_acentos).str.contains(termo, na=False)
                | df_filtrado_global['Fonte'].str.contains(st.session_state.busca.strip(), na=False)
            )
        df_filtrado_global = df_filtrado_global[mask]

    # ── TÍTULO ────────────────────────────────────────────────────────────────
    st.title("📊 Bom Jesus da Penha — Saúde")
    st.markdown("---")

    # ── MÉTRICAS GERAIS ───────────────────────────────────────────────────────
    # Orçado: previsão | Executado = Total_Liq (liquidado real da ficha)
    # Saldo = Orçado - Total_Liq (diferente do 'Saldo' do CSV que usa empenhado)
    orcado_total  = df_filtrado_global['Orçado'].sum()
    liq_total     = df_filtrado_global['Total_Liq'].sum() if 'Total_Liq' in df_filtrado_global.columns else 0.0
    saldo_total   = df_filtrado_global['Saldo'].sum()
    perc_exec     = (liq_total / orcado_total * 100) if orcado_total > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Previsão (Orçado)",      formar_real(orcado_total))
    with c2: st.metric("Saldo Disponível",        formar_real(saldo_total))
    with c3: st.metric("Executado (Liquidado)",   formar_real(liq_total))
    with c4: st.metric("% de Execução",           f"{perc_exec:.2f}%".replace('.',','))

    # ── EVOLUÇÃO MENSAL ───────────────────────────────────────────────────────
    st.subheader("📈 Evolução Mensal da Execução (Liquidado)")

    # Meses disponíveis com coluna _Liq no df
    meses_liq_map = {
        'Janeiro': 'Janeiro_Liq', 'Fevereiro': 'Fevereiro_Liq', 'Março': 'Março_Liq',
        'Abril': 'Abril_Liq', 'Maio': 'Maio_Liq', 'Junho': 'Junho_Liq',
        'Julho': 'Julho_Liq', 'Agosto': 'Agosto_Liq', 'Setembro': 'Setembro_Liq',
        'Outubro': 'Outubro_Liq', 'Novembro': 'Novembro_Liq', 'Dezembro': 'Dezembro_Liq',
    }
    mensal_dados = []
    for mes, col in meses_liq_map.items():
        val = df_filtrado_global[col].sum() if col in df_filtrado_global.columns else 0.0
        mensal_dados.append({"Mês": mes, "Valor": val})
    df_mensal = pd.DataFrame(mensal_dados)

    fig_evolucao = px.line(
        df_mensal, x='Mês', y='Valor', markers=True,
        color_discrete_sequence=["#00CC96"]
    )
    fig_evolucao.update_layout(
        yaxis_tickprefix='R$ ', yaxis_tickformat=',.2f', separators=',.',
        xaxis_title=None, yaxis_title="Liquidado (R$)",
        height=380,
    )
    fig_evolucao.update_traces(
        hovertemplate="<b>%{x}</b><br>Liquidado: R$ %{y:,.2f}<extra></extra>"
    )
    st.plotly_chart(fig_evolucao, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # ── DETALHAMENTO POR ELEMENTO ──────────────────────────────────────────────
    st.markdown('<div id="foco_grafico"></div>', unsafe_allow_html=True)
    st.subheader("📦 Detalhamento por Elemento")

    st.markdown("""
        <style>
        @keyframes subirBarra {
            from { clip-path: inset(100% 0 0 0); }
            to   { clip-path: inset(0% 0 0 0); }
        }
        .js-plotly-plot .point path {
            animation: subirBarra 0.8s cubic-bezier(0.25, 1, 0.5, 1) forwards;
            clip-path: inset(100% 0 0 0);
        }
        </style>
    """, unsafe_allow_html=True)

    elementos_disponiveis = sorted([
        str(x) for x in df_filtrado_global['Elemento'].dropna().unique()
    ])

    if elementos_disponiveis:
        st.write("Selecione um elemento para visualizar o detalhamento:")
        cols_botoes = st.columns(4)
        for i, elemento in enumerate(elementos_disponiveis):
            with cols_botoes[i % 4]:
                if st.button(elemento, use_container_width=True, key=f"btn_detalhamento_fichas_{i}"):
                    st.session_state['elemento_ativo'] = elemento
                    st.rerun()

        if 'elemento_ativo' in st.session_state:
            ele = st.session_state['elemento_ativo']
            scroll_id = random()
            components.html(
                f"""
                <script id="scroll_{scroll_id}">
                    var scroll = () => {{
                        const el = window.parent.document.querySelector('.st-key-detalhamento-fichas');
                        if (el) el.scrollIntoView({{ behavior: "smooth", block: "center" }});
                    }};
                    setTimeout(scroll, 150);
                </script>
                """,
                height=0,
            )

            df_detalhe = (
                df_filtrado_global[df_filtrado_global['Elemento'] == ele]
                .sort_values('Orçado', ascending=False)
                .copy()
            )

            st.subheader(f"📊 Detalhamento de Fichas: {ele}")

            lista_elementos = [remover_acentos(e) for e in df_raw['Elemento'].unique() if pd.notna(e)]
            busca_limpa  = remover_acentos(st.session_state.busca)
            label_hover  = (
                "Categoria" if st.session_state.busca and busca_limpa in lista_elementos
                else ("Elemento" if st.session_state.busca else "Categoria")
            )

            fig_detalhe = px.bar(
                df_detalhe, x='Ficha', y='Orçado',
                color_discrete_sequence=["#00CC96"],
                custom_data=[label_hover, 'Fonte']
            )
            fig_detalhe.update_traces(
                hovertemplate=(
                    f"<b>{label_hover}:</b> %{{customdata[0]}}<br>"
                    "<b>Fonte:</b> %{customdata[1]}<br>"
                    "<b>Valor:</b> R$ %{y:,.2f}<extra></extra>"
                ),
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
            st.plotly_chart(
                fig_detalhe, use_container_width=True, theme=None,
                config=CONFIG_PT, key="detalhamento-fichas"
            )

            if st.button("⬅️ Voltar para Visão Geral"):
                del st.session_state['elemento_ativo']
                st.rerun()

    st.markdown("---")

    # ── CUSTEIO x CAPITAL ─────────────────────────────────────────────────────
    st.subheader("📊 Custeio × Capital")

    df_natureza = (
        df_filtrado_global.groupby('Natureza')['Orçado']
        .sum().reset_index()
    )
    # Garante que ambas as categorias apareçam
    for nat in ['Capital (Invest.)','Custeio (Manut.)']:
        if nat not in df_natureza['Natureza'].values:
            df_natureza = pd.concat(
                [df_natureza, pd.DataFrame({'Natureza':[nat],'Orçado':[0.0]})],
                ignore_index=True
            )

    fig_natureza = px.pie(
        df_natureza, values='Orçado', names='Natureza', hole=.4,
        color='Natureza',
        color_discrete_map={'Custeio (Manut.)':'#00CC96','Capital (Invest.)':'#EF553B'}
    )
    fig_natureza.update_layout(
        margin=dict(t=50, b=50, l=20, r=20), height=450,
        showlegend=True, separators=',.',
        legend=dict(
            orientation="v", yanchor="middle", y=0.5,
            xanchor="left", x=1.05, font=dict(size=16)
        )
    )
    fig_natureza.update_traces(
        textinfo='percent', textposition='inside',
        hovertemplate="<b>Natureza:</b> %{label}<br><b>Valor Total:</b> R$ %{value:,.2f}<extra></extra>"
    )
    _, col_central_1, _ = st.columns([1,2,1])
    with col_central_1:
        st.plotly_chart(fig_natureza, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # ── % DE EXECUÇÃO POR CATEGORIA ───────────────────────────────────────────
    st.subheader("🎯 % de Execução por Categoria")

    df_exec_cat = (
        df_filtrado_global.groupby('Categoria')
        .agg(Orçado=('Orçado','sum'), Liquidado=('Total_Liq','sum'))
        .reset_index()
    )
    df_exec_cat['Perc'] = (
        df_exec_cat['Liquidado'] / df_exec_cat['Orçado'] * 100
    ).fillna(0)
    df_exec_cat = df_exec_cat.sort_values('Perc', ascending=True)

    fig_exec = px.bar(
        df_exec_cat, x='Perc', y='Categoria', orientation='h',
        text='Perc', color='Perc', color_continuous_scale='Greens'
    )
    fig_exec.update_traces(
        texttemplate='%{text:.1f}%', textposition='outside',
        hovertemplate="<b>Categoria:</b> %{y}<br><b>Execução:</b> %{x:.2f}%<extra></extra>"
    )
    fig_exec.update_layout(
        xaxis_title="Liquidado (%)", yaxis_title="",
        coloraxis_showscale=False, height=400,
        separators=',.',
        margin=dict(l=200),
        xaxis=dict(range=[0, 120])
    )
    st.plotly_chart(fig_exec, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # ── ORÇADO × EXECUTADO POR CATEGORIA ──────────────────────────────────────
    st.subheader("💰 Orçado × Executado por Categoria")

    df_comp_cat = (
        df_filtrado_global.groupby('Categoria')
        .agg(Orçado=('Orçado','sum'), Liquidado=('Total_Liq','sum'))
        .reset_index()
    )
    ordem_categorias = df_comp_cat.sort_values('Orçado', ascending=False)['Categoria'].tolist()
    df_melted = df_comp_cat.melt(
        id_vars='Categoria', value_vars=['Orçado','Liquidado'],
        var_name='Tipo', value_name='Valor'
    )

    fig_comp = px.bar(
        df_melted, x='Categoria', y='Valor', color='Tipo',
        barmode='group',
        color_discrete_map={'Orçado':'#2196F3','Liquidado':'#00CC96'},
        category_orders={'Categoria': ordem_categorias},
        text='Valor'
    )
    fig_comp.update_traces(
        texttemplate='R$ %{y:,.2f}', textposition='outside',
        hovertemplate="<b>Categoria:</b> %{x}<br><b>%{data.name}:</b> R$ %{y:,.2f}<extra></extra>"
    )
    fig_comp.update_layout(
        xaxis_title="", yaxis_title="Valor (R$)", height=500,
        legend_title="Legenda", separators=',.',
        yaxis=dict(range=[0, df_comp_cat['Orçado'].max() * 1.25])
    )
    st.plotly_chart(fig_comp, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # ── DESPESAS POR FONTE (DF file) ───────────────────────────────────────────
    if df_df is not None:
        st.subheader("🏦 Execução por Fonte de Recurso")

        meses_disp = ['Janeiro','Fevereiro','Março']
        df_liq_fonte = df_df[df_df['Tipo']=='Liquidado'].copy()
        df_liq_fonte = df_liq_fonte[df_liq_fonte['Nomenclatura'].notna()].copy()
        df_liq_fonte['Total_Liq'] = df_liq_fonte[meses_disp].sum(axis=1)
        df_liq_fonte = df_liq_fonte[df_liq_fonte['Total_Liq'] > 0]

        if not df_liq_fonte.empty:
            fig_fonte = px.bar(
                df_liq_fonte.sort_values('Total_Liq', ascending=True),
                x='Total_Liq', y='Nomenclatura', orientation='h',
                color='Nomenclatura',
                text='Total_Liq',
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_fonte.update_traces(
                texttemplate='R$ %{x:,.2f}', textposition='outside',
                hovertemplate=(
                    "<b>Fonte:</b> %{y}<br>"
                    "<b>Liquidado (Jan–Mar):</b> R$ %{x:,.2f}<extra></extra>"
                )
            )
            fig_fonte.update_layout(
                xaxis_title="Liquidado (R$)", yaxis_title="",
                showlegend=False, height=420, separators=',.',
                margin=dict(r=200, l=20)
            )
            st.plotly_chart(fig_fonte, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

    # ── RELATÓRIO DETALHADO ────────────────────────────────────────────────────
    st.subheader("📋 Relatório Detalhado")

    df_relatorio = df_filtrado_global.copy()
    df_relatorio['Orçado_F']   = df_relatorio['Orçado'].apply(formar_real)
    df_relatorio['Saldo_F']    = df_relatorio['Saldo'].apply(formar_real)
    df_relatorio['Liq_F']      = df_relatorio['Total_Liq'].apply(formar_real)

    st.data_editor(
        df_relatorio[['Categoria','Ficha','Elemento','Fonte','Orçado_F','Liq_F','Saldo_F']],
        use_container_width=True, hide_index=True, disabled=True,
        column_config={
            "Orçado_F":  "Orçado",
            "Liq_F":     "Liquidado",
            "Saldo_F":   "Saldo",
            "Elemento":  st.column_config.TextColumn("Elemento", width="large"),
            "Ficha":     st.column_config.TextColumn("Ficha"),
            "Fonte":     st.column_config.TextColumn("Fonte"),
            "Categoria": st.column_config.TextColumn("Categoria"),
        },
    )

else:
    st.error("Arquivos de dados não encontrados! Verifique a pasta 'zSaúde'.")