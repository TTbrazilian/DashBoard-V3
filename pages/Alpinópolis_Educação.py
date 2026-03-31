import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Alpinópolis - Gestão Educação", layout="wide")

# --- FILTRO DO MENU LATERAL (CSS para ocultar outros municípios) ---
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
    arquivo_f = "zEducação/Alpinópolis.csv"
    arquivo_r = "zEducação/Alpinópolis_R.csv"
    arquivo_df = "zEducação/Alpinópolis_DF.csv" 
    
    path_f, path_r, path_df = buscar_arquivo(arquivo_f), buscar_arquivo(arquivo_r), buscar_arquivo(arquivo_df)
    if not path_f or not path_r or not path_df: return None, None, None
    
    # Tratamento de Header Multinível para Fichas
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]: new_cols.append(col[1].strip())
        else: new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols

    # Base de Receitas
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=1)
    df_r.columns = [str(c).strip() for c in df_r.columns]

    # Base de Despesa por Fonte
    df_df = pd.read_csv(path_df, sep=None, engine='python', encoding='utf-8')
    df_df.columns = [str(c).strip() for c in df_df.columns]

    meses_limpeza = ['Janeiro', 'Fevereiro', 'Março', 'Total', 'Orçado', 'Dedução', 'Orçado Receitas']
    
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

# --- PROCESSAMENTO INICIAL ---
df_f_raw, df_r, df_df_raw = load_all_data()

