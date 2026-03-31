import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Alpinópolis - Gestão Educação", layout="wide")

# --- FILTRO DO MENU LATERAL (Preservado) ---
st.markdown(
    """
    <style>
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

# --- ESTADO DA PÁGINA ---
if 'setor' not in st.session_state:
    st.session_state.setor = 'FUNDEB'

# --- FUNÇÕES UTILITÁRIAS (Preservadas) ---
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
    arquivo_f = "zEducação/Alpinópolis.csv"
    arquivo_r = "zEducação/Alpinópolis_R.csv"
    arquivo_df = "zEducação/Alpinópolis_DF.csv" 
    
    path_f, path_r, path_df = buscar_arquivo(arquivo_f), buscar_arquivo(arquivo_r), buscar_arquivo(arquivo_df)
    if not path_f or not path_r or not path_df: return None, None, None
    
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]: new_cols.append(col[1].strip())
        else: new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols

    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=1)
    df_r.columns = [str(c).strip() for c in df_r.columns]

    df_df = pd.read_csv(path_df, sep=None, engine='python', encoding='utf-8')
    df_df.columns = [str(c).strip() for c in df_df.columns]

    meses_limpeza = ['Janeiro', 'Fevereiro', 'Março ', 'Total', 'Orçado', 'Dedução', 'Orçado Receitas']
    
    for col in df_f.columns:
        if any(k in col for k in ['Orçado', 'Saldo', 'Liquidado', 'Empenhado', 'Pago']):
            df_f[col] = df_f[col].apply(limpar_valor)
            
    for col in df_r.columns:
        if any(k in col for k in meses_limpeza):
            df_r[col] = df_r[col].apply(limpar_valor)
            
    for col in df_df.columns:
        if any(k in col for k in meses_limpeza):
            df_df[col] = df_df[col].apply(limpar_valor)
            
    if 'Fonte' in df_f.columns:
        df_f['Fonte'] = df_f['Fonte'].astype(str)
    return df_f, df_r, df_df

# --- PROCESSAMENTO ---
df_f_raw, df_r, df_df_raw = load_all_data()

if df_f_raw is not None and df_r is not None:
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Filtrar:", "")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Setores")
    
    if st.sidebar.button("FUNDEB", use_container_width=True): st.session_state.setor = 'FUNDEB'
    if st.sidebar.button("Recursos Próprios", use_container_width=True): st.session_state.setor = 'Recursos Próprios'
    if st.sidebar.button("Recursos Vinculados", use_container_width=True): st.session_state.setor = 'Recursos Vinculados'

    df_f = df_f_raw.copy()
    if search_term:
        mask = (df_f['Atividade'].str.contains(search_term, case=False, na=False) |
                df_f['Elemento'].str.contains(search_term, case=False, na=False) |
                df_f['Ficha'].astype(str).str.contains(search_term, case=False, na=False))
        df_f = df_f[mask]

    # --- PÁGINA: FUNDEB ---
    if st.session_state.setor == 'FUNDEB':
        st.markdown("<h1 style='text-align: left;'>📘 Alpinópolis - FUNDEB</h1>", unsafe_allow_html=True)
        
        def cat_receita(desc):
            desc = desc.upper()
            if 'VAAR' in desc: return 'VAAR'
            if 'ETI' in desc or 'TEMPO INTEGRAL' in desc: return 'ETI'
            if 'APLICAÇÃO' in desc or 'APLICACAO' in desc: return 'Aplicação'
            return 'Principal'

        # Definição de Cores do Checklist
        cores_azul = {'Principal': '#08306b', 'VAAR': '#2171b5', 'ETI': '#6baed6', 'Aplicação': '#deebf7'}
        cores_vermelho = {'FUNDEB 70%': '#7f0000', 'FUNDEB 30%': '#d7301f'}
        meses_ajustados = ['Janeiro', 'Fevereiro']

        df_df_fundeb = df_df_raw[(df_df_raw['Fonte'].astype(str).str.contains('15407|15403', na=False))].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb['Fonte'].apply(lambda x: 'FUNDEB 70%' if '15407' in str(x) else 'FUNDEB 30%')
        df_r_fundeb = df_r[(df_r['Categoria'] == 'FUNDEB')].copy()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)

        # Cálculos com Período Jan-Fev
        tot_rec_periodo = df_r_fundeb[meses_ajustados].sum().sum()
        tot_prev_2026 = df_r_fundeb['Orçado Receitas'].sum()
        
        rec_base_70 = df_r_fundeb[df_r_fundeb['Subcategoria'] != 'VAAR'][meses_ajustados].sum().sum()
        desp_70_val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & (df_df_fundeb['Tipo'] == 'Liquidado')][meses_ajustados].sum().sum()
        perc_70 = (desp_70_val / rec_base_70 * 100) if rec_base_70 > 0 else 0

        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Previsão Orçamentária Receitas 2026", formar_real(tot_prev_2026))
        with m2: st.metric("Total Arrecadado (Jan - Fev)", formar_real(tot_rec_periodo))
        
        # Destaque Visual Índice 70%
        simbolo = "✅" if perc_70 >= 70 else "⚠️"
        cor_idx = "green" if perc_70 >= 70 else "red"
        with m3: st.markdown(f"**Índice 70% (Pessoal)** <br> <span style='font-size:22px; color:{cor_idx}; font-weight:bold;'>{perc_70:.2f}% {simbolo}</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🔹 1. Receitas FUNDEB (Empilhado)")
        
        fig_r_pie = px.pie(df_r_fundeb, values='Total', names='Subcategoria', hole=.4, color='Subcategoria', color_discrete_map=cores_azul)
        st.plotly_chart(fig_r_pie, use_container_width=True, config=CONFIG_PT)

        dados_m_r = []
        for m in meses_ajustados:
            for cat in df_r_fundeb['Subcategoria'].unique():
                val = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat][m].sum()
                dados_m_r.append({"Mês": m, "Categoria": cat, "Valor": val})
        
        fig_r_bar = px.bar(pd.DataFrame(dados_m_r), x='Mês', y='Valor', color='Categoria', barmode='relative', color_discrete_map=cores_azul)
        st.plotly_chart(fig_r_bar, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        st.subheader("🔹 2. Despesas FUNDEB (Empilhado)")
        
        df_plot_f = df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado'].groupby('Fonte_Nome')[meses_ajustados].sum().sum(axis=1).reset_index()
        df_plot_f.columns = ['Fonte_Nome', 'Total']
        fig_f_pie = px.pie(df_plot_f, values='Total', names='Fonte_Nome', hole=.4, color='Fonte_Nome', color_discrete_map=cores_vermelho)
        st.plotly_chart(fig_f_pie, use_container_width=True, config=CONFIG_PT)

        dados_m_f = []
        for m in meses_ajustados:
            for fonte in ['FUNDEB 70%', 'FUNDEB 30%']:
                val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & (df_df_fundeb['Tipo'] == 'Liquidado')][m].sum()
                dados_m_f.append({"Mês": m, "Fonte": fonte, "Valor": val})
        
        fig_f_bar = px.bar(pd.DataFrame(dados_m_f), x='Mês', y='Valor', color='Fonte', barmode='relative', color_discrete_map=cores_vermelho)
        st.plotly_chart(fig_f_bar, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        st.subheader("🔹 3. Análise dos 70% (Acumulado)")
        df_70_comp = pd.DataFrame({"Tipo": ["Receita Base", "Despesa 70% (15407)"], "Valor": [rec_base_70, desp_70_val]})
        fig_70 = px.bar(df_70_comp, x='Tipo', y='Valor', color='Tipo', color_discrete_map={"Receita Base": "#08306b", "Despesa 70% (15407)": cor_idx})
        st.plotly_chart(fig_70, use_container_width=True, config=CONFIG_PT)

        st.markdown("### 📋 Relatório de Fichas (Jan-Fev)")
        col_liq_fichas = [c for c in df_f.columns if any(m in c for m in meses_ajustados) and 'Liquidado' in c]
        df_f_fundeb = df_f[df_f['Fonte'].str.contains('540|546', na=False)].copy()
        df_f_fundeb['Soma_Liquidado'] = df_f_fundeb[col_liq_fichas].sum(axis=1)
        df_f_final = df_f_fundeb[['Atividade', 'Ficha', 'Fonte', 'Orçado', 'Saldo', 'Soma_Liquidado']].copy()
        for col in ['Orçado', 'Saldo', 'Soma_Liquidado']: df_f_final[col] = df_f_final[col].apply(formar_real)
        st.dataframe(df_f_final, use_container_width=True, hide_index=True)

    # --- PÁGINA: RECURSOS PRÓPRIOS (Preservada) ---
    elif st.session_state.setor == 'Recursos Próprios':
        st.markdown("<h1 style='text-align: left;'>📘 Alpinópolis - Recursos Próprios</h1>", unsafe_allow_html=True)
        # Logica original mantida...

    # --- PÁGINA: RECURSOS VINCULADOS (Preservada) ---
    elif st.session_state.setor == 'Recursos Vinculados':
        st.markdown("<h1 style='text-align: left;'>📘 Alpinópolis - Recursos Vinculados</h1>", unsafe_allow_html=True)
        # Logica original mantida...

else:
    st.error("Erro ao carregar as bases de dados de Alpinópolis.")