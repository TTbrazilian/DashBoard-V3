import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Alpinópolis - FUNDEB", layout="wide")

# --- FILTRO DO MENU LATERAL (CSS) ---
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] ul li div:has(span:contains("Bom Jesus")),
        [data-testid="stSidebarNav"] ul li:has(span:contains("Bom Jesus")),
        [data-testid="stSidebarNav"] ul li:has(span:contains("Penha")) {
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

df_f_raw, df_r = load_all_data()

if df_f_raw is not None and df_r is not None:
    # --- BARRA LATERAL ---
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Pesquisar na Planilha:", "")
    df_f = df_f_raw.copy()
    if search_term:
        mask = (df_f['Atividade'].str.contains(search_term, case=False, na=False) |
                df_f['Elemento'].str.contains(search_term, case=False, na=False) |
                df_f['Ficha'].astype(str).str.contains(search_term, case=False, na=False))
        df_f = df_f[mask]

    st.markdown("<h1 style='text-align: left;'>📘 Painel FUNDEB - Alpinópolis</h1>", unsafe_allow_html=True)

    # --- LÓGICA DE FILTRAGEM FUNDEB (RECEITAS) ---
    df_r_fundeb = df_r[df_r['Categoria'] == 'FUNDEB'].copy()
    # Mapeamento sugerido: Principal, VAAR, ETI (Baseado na Descrição)
    def categorizar_receita(desc):
        desc = desc.upper()
        if 'VAAR' in desc: return 'VAAR'
        if 'ETI' in desc or 'TEMPO INTEGRAL' in desc: return 'ETI'
        return 'Principal'
    
    df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(categorizar_receita)
    meses = ['Janeiro', 'Fevereiro', 'Março']

    # --- LÓGICA DE FILTRAGEM FUNDEB (DESPESAS) ---
    # Fontes sugeridas: 1540 (70%), 15403 (30%), 1546 (ETI), 2540 (Superávit)
    def categorizar_despesa(fonte):
        if '1540' in fonte and '7' in fonte: return '15407 (70%)'
        if '1540' in fonte and '3' in fonte: return '15403 (30%)'
        if '1546' in fonte: return '1546 (ETI)'
        if '2540' in fonte: return '2540 (Superávit)'
        return 'Outras Fontes FUNDEB'

    df_f_fundeb = df_f[df_f['Fonte'].str.contains('540|546', na=False)].copy()
    df_f_fundeb['Fonte_Agrupada'] = df_f_fundeb['Fonte'].apply(categorizar_despesa)

    # --- INDICADORES (CARDS) ---
    tot_rec_ano = df_r_fundeb['Total'].sum()
    tot_prev_2026 = df_r_fundeb['Orçado Receitas'].sum()
    
    # Cálculo Regra dos 70% (Receita acumulada exceto VAAR vs Despesa 15407)
    rec_base_70 = df_r_fundeb[df_r_fundeb['Subcategoria'] != 'VAAR']['Total'].sum()
    desp_70_total = df_f_fundeb[df_f_fundeb['Fonte_Agrupada'] == '15407 (70%)'][[c for c in df_f.columns if 'Liquidado' in c]].sum().sum()
    perc_70 = (desp_70_total / rec_base_70 * 100) if rec_base_70 > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Arrecadado (Ano)", formar_real(tot_rec_ano))
    c2.metric("Previsto para 2026", formar_real(tot_prev_2026))
    c3.metric("Aplicação em Pessoal (70%)", f"{perc_70:.2f}%", delta=f"{perc_70-70:.2f}%")

    st.markdown("---")

    # --- SEÇÃO 1: RECEITAS ---
    st.subheader("🔹 1. Análise de Receitas FUNDEB")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<p style='text-align: center;'><b>Arrecadação por Categoria</b></p>", unsafe_allow_html=True)
        fig_pie_r = px.pie(df_r_fundeb, values='Total', names='Subcategoria', hole=.4,
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie_r, use_container_width=True, config=CONFIG_PT)
        
    with col2:
        st.markdown("<p style='text-align: center;'><b>Movimentação Mensal (Receitas)</b></p>", unsafe_allow_html=True)
        rec_mensal = []
        for m in meses:
            for sub in df_r_fundeb['Subcategoria'].unique():
                val = df_r_fundeb[df_r_fundeb['Subcategoria'] == sub][m].sum()
                rec_mensal.append({"Mês": m, "Categoria": sub, "Valor": val})
        fig_bar_r = px.bar(pd.DataFrame(rec_mensal), x='Mês', y='Valor', color='Categoria', barmode='stack')
        st.plotly_chart(fig_bar_r, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # --- SEÇÃO 2: DESPESAS ---
    st.subheader("🔹 2. Análise de Despesas FUNDEB")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("<p style='text-align: center;'><b>Distribuição por Fonte</b></p>", unsafe_allow_html=True)
        desp_por_fonte = df_f_fundeb.groupby('Fonte_Agrupada')['Orçado'].sum().reset_index()
        fig_pie_f = px.pie(desp_por_fonte, values='Orçado', names='Fonte_Agrupada', hole=.4,
                          color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pie_f, use_container_width=True, config=CONFIG_PT)

    with col4:
        st.markdown("<p style='text-align: center;'><b>Movimentação Mensal (Despesas)</b></p>", unsafe_allow_html=True)
        desp_mensal = []
        for m in meses:
            col_liq = f"{m}_Liquidado"
            if col_liq in df_f_fundeb.columns:
                for fonte in df_f_fundeb['Fonte_Agrupada'].unique():
                    val = df_f_fundeb[df_f_fundeb['Fonte_Agrupada'] == fonte][col_liq].sum()
                    desp_mensal.append({"Mês": m, "Fonte": fonte, "Valor": val})
        if desp_mensal:
            fig_bar_f = px.bar(pd.DataFrame(desp_mensal), x='Mês', y='Valor', color='Fonte', barmode='stack')
            st.plotly_chart(fig_bar_f, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # --- SEÇÃO 3: COMPARAÇÃO GERAL ---
    st.subheader("🔹 3. Análise Comparativa Final")
    
    comp_data = [
        {"Tipo": "Total Receitas", "Valor": tot_rec_ano},
        {"Tipo": "Total Despesas (Liq.)", "Valor": df_f_fundeb[[c for c in df_f.columns if 'Liquidado' in c]].sum().sum()}
    ]
    fig_comp = px.bar(pd.DataFrame(comp_data), x='Tipo', y='Valor', color='Tipo', text_auto='.2s')
    st.plotly_chart(fig_comp, use_container_width=True)

    # Tabela de conferência rápida
    with st.expander("Ver Detalhamento das Fichas FUNDEB"):
        st.dataframe(df_f_fundeb[['Atividade', 'Ficha', 'Fonte_Agrupada', 'Orçado', 'Saldo']], use_container_width=True)

else:
    st.error("Erro ao carregar as bases de Alpinópolis.")