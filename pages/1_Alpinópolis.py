import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import unicodedata

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Recursos - Alpinópolis", layout="wide")

pio.templates.default = "plotly_white"
CONFIG_PT = {'displaylogo': False, 'showTips': False}

# --- FUNÇÕES UTILITÁRIAS (PADRÃO BOM JESUS) ---
def limpar_valor(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "-", "R$ 0,00", "0"]:
        return 0.0
    s_valor = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try: return float(s_valor)
    except: return 0.0

def formar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def load_all_data():
    dir_at = os.path.dirname(os.path.abspath(__file__))
    path_f = os.path.join(dir_at, '..', 'Alpinópolis.csv')
    path_r = os.path.join(dir_at, '..', 'Alpinópolis_R.csv')
    
    # 1. Despesas (Fichas) - Header duplo
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
    
    return df_f, df_r

# --- LÓGICA DO DASHBOARD ---
df_f, df_r = load_all_data()

if df_f is not None and df_r is not None:
    st.title("🎓 Gestão de Recursos - Alpinópolis")
    st.subheader("Relatório G35T40 - Educação")
    st.markdown("---")

    # --- CÁLCULOS TÉCNICOS (CONFORME PDF) ---
    cols_liq = [c for c in df_f.columns if 'Liquidado' in c]
    
    # A. FUNDEB (Pág 2 e 3 do PDF)
    receita_fundeb = df_r[df_r['Categoria'] == 'FUNDEB']['Total'].sum()
    # Despesa FUNDEB 70 (Pessoal) - Fontes 1540/1500 e Elemento 3.1.90
    df_f_70 = df_f[(df_f['Fonte'].str.contains('1540|1500', na=False)) & (df_f['Elemento'].str.contains('3.1.90', na=False))]
    despesa_70 = df_f_70[cols_liq].sum().sum()
    perc_70 = (despesa_70 / receita_fundeb * 100) if receita_fundeb > 0 else 0

    # B. MÍNIMO CONSTITUCIONAL 25% (Pág 4 e 5 do PDF)
    # Base de cálculo: Impostos + Transferências (Dedução FUNDEB já considerada no Total do CSV)
    receita_base_25 = df_r[df_r['Categoria'].isin(['Impostos', 'Transferências'])]['Total'].sum()
    # Despesa Rec. Próprios (Fonte 1500)
    df_f_25 = df_f[df_f['Fonte'].str.contains('1500', na=False)]
    despesa_25 = df_f_25[cols_liq].sum().sum()
    perc_25 = (despesa_25 / receita_base_25 * 100) if receita_base_25 > 0 else 0

    # --- LAYOUT DE MÉTRICAS ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Aplicação FUNDEB 70%", f"{perc_70:.2f}%", delta=f"{perc_70-70:.2f}%")
        st.caption("Pág 3: Pessoal c/ Rec. FUNDEB")
    with c2:
        st.metric("Mínimo Constitucional (25%)", f"{perc_25:.2f}%", delta=f"{perc_25-25:.2f}%")
        st.caption("Pág 4: Recursos Próprios")
    with c3:
        st.metric("Receita FUNDEB Total", formar_real(receita_fundeb))
        st.caption("Pág 2: FUNDEB + VAAR + ETI")

    st.markdown("---")

    # --- ANÁLISE FUNDEB (Pág 6 do PDF) ---
    st.subheader("📊 FUNDEB: Receita vs Despesa de Pessoal")
    meses_disponiveis = ['Janeiro', 'Fevereiro', 'Março'] # Ajuste conforme evolução dos meses
    evol_fundeb = []
    for m in meses_disponiveis:
        rec_m = df_r[(df_r['Categoria'] == 'FUNDEB')][m].sum()
        desp_m = df_f_70[f"{m}_Liquidado"].sum()
        evol_fundeb.append({"Mês": m, "Tipo": "Receita FUNDEB", "Valor": rec_m})
        evol_fundeb.append({"Mês": m, "Tipo": "Despesa 70%", "Valor": desp_m})
    
    fig_fundeb = px.bar(pd.DataFrame(evol_fundeb), x='Mês', y='Valor', color='Tipo', barmode='group',
                        color_discrete_map={"Receita FUNDEB": "#636EFA", "Despesa 70%": "#00CC96"})
    st.plotly_chart(fig_fundeb, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # --- CUSTEIO VS CAPITAL (Pág 7 do PDF) ---
    col_esq, col_dir = st.columns(2)
    with col_esq:
        st.subheader("📦 Custeio vs Capital")
        df_f['Natureza'] = df_f['Elemento'].apply(lambda x: 'Capital (Invest.)' if '4.4' in str(x) else 'Custeio (Manut.)')
        res_nat = df_f.groupby('Natureza')['Orçado'].sum().reset_index()
        fig_pie = px.pie(res_nat, values='Orçado', names='Natureza', hole=.4,
                         color_discrete_map={'Custeio (Manut.)':'#00CC96', 'Capital (Invest.)':'#EF553B'})
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_dir:
        st.subheader("📑 Top Elementos de Despesa")
        res_ele = df_f.groupby('Elemento')['Orçado'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_bar = px.bar(res_ele, x='Orçado', y='Elemento', orientation='h', color_discrete_sequence=['#00CC96'])
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- DETALHAMENTO PNAE E SALÁRIO EDUCAÇÃO (Pág 10 e 13 do PDF) ---
    st.markdown("---")
    st.subheader("🍎 Alimentação Escolar (PNAE) e Recursos QSE")
    
    # Filtro PNAE (Merenda)
    df_pnae = df_f[df_f['Atividade'].str.contains('Alimentação|Merenda', case=False, na=False)]
    # Filtro Salário Educação (Fonte 1550)
    df_qse = df_f[df_f['Fonte'].str.contains('1550', na=False)]
    
    tab1, tab2 = st.tabs(["Alimentação Escolar", "Salário Educação (QSE)"])
    with tab1:
        st.write(f"Total Orçado PNAE: **{formar_real(df_pnae['Orçado'].sum())}**")
        st.dataframe(df_pnae[['Ficha', 'Atividade', 'Elemento', 'Orçado', 'Saldo']], use_container_width=True, hide_index=True)
    with tab2:
        st.write(f"Total Orçado QSE: **{formar_real(df_qse['Orçado'].sum())}**")
        st.dataframe(df_qse[['Ficha', 'Atividade', 'Elemento', 'Orçado', 'Saldo']], use_container_width=True, hide_index=True)

    # --- RELATÓRIO FINAL (IGUAL BOM JESUS) ---
    st.markdown("---")
    st.subheader("📋 Relatório Geral de Fichas")
    df_final = df_f[['Categoria', 'Atividade', 'Ficha', 'Elemento', 'Fonte', 'Orçado', 'Saldo']].copy()
    for c in ['Orçado', 'Saldo']: df_final[c] = df_final[c].apply(formar_real)
    st.dataframe(df_final, use_container_width=True, hide_index=True)

else:
    st.error("Erro no carregamento das bases de Alpinópolis.")