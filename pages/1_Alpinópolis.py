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
    
    # Carregando Fichas (Despesas) - Header duplo
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]: new_cols.append(col[1].strip())
        else: new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols

    # Carregando Receitas
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=1)
    df_r.columns = [str(c).strip() for c in df_r.columns]
    
    # Limpeza Geral
    for df in [df_f, df_r]:
        for col in df.columns:
            if any(k in col for k in ['Orçado', 'Saldo', 'Janeiro', 'Fevereiro', 'Março', 'Total']):
                df[col] = df[col].apply(limpar_valor)
    
    return df_f, df_r

# --- PROCESSAMENTO ---
df_f, df_r = load_all_data()

if df_f is not None and df_r is not None:
    st.title("🎓 Alpinópolis - Gestão Financeira da Educação")
    st.caption("Análise integrada: Receitas vs. Despesas (Baseado no Modelo G35T40)")
    st.markdown("---")

    # --- CÁLCULOS PARA OS LIMITES CONSTITUCIONAIS ---
    # 1. Receita FUNDEB (Base Pág 2 PDF)
    receita_fundeb_total = df_r[df_r['Categoria'] == 'FUNDEB']['Total'].sum()
    
    # 2. Despesa FUNDEB 70% (Base Pág 3 PDF - Pessoal)
    # Filtro: Fonte FUNDEB e Elemento de Pessoal (3.1.90)
    despesa_70 = df_f[
        (df_f['Fonte'].astype(str).str.contains('1540|1500', na=False)) & 
        (df_f['Elemento'].astype(str).str.contains('3.1.90', na=False))
    ][[c for c in df_f.columns if 'Liquidado' in c]].sum().sum()
    
    perc_70 = (despesa_70 / receita_fundeb_total * 100) if receita_fundeb_total > 0 else 0

    # 3. Mínimo 25% (Base Pág 4 PDF)
    # Receita de Impostos e Transferências (Simplificado para o Dashboard)
    receita_impostos = df_r[df_r['Categoria'].isin(['Impostos', 'Transferências'])]['Total'].sum()
    despesa_propria = df_f[df_f['Fonte'].astype(str).str.contains('1500', na=False)][[c for c in df_f.columns if 'Liquidado' in c]].sum().sum()
    
    perc_25 = (despesa_propria / receita_impostos * 100) if receita_impostos > 0 else 0

    # --- SEÇÃO 1: DASHBOARD DE LIMITES ---
    st.subheader("🏛️ Limites Constitucionais e Legais")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric("Aplicação FUNDEB 70%", f"{perc_70:.2f}%", delta=f"{perc_70-70:.2f}%", delta_color="normal")
        st.caption("Mínimo exigido: 70%")

    with m2:
        # Nota: O delta aqui é em relação aos 25% constitucionais
        st.metric("Mínimo Constitucional (25%)", f"{perc_25:.2f}%", delta=f"{perc_25-25:.2f}%")
        st.caption("Base: Impostos + Transferências")

    with m3:
        st.metric("Receita FUNDEB Acumulada", formar_real(receita_fundeb_total))
        st.caption("Total recebido no período")

    st.markdown("---")

    # --- SEÇÃO 2: GRÁFICOS DE EXECUÇÃO (Pág 6 e 7 PDF) ---
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.write("**Despesas por Categoria (Natureza)**")
        df_f['Natureza'] = df_f['Elemento'].apply(lambda x: 'Capital' if '4.4' in str(x) else 'Custeio')
        res_nat = df_f.groupby('Natureza')['Orçado'].sum().reset_index()
        fig_pie = px.pie(res_nat, values='Orçado', names='Natureza', hole=.4, 
                         color_discrete_map={'Custeio':'#00CC96', 'Capital':'#EF553B'})
        st.plotly_chart(fig_pie, use_container_width=True, config=CONFIG_PT)

    with col_dir:
        st.write("**Evolução Mensal: Receita vs Despesa**")
        meses = ['Janeiro', 'Fevereiro', 'Março'] # Expanda conforme seu CSV
        evol_data = []
        for m in meses:
            rec_m = df_r[m].sum()
            desp_m = df_f[[c for c in df_f.columns if f"{m}_Liquidado" in c]].sum().sum()
            evol_data.append({"Mês": m, "Tipo": "Receita", "Valor": rec_m})
            evol_data.append({"Mês": m, "Tipo": "Despesa", "Valor": desp_m})
        
        fig_evol = px.line(pd.DataFrame(evol_data), x='Mês', y='Valor', color='Tipo', markers=True,
                           color_discrete_map={"Receita": "#636EFA", "Despesa": "#00CC96"})
        st.plotly_chart(fig_evol, use_container_width=True, config=CONFIG_PT)

    # --- SEÇÃO 3: DETALHAMENTO PNAE / MERENDA (Pág 10 PDF) ---
    st.markdown("---")
    st.subheader("🍎 Alimentação Escolar (PNAE)")
    df_pnae = df_f[df_f['Atividade'].astype(str).str.contains('Alimentação|Merenda', case=False, na=False)]
    
    if not df_pnae.empty:
        total_pnae = df_pnae['Orçado'].sum()
        st.info(f"Volume de Recursos para Merenda: **{formar_real(total_pnae)}**")
        st.dataframe(df_pnae[['Ficha', 'Atividade', 'Elemento', 'Orçado', 'Saldo']], use_container_width=True, hide_index=True)
    
    # --- RELATÓRIO DE RECEITAS ---
    st.markdown("---")
    with st.expander("📊 Visualizar Detalhamento de Receitas"):
        st.dataframe(df_r[['Código', 'Categoria', 'Descrição da Receita', 'Total', 'Orçado Receitas']], use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar os arquivos 1_Alpinópolis.csv ou Alpinópolis_R.csv")