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
    arquivo_f = "Alpinópolis.csv"
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
    
    # Limpeza de valores
    for col in df_f.columns:
        if any(k in col for k in ['Orçado', 'Saldo', 'Liquidado']):
            df_f[col] = df_f[col].apply(limpar_valor)
    for col in df_r.columns:
        if any(k in col for k in ['Janeiro', 'Fevereiro', 'Março', 'Total', 'Orçado']):
            df_r[col] = df_r[col].apply(limpar_valor)
            
    df_f['Fonte'] = df_f['Fonte'].astype(str)
    df_f['Elemento'] = df_f['Elemento'].astype(str)
    df_f['Atividade'] = df_f['Atividade'].astype(str)
    
    return df_f, df_r

# --- CARREGAMENTO ---
df_f_raw, df_r = load_all_data()

if df_f_raw is not None and df_r is not None:
    # --- BARRA LATERAL ---
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Pesquisar (Atividade, Elemento ou Ficha):", "")
    
    df_f = df_f_raw.copy()
    if search_term:
        mask = (df_f['Atividade'].str.contains(search_term, case=False, na=False) |
                df_f['Elemento'].str.contains(search_term, case=False, na=False) |
                df_f['Ficha'].astype(str).str.contains(search_term, case=False, na=False))
        df_f = df_f[mask]

    # --- TÍTULO PRINCIPAL ---
    st.markdown("<h1 style='text-align: left;'>🎓 Gestão de Recursos - Alpinópolis</h1>", unsafe_allow_html=True)
    
    # --- MÉTRICAS ---
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

    # --- GRÁFICO 1 ---
    st.markdown("<h3 style='text-align: center;'>FUNDEB: Receita Realizada vs Despesa de Pessoal (70%)</h3>", unsafe_allow_html=True)
    meses = ['Janeiro', 'Fevereiro', 'Março'] 
    evol_data = []
    for m in meses:
        if m in df_r.columns:
            rec_m = df_r[df_r['Categoria'] == 'FUNDEB'][m].sum()
            desp_m = df_f_70[f"{m}_Liquidado"].sum() if f"{m}_Liquidado" in df_f_70.columns else 0
            evol_data.append({"Mês": m, "Tipo": "Receita Realizada", "Valor": rec_m})
            evol_data.append({"Mês": m, "Tipo": "Despesa 70%", "Valor": desp_m})
    
    if evol_data:
        fig1 = px.bar(pd.DataFrame(evol_data), x='Mês', y='Valor', color='Tipo', barmode='group',
                      color_discrete_map={"Receita Realizada": "#636EFA", "Despesa 70%": "#00CC96"})
        fig1.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>Valor: R$ %{y:,.2f}<extra></extra>")
        fig1.update_layout(separators=",.", legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02))
        st.plotly_chart(fig1, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # --- GRÁFICO 2 ---
    st.markdown("<h3 style='text-align: center;'>Natureza da Despesa (Custeio x Capital)</h3>", unsafe_allow_html=True)
    df_f['Natureza'] = df_f['Elemento'].apply(lambda x: 'Capital (Invest.)' if str(x).startswith('4.') else 'Custeio (Manut.)')
    res_nat = df_f.groupby('Natureza')['Orçado'].sum().reset_index()
    fig2 = px.pie(res_nat, values='Orçado', names='Natureza', hole=.4,
                  color_discrete_map={'Custeio (Manut.)':'#00CC96', 'Capital (Invest.)':'#EF553B'})
    fig2.update_traces(textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<extra></extra>")
    fig2.update_layout(separators=",.", legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02))
    st.plotly_chart(fig2, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # --- GRÁFICO 3 ---
    st.markdown("<h3 style='text-align: center;'>Maiores Investimentos por Atividade</h3>", unsafe_allow_html=True)
    res_atv = df_f.groupby('Atividade')['Orçado'].sum().sort_values(ascending=False).head(5).reset_index()
    fig3 = px.bar(res_atv, x='Orçado', y='Atividade', orientation='h', color_discrete_sequence=['#636EFA'])
    fig3.update_traces(hovertemplate="<b>%{y}</b><br>Total: R$ %{x:,.2f}<extra></extra>")
    fig3.update_layout(separators=",.", yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig3, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # --- MONITORAMENTO ---
    st.subheader("📋 Monitoramento de Recursos Vinculados")
    c1, c2 = st.columns(2)
    with c1:
        pnae_total = df_f[df_f['Atividade'].str.contains('Alimentação|PNAE', case=False, na=False)]['Orçado'].sum()
        st.info(f"**PNAE (Merenda):** {formar_real(pnae_total)}")
    with c2:
        qse_total = df_f[df_f['Fonte'].str.contains('1550', na=False)]['Orçado'].sum()
        st.success(f"**Salário Educação (QSE):** {formar_real(qse_total)}")

    # --- TABELAS ---
    st.markdown("---")
    st.subheader("📋 Relatório Geral de Fichas")
    df_rel = df_f[['Atividade', 'Ficha', 'Elemento', 'Fonte', 'Orçado', 'Saldo']].copy()
    for c in ['Orçado', 'Saldo']: df_rel[c] = df_rel[c].apply(formar_real)
    st.dataframe(df_rel, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📊 Relatório Geral das Receitas")
    df_r_rel = df_r[['Código', 'Categoria', 'Descrição da Receita', 'Total', 'Orçado Receitas']].copy()
    for c in ['Total', 'Orçado Receitas']: df_r_rel[c] = df_r_rel[c].apply(formar_real)
    st.dataframe(df_r_rel, use_container_width=True, hide_index=True)

    # --- SEÇÃO DINÂMICA DE RECEITAS ---
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Análise Mensal por Receita Específica</h3>", unsafe_allow_html=True)
    
    c_cat, c_desc = st.columns([1, 1])
    with c_cat:
        categorias_disp = sorted(df_r['Categoria'].unique())
        cat_selecionada = st.radio("Selecione a Categoria:", categorias_disp, horizontal=True)
    with c_desc:
        # Correção: Filtra descrições APENAS da categoria selecionada para evitar soma cruzada
        desc_disp = sorted(df_r[df_r['Categoria'] == cat_selecionada]['Descrição da Receita'].unique())
        receita_especifica = st.selectbox("Selecione a Descrição da Receita:", desc_disp)
    
    # Filtro rigoroso: Categoria + Descrição para precisão de 100%
    df_rec_sel = df_r[(df_r['Categoria'] == cat_selecionada) & (df_r['Descrição da Receita'] == receita_especifica)]
    
    evol_rec = [{"Mês": m, "Valor": df_rec_sel[m].sum()} for m in meses if m in df_rec_sel.columns]
    
    if evol_rec:
        fig_rec = px.bar(pd.DataFrame(evol_rec), x='Mês', y='Valor', color_discrete_sequence=['#636EFA'])
        fig_rec.update_traces(hovertemplate="<b>%{x}</b><br>Receita: " + receita_especifica + "<br>Valor: R$ %{y:,.2f}<extra></extra>")
        fig_rec.update_layout(separators=",.", yaxis_title="Valor (R$)", xaxis_title="Mês")
        st.plotly_chart(fig_rec, use_container_width=True, config=CONFIG_PT)

else:
    st.error("Erro ao localizar as bases de dados.")