if df_f_raw is not None and df_r is not None:
    # --- SIDEBAR ---
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Filtrar Fichas:", "")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Setores")
    
    if st.sidebar.button("FUNDEB", use_container_width=True):
        st.session_state.setor = 'FUNDEB'
    if st.sidebar.button("Recursos Próprios", use_container_width=True):
        st.session_state.setor = 'Recursos Próprios'
    if st.sidebar.button("Recursos Vinculados", use_container_width=True):
        st.session_state.setor = 'Recursos Vinculados'

    # --- PÁGINA: FUNDEB ---
    if st.session_state.setor == 'FUNDEB':
        st.markdown("<h1 style='text-align: left;'>📘 Alpinópolis - FUNDEB</h1>", unsafe_allow_html=True)
        
        def cat_receita(desc):
            desc = desc.upper()
            if 'VAAR' in desc: return 'VAAR'
            if 'ETI' in desc or 'TEMPO INTEGRAL' in desc: return 'ETI'
            if 'APLICAÇÃO' in desc or 'APLICACAO' in desc: return 'Aplicação'
            return 'Principal'

        meses_disponiveis = [c for c in df_r.columns if c in ['Janeiro', 'Fevereiro']]
        
        # Filtros de Dados FUNDEB
        df_df_fundeb = df_df_raw[(df_df_raw['Fonte'].astype(str).str.contains('15407|15403', na=False))].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb['Fonte'].apply(lambda x: 'FUNDEB 70%' if '15407' in str(x) else 'FUNDEB 30%')
        
        df_r_fundeb = df_r[(df_r['Categoria'] == 'FUNDEB')].copy()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)
        
        df_f_fundeb = df_f_raw[df_f_raw['Fonte'].str.contains('540|546', na=False)].copy()

        # Cálculos de Métricas
        tot_rec_ano = df_r_fundeb[meses_disponiveis].sum().sum()
        tot_prev_2026 = df_r_fundeb['Orçado Receitas'].sum()
        rec_base_70 = df_r_fundeb[df_r_fundeb['Subcategoria'] != 'VAAR'][meses_disponiveis].sum().sum()
        desp_70_val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & (df_df_fundeb['Tipo'] == 'Liquidado')][meses_disponiveis].sum().sum()
        perc_70 = (desp_70_val / rec_base_70 * 100) if rec_base_70 > 0 else 0

        # --- HEADER EM UMA ÚNICA LINHA ---
        m1, m2, m3 = st.columns(3)
        with m1: 
            st.metric("Previsão Orçamentária 2026", formar_real(tot_prev_2026))
        with m2: 
            st.metric(f"Total Arrecadado ({meses_disponiveis[0]}-{meses_disponiveis[-1]})", formar_real(tot_rec_ano))
        with m3:
            if perc_70 >= 70:
                st.metric("Aplicação em Pessoal (70%)", f"✅ {perc_70:.2f}%", delta=f"{perc_70-70:.2f}%")
            else:
                st.metric("Aplicação em Pessoal (70%)", f"⚠️ {perc_70:.2f}%", delta=f"{perc_70-70:.2f}%", delta_color="inverse")

        st.markdown("---")
        
        # --- GRÁFICOS COM PADRONIZAÇÃO DE CORES ---
        st.subheader("🔹 1. Receitas FUNDEB (Escala de Azul)")
        dados_m_r = []
        for m in meses_disponiveis:
            for cat in df_r_fundeb['Subcategoria'].unique():
                val = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat][m].sum()
                dados_m_r.append({"Mês": m, "Categoria": cat, "Valor": val})
        
        fig_r = px.bar(pd.DataFrame(dados_m_r), x='Mês', y='Valor', color='Categoria', text_auto='.2s', barmode='stack',
                       color_discrete_map={'Principal':'#003366', 'VAAR':'#004080', 'ETI':'#0059b3', 'Aplicação':'#3385ff'})
        st.plotly_chart(fig_r, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        st.subheader("🔹 2. Despesas FUNDEB (Escala de Vermelho)")
        dados_m_f = []
        for m in meses_disponiveis:
            for fonte in ['FUNDEB 70%', 'FUNDEB 30%']:
                val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & (df_df_fundeb['Tipo'] == 'Liquidado')][m].sum()
                dados_m_f.append({"Mês": m, "Fonte": fonte, "Valor": val})
        
        fig_f = px.bar(pd.DataFrame(dados_m_f), x='Mês', y='Valor', color='Fonte', text_auto='.2s', barmode='stack',
                       color_discrete_map={'FUNDEB 70%':'#800000', 'FUNDEB 30%':'#ff4d4d'})
        st.plotly_chart(fig_f, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        st.subheader("🔹 3. Comparativo Acumulado (Receitas x Despesas)")
        df_comp = pd.DataFrame({"Tipo": ["Receitas", "Despesas (70%)"], "Valor": [rec_base_70, desp_70_val]})
        fig_comp = px.bar(df_comp, x='Tipo', y='Valor', color='Tipo', text_auto='.3s',
                          color_discrete_map={"Receitas": "#004080", "Despesas (70%)": "#800000"})
        st.plotly_chart(fig_comp, use_container_width=True, config=CONFIG_PT)

        # --- RELATÓRIO DE FICHAS (CORREÇÃO KEYERROR) ---
        st.markdown("### 📋 Relatório de Fichas FUNDEB")
        col_liq_fichas = [c for c in df_f_fundeb.columns if any(m in c for m in meses_disponiveis) and 'Liquidado' in c]
        df_f_fundeb['Soma_Liquidado'] = df_f_fundeb[col_liq_fichas].sum(axis=1)
        df_f_fundeb['Fonte_Agrupada'] = df_f_fundeb['Fonte'].apply(lambda x: 'FUNDEB 70%' if '540' in str(x) else 'FUNDEB 30%')
        
        # Identificação dinâmica de colunas para evitar erro
        col_orc = next((c for c in df_f_fundeb.columns if 'Orçado' in c), None)
        col_sld = next((c for c in df_f_fundeb.columns if 'Saldo' in c), None)
        
        cols_show = ['Atividade', 'Ficha', 'Fonte_Agrupada']
        if col_orc: cols_show.append(col_orc)
        if col_sld: cols_show.append(col_sld)
        cols_show.append('Soma_Liquidado')

        df_f_final = df_f_fundeb[cols_show].copy()
        for col in [c for c in [col_orc, col_sld, 'Soma_Liquidado'] if c]:
            df_f_final[col] = df_f_final[col].apply(formar_real)
            
        st.dataframe(df_f_final, use_container_width=True, hide_index=True)

    # --- PÁGINA: RECURSOS PRÓPRIOS (Preservada) ---
    elif st.session_state.setor == 'Recursos Próprios':
        st.markdown("<h1 style='text-align: left;'>📘 Alpinópolis - Recursos Próprios</h1>", unsafe_allow_html=True)
        df_r_imp = df_r[(df_r['Categoria'] == 'IMPOSTOS')].copy()
        df_df_15001 = df_df_raw[(df_df_raw['Fonte'].astype(str) == '15001')].copy()
        
        base_calc = df_r_imp['Total'].sum() - df_r_imp[[c for c in df_r_imp.columns if 'Dedução' in c]].sum().sum()
        tot_liq_15001 = df_df_15001[df_df_15001['Tipo'] == 'Liquidado']['Total'].sum()
        perc_25 = (tot_liq_15001 / base_calc * 100) if base_calc > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Base de Cálculo (Impostos)", formar_real(base_calc))
        with m2: st.metric("Despesa 15001 (Liq.)", formar_real(tot_liq_15001))
        with m3: st.metric("Índice 25%", f"{perc_25:.2f}%", delta=f"{perc_25-25:.2f}%")

        df_f_rp = df_f_raw[df_f_raw['Fonte'].str.contains('15001', na=False)].copy()
        col_orc_rp = next((c for c in df_f_rp.columns if 'Orçado' in c), 'Orçado')
        col_sld_rp = next((c for c in df_f_rp.columns if 'Saldo' in c), 'Saldo')
        df_f_rp_f = df_f_rp[['Atividade', 'Ficha', col_orc_rp, col_sld_rp]].copy()
        for c in [col_orc_rp, col_sld_rp]: df_f_rp_f[c] = df_f_rp_f[c].apply(formar_real)
        st.dataframe(df_f_rp_f, use_container_width=True, hide_index=True)

    # --- PÁGINA: RECURSOS VINCULADOS (Preservada) ---
    elif st.session_state.setor == 'Recursos Vinculados':
        st.markdown("<h1 style='text-align: left;'>📘 Alpinópolis - Recursos Vinculados</h1>", unsafe_allow_html=True)
        programas = ['QESE', 'PTE', 'PNAE', 'PNATE']
        df_r_vinc = df_r[df_r['Descrição da Receita'].str.contains('|'.join(programas), case=False, na=False)].copy()
        
        st.metric("Total Receitas Vinculadas", formar_real(df_r_vinc['Total'].sum()))
        fig_vinc = px.pie(df_r_vinc, values='Total', names='Descrição da Receita', hole=.4)
        st.plotly_chart(fig_vinc, use_container_width=True, config=CONFIG_PT)

else:
    st.error("Erro ao carregar as bases de dados de Alpinópolis.")