import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Alpinópolis - FUNDEB", layout="wide")

# --- FILTRO DO MENU LATERAL (OCULTA ITENS DE OUTROS SETORES) ---
# Aqui garantimos que apenas municípios do setor de EDUCAÇÃO apareçam
st.markdown(
    """
    <style>
        /* Esconde especificamente municípios que NÃO são do setor atual (Educação) */
        [data-testid="stSidebarNav"] ul li div:has(span:contains("Bom Jesus")),
        [data-testid="stSidebarNav"] ul li:has(span:contains("Bom Jesus")),
        [data-testid="stSidebarNav"] ul li:has(span:contains("Penha")),
        [data-testid="stSidebarNav"] ul li:has(span:contains("São José da Barra")) {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

pio.templates.default = "plotly_white"
CONFIG_PT = {'displaylogo': False, 'showTips': False}

# --- FUNÇÕES UTILITÁRIAS ---
def limpar_valor(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "-", "R$ 0,00", "0"]:
        return 0.0
    s_valor = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try: return float(s_valor)
    except: return 0.0

def formar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def buscar_arquivo(nome):
    caminhos = [nome, os.path.join("..", nome), os.path.join("pages", nome), 
                os.path.join(os.path.dirname(__file__), "..", nome)]
    for p in caminhos:
        if os.path.exists(p): return p
    return None

@st.cache_data
def load_all_data():
    arquivo_f = "Alpinópolis.csv"
    arquivo_r = "Alpinópolis_R.csv"
    path_f, path_r = buscar_arquivo(arquivo_f), buscar_arquivo(arquivo_r)
    if not path_f or not path_r: return None, None
    
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]: new_cols.append(col[1].strip())
        else: new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols

    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=1)
    df_r.columns = [str(c).strip() for c in df_r.columns]
    
    for col in df_f.columns:
        if any(k in col for k in ['Orçado', 'Saldo', 'Liquidado']):
            df_f[col] = df_f[col].apply(limpar_valor)
    for col in df_r.columns:
        if any(k in col for k in ['Janeiro', 'Fevereiro', 'Março', 'Total', 'Orçado']):
            df_r[col] = df_r[col].apply(limpar_valor)
            
    df_f['Fonte'] = df_f['Fonte'].astype(str)
    return df_f, df_r

# --- PROCESSAMENTO DE DADOS ---
df_f_raw, df_r = load_all_data()

if df_f_raw is not None and df_r is not None:
    # --- FILTROS LATERAIS ---
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Filtrar:", "")
    df_f = df_f_raw.copy()
    if search_term:
        mask = (df_f['Atividade'].str.contains(search_term, case=False, na=False) |
                df_f['Elemento'].str.contains(search_term, case=False, na=False) |
                df_f['Ficha'].astype(str).str.contains(search_term, case=False, na=False))
        df_f = df_f[mask]

    # --- TÍTULO ---
    st.markdown("<h1 style='text-align: left;'>📘 Alpinópolis - FUNDEB</h1>", unsafe_allow_html=True)

    # --- CATEGORIZAÇÃO (REGRAS DA EMPRESA) ---
    def cat_receita(desc):
        desc = desc.upper()
        if 'VAAR' in desc: return 'VAAR'
        if 'ETI' in desc or 'TEMPO INTEGRAL' in desc: return 'ETI'
        return 'Principal'

    def cat_fonte_desp(fonte):
        if '15407' in fonte or ('1540' in fonte and fonte.endswith('7')): return '15407 (70%)'
        if '15403' in fonte or ('1540' in fonte and fonte.endswith('3')): return '15403 (30%)'
        if '1546' in fonte: return '1546 (ETI)'
        if '2540' in fonte: return '2540 (Superávit)'
        return 'Outras Fontes'

    df_r_fundeb = df_r[df_r['Categoria'] == 'FUNDEB'].copy()
    df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)
    
    df_f_fundeb = df_f[df_f['Fonte'].str.contains('540|546', na=False)].copy()
    df_f_fundeb['Fonte_Agrupada'] = df_f_fundeb['Fonte'].apply(cat_fonte_desp)

    # --- INDICADORES (CARDS) ---
    tot_rec_ano = df_r_fundeb['Total'].sum()
    tot_prev_2026 = df_r_fundeb['Orçado Receitas'].sum()
    rec_base_70 = df_r_fundeb[df_r_fundeb['Subcategoria'] != 'VAAR']['Total'].sum()
    col_liq_total = [c for c in df_f.columns if 'Liquidado' in c]
    desp_70_val = df_f_fundeb[df_f_fundeb['Fonte_Agrupada'] == '15407 (70%)'][col_liq_total].sum().sum()
    perc_70 = (desp_70_val / rec_base_70 * 100) if rec_base_70 > 0 else 0

    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Total Arrecadado (Ano)", formar_real(tot_rec_ano))
    with m2: st.metric("Previsão Orçamentária 2026", formar_real(tot_prev_2026))
    with m3: st.metric("Aplicação em Pessoal (70%)", f"{perc_70:.2f}%", delta=f"{perc_70-70:.2f}%")

    st.markdown("---")

    # --- SEÇÃO 1: RECEITAS ---
    st.subheader("🔹 1. Receitas FUNDEB")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<p style='text-align: center;'><b>Distribuição por Categoria</b></p>", unsafe_allow_html=True)
        fig_r_pie = px.pie(df_r_fundeb, values='Total', names='Subcategoria', hole=.4,
                           color_discrete_map={'Principal':'#636EFA', 'VAAR':'#00CC96', 'ETI':'#EF553B'})
        fig_r_pie.update_traces(textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<extra></extra>")
        fig_r_pie.update_layout(separators=",.")
        st.plotly_chart(fig_r_pie, use_container_width=True, config=CONFIG_PT)

    with c2:
        st.markdown("<p style='text-align: center;'><b>Movimentação Mensal Agrupada</b></p>", unsafe_allow_html=True)
        meses = ['Janeiro', 'Fevereiro', 'Março']
        dados_m_r = []
        for m in meses:
            for cat in df_r_fundeb['Subcategoria'].unique():
                val = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat][m].sum()
                dados_m_r.append({"Mês": m, "Categoria": cat, "Valor": val})
        fig_r_bar = px.bar(pd.DataFrame(dados_m_r), x='Mês', y='Valor', color='Categoria', barmode='group',
                           color_discrete_map={'Principal':'#636EFA', 'VAAR':'#00CC96', 'ETI':'#EF553B'})
        fig_r_bar.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>Valor: R$ %{y:,.2f}<extra></extra>")
        fig_r_bar.update_layout(separators=",.", yaxis_title="R$")
        st.plotly_chart(fig_r_bar, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # --- SEÇÃO 2: DESPESAS ---
    st.subheader("🔹 2. Despesas FUNDEB")
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("<p style='text-align: center;'><b>Distribuição por Fonte</b></p>", unsafe_allow_html=True)
        fig_f_pie = px.pie(df_f_fundeb, values='Orçado', names='Fonte_Agrupada', hole=.4)
        fig_f_pie.update_traces(textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Orçado: R$ %{value:,.2f}<extra></extra>")
        fig_f_pie.update_layout(separators=",.")
        st.plotly_chart(fig_f_pie, use_container_width=True, config=CONFIG_PT)

    with c4:
        st.markdown("<p style='text-align: center;'><b>Movimentação Mensal Agrupada</b></p>", unsafe_allow_html=True)
        dados_m_f = []
        for m in meses:
            c_liq = f"{m}_Liquidado"
            if c_liq in df_f_fundeb.columns:
                for fonte in df_f_fundeb['Fonte_Agrupada'].unique():
                    val = df_f_fundeb[df_f_fundeb['Fonte_Agrupada'] == fonte][c_liq].sum()
                    dados_m_f.append({"Mês": m, "Fonte": fonte, "Valor": val})
        if dados_m_f:
            fig_f_bar = px.bar(pd.DataFrame(dados_m_f), x='Mês', y='Valor', color='Fonte', barmode='group')
            fig_f_bar.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>Valor: R$ %{y:,.2f}<extra></extra>")
            fig_f_bar.update_layout(separators=",.", yaxis_title="R$")
            st.plotly_chart(fig_f_bar, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # --- SEÇÃO 3: ANÁLISES E COMPARAÇÃO FINAL ---
    st.subheader("🔹 3. Análises e Equilíbrio")
    
    total_desp_liq = df_f_fundeb[col_liq_total].sum().sum()
    df_comp = pd.DataFrame({
        "Tipo": ["Total Receitas", "Total Despesas (Liq.)"],
        "Valor": [tot_rec_ano, total_desp_liq]
    })
    
    fig_comp = px.bar(df_comp, x='Tipo', y='Valor', color='Tipo', barmode='group',
                      color_discrete_map={"Total Receitas": "#636EFA", "Total Despesas (Liq.)": "#EF553B"})
    
    fig_comp.update_traces(
        texttemplate='R$ %{y:,.2f}', 
        textposition='outside', 
        hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
    )
    fig_comp.update_layout(separators=",.", yaxis_title="R$")
    st.plotly_chart(fig_comp, use_container_width=True, config=CONFIG_PT)

    # Tabela de Conferência
    st.markdown("### 📋 Relatório de Fichas FUNDEB (Detalhamento)")
    df_f_final = df_f_fundeb[['Atividade', 'Ficha', 'Fonte_Agrupada', 'Orçado', 'Saldo']].copy()
    for col in ['Orçado', 'Saldo']: df_f_final[col] = df_f_final[col].apply(formar_real)
    st.dataframe(df_f_final, use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar as bases de dados de Alpinópolis.")