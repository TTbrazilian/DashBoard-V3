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

# --- FUNÇÕES UTILITÁRIAS ---
def limpar_valor(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "-", "R$ 0,00", "0"]:
        return 0.0
    # Remove símbolos e garante que o ponto seja o separador decimal
    s_valor = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(s_valor)
    except:
        return 0.0

def formar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def load_all_data():
    dir_at = os.path.dirname(os.path.abspath(__file__))
    path_f = os.path.join(dir_at, '..', 'Alpinópolis.csv')
    path_r = os.path.join(dir_at, '..', 'Alpinópolis_R.csv')
    
    # 1. CARREGANDO FICHAS (DESPESAS)
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    
    # Organiza os nomes das colunas: "Janeiro_Liquidado", "Janeiro_Empenhado", etc.
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]: 
            new_cols.append(col[1].strip())
        else: 
            new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols

    # 2. CARREGANDO RECEITAS
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=1)
    df_r.columns = [str(c).strip() for c in df_r.columns]
    
    # 3. LIMPEZA FORÇADA DE VALORES (Garante que tudo seja Float)
    # Nas Fichas
    for col in df_f.columns:
        if any(k in col for k in ['Orçado', 'Saldo', 'Empenhado', 'Liquidado', 'Pago']):
            df_f[col] = df_f[col].apply(limpar_valor)
            
    # Nas Receitas
    for col in df_r.columns:
        if any(k in col for k in ['Janeiro', 'Fevereiro', 'Março', 'Total', 'Orçado']):
            df_r[col] = df_r[col].apply(limpar_valor)
    
    return df_f, df_r

# --- PROCESSAMENTO ---
try:
    df_f, df_r = load_all_data()

    if df_f is not None and df_r is not None:
        st.title("🎓 Alpinópolis - Gestão Financeira da Educação")
        st.markdown("---")

        # Filtra as colunas de "Liquidado" para os cálculos de execução
        cols_liq = [c for c in df_f.columns if 'Liquidado' in c]

        # --- CÁLCULOS DOS LIMITES ---
        # Receita FUNDEB
        receita_fundeb_total = df_r[df_r['Categoria'] == 'FUNDEB']['Total'].sum()
        
        # Despesa FUNDEB 70% (Fonte 1540 ou 1500 + Elemento Pessoal 3.1.90)
        df_f_fundeb = df_f[
            (df_f['Fonte'].astype(str).str.contains('1540|1500', na=False)) & 
            (df_f['Elemento'].astype(str).str.contains('3.1.90', na=False))
        ]
        despesa_70 = df_f_fundeb[cols_liq].sum().sum()
        perc_70 = (despesa_70 / receita_fundeb_total * 100) if receita_fundeb_total > 0 else 0

        # Mínimo 25% (Fonte 1500)
        receita_impostos = df_r[df_r['Categoria'].isin(['Impostos', 'Transferências'])]['Total'].sum()
        df_f_proprio = df_f[df_f['Fonte'].astype(str).str.contains('1500', na=False)]
        despesa_propria = df_f_proprio[cols_liq].sum().sum()
        perc_25 = (despesa_propria / receita_impostos * 100) if receita_impostos > 0 else 0

        # --- DASHBOARD ---
        st.subheader("🏛️ Limites Constitucionais")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Aplicação FUNDEB 70%", f"{perc_70:.2f}%", delta=f"{perc_70-70:.2f}%")
        with m2:
            st.metric("Mínimo Educação (25%)", f"{perc_25:.2f}%", delta=f"{perc_25-25:.2f}%")
        with m3:
            st.metric("Receita FUNDEB (Total)", formar_real(receita_fundeb_total))

        st.markdown("---")

        # --- GRÁFICOS ---
        c_esq, c_dir = st.columns(2)
        with c_esq:
            st.write("**Natureza da Despesa (Custeio x Capital)**")
            df_f['Natureza'] = df_f['Elemento'].apply(lambda x: 'Capital' if '4.4' in str(x) else 'Custeio')
            res_nat = df_f.groupby('Natureza')['Orçado'].sum().reset_index()
            st.plotly_chart(px.pie(res_nat, values='Orçado', names='Natureza', hole=.4, 
                                 color_discrete_map={'Custeio':'#00CC96', 'Capital':'#EF553B'}), use_container_width=True)

        with c_dir:
            st.write("**Top 5 Maiores Gastos por Elemento**")
            res_ele = df_f.groupby('Elemento')['Orçado'].sum().sort_values(ascending=False).head(5).reset_index()
            st.plotly_chart(px.bar(res_ele, x='Orçado', y='Elemento', orientation='h', color_discrete_sequence=['#636EFA']), use_container_width=True)

        # --- RELATÓRIO ---
        st.markdown("---")
        st.subheader("📋 Relatório Geral de Fichas")
        df_rel = df_f[['Categoria', 'Atividade', 'Ficha', 'Elemento', 'Fonte', 'Orçado', 'Saldo']].copy()
        for c in ['Orçado', 'Saldo']: df_rel[c] = df_rel[c].apply(formar_real)
        st.dataframe(df_rel, use_container_width=True, hide_index=True)

    else:
        st.error("Arquivos não encontrados.")
except Exception as e:
    st.error(f"Erro ao processar dados: {e}")