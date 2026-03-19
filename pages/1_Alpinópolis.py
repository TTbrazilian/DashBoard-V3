import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Recursos - Alpinópolis", layout="wide")

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
    arquivo_f = "Educação Gestão de  Recursos Alpinópolis - 2026 - Fichas.csv"
    arquivo_r = "Alpinópolis_R.csv"
    
    path_f = buscar_arquivo(arquivo_f)
    path_r = buscar_arquivo(arquivo_r)
    
    if not path_f or not path_r:
        return None, None
    
    # 1. Despesas (Fichas)
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]: new_cols.append(col[1].strip())
        else: new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols

    # 2. Receitas
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=1)
    df_r.columns = [str(c).strip() for c in df_r.columns]
    
    # Limpeza e Tipagem
    for col in df_f.columns:
        if any(k in col for k in ['Orçado', 'Saldo', 'Liquidado']):
            df_f[col] = df_f[col].apply(limpar_valor)
    
    for col in df_r.columns:
        if any(k in col for k in ['Janeiro', 'Fevereiro', 'Março', 'Total', 'Orçado']):
            df_r[col] = df_r[col].apply(limpar_valor)
            
    df_f['Fonte'] = df_f['Fonte'].astype(str)
    df_f['Elemento'] = df_f['Elemento'].astype(str)
    df_f['Atividade'] = df_f['Atividade'].astype(str)
    df_f['Categoria'] = df_f['Categoria'].astype(str)
    
    return df_f, df_r

# --- CARREGAMENTO ---
df_f_raw, df_r = load_all_data()

if df_f_raw is not None and df_r is not None:
    # --- BARRA LATERAL (FILTRO ÚNICO) ---
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Pesquisar (Atividade, Elemento ou Ficha):", "")

    # Aplicação da Pesquisa Precisa (Afeta todos os cálculos abaixo)
    df_f = df_f_raw.copy()
    if search_term:
        mask = (
            df_f['Atividade'].str.contains(search_term, case=False, na=False) |
            df_f['Elemento'].str.contains(search_term, case=False, na=False) |
            df_f['Ficha'].astype(str).str.contains(search_term, case=False, na=False)
        )
        df_f = df_f[mask]

    # --- TÍTULO PRINCIPAL ---
    st.title("🎓 Gestão de Recursos - Alpinópolis")
    st.subheader("Relatório G35T40 - Educação")
    st.markdown("---")

    # --- MÉTRICAS (LIMITES) ---
    cols_liq = [c for c in df_f.columns if 'Liquidado' in c]
    
    receita_fundeb = df_r[df_r['Categoria'] == 'FUNDEB']['Total'].sum()
    df_f_70 = df_f[(df_f['Fonte'].str.contains('1540|1500', na=False)) & (df_f['Elemento'].str.contains('3.1.90', na=False))]
    despesa_70 = df_f_70[cols_liq].sum().sum()
    perc_70 = (despesa_70 / receita_fundeb * 100) if receita_fundeb > 0 else 0

    receita_base_25 = df_r[df_r['Categoria'].isin(['Impostos', 'Transferências'])]['Total'].sum()
    df_f_25 = df_f[df_f['Fonte'].str.contains('1500', na=False)]
    despesa_25 = df_f_25[cols_liq].sum().sum()
    perc_25 = (despesa_25 / receita_base_25 * 100) if receita_base_25 > 0 else 0

    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Aplicação FUNDEB 70%", f"{perc_70:.2f}%", delta=f"{perc_70-70:.2f}%")
    with m2: st.metric("Mínimo Educação (25%)", f"{perc_25:.2f}%", delta=f"{perc_25-25:.2f}%")
    with m3: st.metric("Receita FUNDEB Total", formar_real(receita_fundeb))
    
    st.markdown("---")

    # --- GRÁFICOS CENTRALIZADOS ---
    
    # 1. Evolução Mensal
    st.markdown("<h3 style='text-align: center;'>Evolução Mensal FUNDEB 70%</h3>", unsafe_allow_html=True)
    meses = ['Janeiro', 'Fevereiro', 'Março'] 
    evol_data = []
    for m in meses:
        if m in df_r.columns:
            rec_m = df_r[df_r['Categoria'] == 'FUNDEB'][m].sum()
            desp_m = df_f_70[f"{m}_Liquidado"].sum() if f"{m}_Liquidado" in df_f_70.columns else 0
            evol_data.append({"Mês": m, "Tipo": "Receita FUNDEB", "Valor": rec_m})
            evol_data.append({"Mês": m, "Tipo": "Despesa 70%", "Valor": desp_m})
    
    if evol_data:
        fig1 = px.bar(pd.DataFrame(evol_data), x='Mês', y='Valor', color='Tipo', barmode='group',
                      color_discrete_map={"Receita FUNDEB": "#636EFA", "Despesa 70%": "#00CC96"})
        fig1.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02))
        _, col_center, _ = st.columns([1, 4, 1])
        with col_center: st.plotly_chart(fig1, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # 2. Natureza da Despesa
    st.markdown("<h3 style='text-align: center;'>Natureza da Despesa (Custeio x Capital)</h3>", unsafe_allow_html=True)
    df_f['Natureza'] = df_f['Elemento'].apply(lambda x: 'Capital (Invest.)' if '4.4' in str(x) else 'Custeio (Manut.)')
    res_nat = df_f.groupby('Natureza')['Orçado'].sum().reset_index()
    fig2 = px.pie(res_nat, values='Orçado', names='Natureza', hole=.4,
                  color_discrete_map={'Custeio (Manut.)':'#00CC96', 'Capital (Invest.)':'#EF553B'})
    fig2.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02))
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center: st.plotly_chart(fig2, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # 3. Top Elementos
    st.markdown("<h3 style='text-align: center;'>Top 5 Elementos de Despesa</h3>", unsafe_allow_html=True)
    res_ele = df_f.groupby('Elemento')['Orçado'].sum().sort_values(ascending=False).head(5).reset_index()
    fig3 = px.bar(res_ele, x='Orçado', y='Elemento', orientation='h', color_discrete_sequence=['#00CC96'])
    fig3.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
    _, col_center, _ = st.columns([1, 4, 1])
    with col_center: st.plotly_chart(fig3, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # --- TABELA DETALHADA ---
    st.subheader("📋 Relatório Detalhado das Fichas")
    df_rel = df_f[['Categoria', 'Atividade', 'Ficha', 'Elemento', 'Fonte', 'Orçado', 'Saldo']].copy()
    for c in ['Orçado', 'Saldo']: df_rel[c] = df_rel[c].apply(formar_real)
    st.dataframe(df_rel, use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar os arquivos na raiz do projeto.")