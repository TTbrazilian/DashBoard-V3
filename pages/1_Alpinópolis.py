import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import unicodedata
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Recursos - Alpinópolis", layout="wide")

# --- TRADUÇÃO GLOBAL DO PLOTLY ---
pio.templates.default = "plotly_white"
CONFIG_PT = {'displaylogo': False, 'showTips': False, 'modeBarButtonsToolTipNames': {}}

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
    caminho = os.path.join(diretorio_atual, '..', 'Alpinópolis.csv')
    if not os.path.exists(caminho):
        caminho = os.path.join(diretorio_atual, 'Alpinópolis.csv')
        if not os.path.exists(caminho): return None
    
    # Lendo com header=[0,1] para lidar com as colunas triplas (Empenhado/Liquidado/Pago)
    df = pd.read_csv(caminho, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    
    # Simplificando os nomes das colunas para facilitar a lógica
    new_cols = []
    for col in df.columns:
        if "Unnamed" in col[0]:
            new_cols.append(col[1].strip())
        else:
            new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df.columns = new_cols
    
    # Limpeza de tipos
    if 'Ficha' in df.columns:
        df['Ficha'] = df['Ficha'].astype(str).str.replace('.0', '', regex=False).str.strip()
    if 'Fonte' in df.columns:
        df['Fonte'] = df['Fonte'].astype(str).str.replace('.0', '', regex=False).str.strip()

    # Limpeza financeira (Orçado e colunas de Liquidado que o PDF prioriza)
    cols_para_limpar = ['Orçado', 'Saldo'] + [c for c in df.columns if 'Liquidado' in c]
    for col in df.columns:
        if any(k in col for k in cols_para_limpar):
            df[col] = df[col].apply(limpar_valor)
            
    return df

# --- CARREGAMENTO ---
df_raw = load_data()

if df_raw is not None:
    # CSS Responsivo
    st.markdown("""
        <style>
        @media (max-width: 768px) {
            [data-testid="stMetricValue"] { font-size: 1.8rem !important; }
            div.stButton > button { width: 100% !important; margin-bottom: 5px; }
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("🎓 Alpinópolis - Gestão da Educação")
    st.markdown("---")

    # --- MÉTRICAS (Pág 3 e 4 do PDF) ---
    orcado_total = df_raw['Orçado'].sum()
    saldo_total = df_raw['Saldo'].sum()
    # No seu CSV, a soma de todos os 'Liquidado' dos meses gera o executado real
    cols_liquidado = [c for c in df_raw.columns if 'Liquidado' in c and any(m in c for m in ['Janeiro', 'Fevereiro', 'Março'])] # etc
    executado_total = df_raw[[c for c in df_raw.columns if 'Liquidado' in c]].sum().sum()
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Previsão Orçamentária", formar_real(orcado_total))
    with c2: st.metric("Total Liquidado (Executado)", formar_real(executado_total))
    with c3: st.metric("Saldo em Fichas", formar_real(saldo_total))

    st.markdown("---")

    # --- ANÁLISE FUNDEB 70% (Pág 3 do PDF) ---
    st.subheader("📊 FUNDEB 70% - Profissionais da Educação")
    # Filtro: Fontes 1540 (FUNDEB 70) ou similar e Elemento de Pessoal (3.1.90)
    df_fundeb = df_raw[df_raw['Fonte'].str.contains('1540|1500', na=False) & df_raw['Elemento'].str.contains('3.1.90', na=False)]
    gasto_fundeb = df_fundeb[[c for c in df_fundeb.columns if 'Liquidado' in c]].sum().sum()
    
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        # Gráfico de barras por mês do FUNDEB 70
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        dados_mes_fundeb = []
        for m in meses:
            col_m = f"{m}_Liquidado"
            if col_m in df_fundeb.columns:
                dados_mes_fundeb.append({"Mês": m, "Valor": df_fundeb[col_m].sum()})
        
        fig_fundeb = px.bar(pd.DataFrame(dados_mes_fundeb), x='Mês', y='Valor', color_discrete_sequence=['#00CC96'], title="Evolução Mensal FUNDEB 70%")
        st.plotly_chart(fig_fundeb, use_container_width=True, config=CONFIG_PT)
    
    with col_f2:
        st.write("**Resumo FUNDEB 70%**")
        st.info(f"Total Acumulado: \n\n {formar_real(gasto_fundeb)}")
        st.caption("Nota: O cálculo de percentual exato requer a importação da aba 'Receitas'.")

    st.markdown("---")

    # --- CUSTEIO VS CAPITAL (Pág 7 do PDF) ---
    st.subheader("📦 Natureza da Despesa (Custeio x Capital)")
    df_raw['Natureza'] = df_raw['Elemento'].apply(lambda x: 'Capital (Invest.)' if any(k in str(x) for k in ['4.4', 'Equipamentos', 'Obras']) else 'Custeio (Manut.)')
    resumo_natureza = df_raw.groupby('Natureza')['Orçado'].sum().reset_index()
    
    fig_nat = px.pie(resumo_natureza, values='Orçado', names='Natureza', hole=.4, color_discrete_map={'Custeio (Manut.)':'#00CC96', 'Capital (Invest.)':'#EF553B'})
    fig_nat.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
    st.plotly_chart(fig_nat, use_container_width=True, config=CONFIG_PT)

    st.markdown("---")

    # --- TOP GASTOS POR ELEMENTO (Pág 8 do PDF) ---
    st.subheader("📑 Maiores Investimentos por Elemento")
    resumo_ele = df_raw.groupby('Elemento')['Orçado'].sum().reset_index().sort_values('Orçado', ascending=False).head(8)
    fig_ele = px.bar(resumo_ele, x='Orçado', y='Elemento', orientation='h', color_discrete_sequence=['#636EFA'])
    fig_ele.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_ele, use_container_width=True, config=CONFIG_PT)

    # --- RELATÓRIO FINAL ---
    st.markdown("---")
    st.subheader("📋 Relatório Detalhado das Fichas")
    df_final = df_raw[['Categoria', 'Atividade', 'Ficha', 'Elemento', 'Fonte', 'Orçado', 'Saldo']].copy()
    for c in ['Orçado', 'Saldo']:
        df_final[c] = df_final[c].apply(formar_real)
    
    st.dataframe(df_final, use_container_width=True, hide_index=True)

else:
    st.error("Arquivo '1_Alpinópolis.csv' não encontrado ou formato inválido.")