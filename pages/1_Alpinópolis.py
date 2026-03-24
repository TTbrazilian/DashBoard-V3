import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Alpinópolis - Gestão Educação", layout="wide")

# --- FILTRO DO MENU LATERAL ---
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

# --- ESTADO DA PÁGINA (CONTROLE DE LAYOUT) ---
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
        if any(k in col for k in ['Orçado', 'Saldo', 'Liquidado', 'Empenhado', 'Pago']):
            df_f[col] = df_f[col].apply(limpar_valor)
    for col in df_r.columns:
        if any(k in col for k in ['Janeiro', 'Fevereiro', 'Março', 'Total', 'Orçado', 'Dedução']):
            df_r[col] = df_r[col].apply(limpar_valor)
            
    df_f['Fonte'] = df_f['Fonte'].astype(str)
    return df_f, df_r

# --- PROCESSAMENTO INICIAL ---
df_f_raw, df_r = load_all_data()

if df_f_raw is not None and df_r is not None:
    # --- SIDEBAR E BOTÕES DE NAVEGAÇÃO ---
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Filtrar:", "")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Setores")
    col_btn1, col_btn2 = st.sidebar.columns(2)
    if col_btn1.button("FUNDEB", use_container_width=True):
        st.session_state.setor = 'FUNDEB'
    if col_btn2.button("Recursos Próprios", use_container_width=True):
        st.session_state.setor = 'Recursos Próprios'

    # --- LÓGICA DE FILTRAGEM ---
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

        def cat_fonte_desp(fonte):
            if '15407' in fonte or ('1540' in fonte and fonte.endswith('7')): return 'Fundeb 70%'
            if '15403' in fonte or ('1540' in fonte and fonte.endswith('3')): return 'Fundeb 30%'
            if '1546' in fonte: return 'Fundeb ETI'
            if '2540' in fonte: return 'Fundeb Superávit'
            return 'Outras Fontes'

        df_r_fundeb = df_r[df_r['Categoria'] == 'FUNDEB'].copy()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)
        df_f_fundeb = df_f[df_f['Fonte'].str.contains('540|546', na=False)].copy()
        df_f_fundeb['Fonte_Agrupada'] = df_f_fundeb['Fonte'].apply(cat_fonte_desp)

        tot_rec_ano = df_r_fundeb['Total'].sum()
        tot_prev_2026 = df_r_fundeb['Orçado Receitas'].sum()
        rec_base_70 = df_r_fundeb[df_r_fundeb['Subcategoria'] != 'VAAR']['Total'].sum()
        col_liq_total = [c for c in df_f.columns if 'Liquidado' in c]
        desp_70_val = df_f_fundeb[df_f_fundeb['Fonte_Agrupada'] == 'Fundeb 70%'][col_liq_total].sum().sum()
        perc_70 = (desp_70_val / rec_base_70 * 100) if rec_base_70 > 0 else 0

        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Previsão Orçamentária 2026", formar_real(tot_prev_2026))
        with m2: st.metric("Total Arrecadado (Jan - Mar)", formar_real(tot_rec_ano))
        with m3: st.metric("Aplicação em Pessoal (70%)", f"{perc_70:.2f}%", delta=f"{perc_70-70:.2f}%")

        st.markdown("---")
        st.subheader("🔹 1. Receitas FUNDEB")
        fig_r_pie = px.pie(df_r_fundeb, values='Total', names='Subcategoria', hole=.4,
                           color_discrete_map={'Principal':'#636EFA', 'VAAR':'#00CC96', 'ETI':'#EF553B', 'Aplicação':'#AB63FA'})
        st.plotly_chart(fig_r_pie, use_container_width=True, config=CONFIG_PT)

        meses = ['Janeiro', 'Fevereiro', 'Março']
        dados_m_r = []
        for m in meses:
            for cat in df_r_fundeb['Subcategoria'].unique():
                val = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat][m].sum()
                dados_m_r.append({"Mês": m, "Categoria": cat, "Valor": val})
        fig_r_bar = px.bar(pd.DataFrame(dados_m_r), x='Mês', y='Valor', color='Categoria', barmode='group')
        st.plotly_chart(fig_r_bar, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        st.subheader("🔹 2. Despesas FUNDEB")
        df_plot_f = df_f_fundeb.groupby('Fonte_Agrupada')['Orçado'].sum().reset_index()
        fig_f_pie = px.pie(df_plot_f, values='Orçado', names='Fonte_Agrupada', hole=.4)
        st.plotly_chart(fig_f_pie, use_container_width=True, config=CONFIG_PT)

        dados_m_f = []
        for m in meses:
            c_liq = f"{m}_Liquidado"
            for fonte in df_f_fundeb['Fonte_Agrupada'].unique():
                val = df_f_fundeb[df_f_fundeb['Fonte_Agrupada'] == fonte][c_liq].sum() if c_liq in df_f_fundeb.columns else 0.0
                dados_m_f.append({"Mês": m, "Fonte": fonte, "Valor": val})
        st.plotly_chart(px.bar(pd.DataFrame(dados_m_f), x='Mês', y='Valor', color='Fonte', barmode='group'), use_container_width=True)

        st.markdown("---")
        st.subheader("🔹 3. Análises e Equilíbrio")
        total_desp_liq = df_f_fundeb[col_liq_total].sum().sum()
        df_comp = pd.DataFrame({"Tipo": ["Total Receitas", "Total Despesas (Liq.)"], "Valor": [tot_rec_ano, total_desp_liq]})
        st.plotly_chart(px.bar(df_comp, x='Tipo', y='Valor', color='Tipo'), use_container_width=True)

        st.markdown("### 📋 Relatório de Fichas FUNDEB (Detalhamento)")
        df_f_final = df_f_fundeb[['Atividade', 'Ficha', 'Fonte_Agrupada', 'Orçado', 'Saldo']].copy()
        for col in ['Orçado', 'Saldo']: df_f_final[col] = df_f_final[col].apply(formar_real)
        st.dataframe(df_f_final, use_container_width=True, hide_index=True)

    # --- PÁGINA: RECURSOS PRÓPRIOS ---
    elif st.session_state.setor == 'Recursos Próprios':
        st.markdown("<h1 style='text-align: left;'>📙 Alpinópolis - Recursos Próprios (Educação)</h1>", unsafe_allow_html=True)
        
        # Filtro de dados específicos
        df_r_imp = df_r[df_r['Categoria'] == 'IMPOSTOS'].copy()
        df_f_15001 = df_f[df_f['Fonte'].str.contains('15001', na=False)].copy()
        
        # Indicadores de Topo
        tot_receita_imp = df_r_imp['Total'].sum()
        tot_deducoes = df_r_imp[[c for c in df_r_imp.columns if 'Dedução' in c or 'DEDUÇÃO' in c.upper()]].sum().sum()
        
        col_liq_15001 = [c for c in df_f_15001.columns if 'Liquidado' in c]
        tot_desp_15001 = df_f_15001[col_liq_15001].sum().sum()
        
        # Cálculo 25% (Lógica: (Receitas - Deduções) * 0.25)
        base_calculo = tot_receita_imp - tot_deducoes
        perc_atual = (tot_desp_15001 / base_calculo * 100) if base_calculo > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Total Receitas de Impostos", formar_real(tot_receita_imp))
        with m2: st.metric("Despesas 15001 (Liq.)", formar_real(tot_desp_15001))
        with m3: st.metric("Percentual dos 25%", f"{perc_atual:.2f}%", delta=f"{perc_atual-25:.2f}%")

        st.markdown("---")
        
        # Receitas
        st.subheader("🔹 1. Análise de Receitas e Impostos")
        meses = ['Janeiro', 'Fevereiro', 'Março']
        
        # Gráfico Receitas Mensais vs Deduções
        dados_rec_mensal = []
        for m in meses:
            val_r = df_r_imp[m].sum()
            # Tenta encontrar coluna de dedução específica do mês (Ex: Janeiro_Dedução)
            col_ded_m = [c for c in df_r_imp.columns if m in c and ('Dedução' in c or 'DEDUÇÃO' in c.upper())]
            val_d = df_r_imp[col_ded_m[0]].sum() if col_ded_m else 0.0
            dados_rec_mensal.append({"Mês": m, "Tipo": "Receita Impostos", "Valor": val_r})
            dados_rec_mensal.append({"Mês": m, "Tipo": "Deduções", "Valor": val_d})
        
        st.plotly_chart(px.bar(pd.DataFrame(dados_rec_mensal), x='Mês', y='Valor', color='Tipo', barmode='group', title="Receitas vs Deduções Mensais"), use_container_width=True)

        # Despesas
        st.subheader("🔹 2. Despesas Fonte 15001 (Mensal)")
        dados_desp_15001 = []
        for m in meses:
            for tipo in ['Empenhado', 'Liquidado', 'Pago']:
                col = f"{m}_{tipo}"
                val = df_f_15001[col].sum() if col in df_f_15001.columns else 0.0
                dados_desp_15001.append({"Mês": m, "Tipo": tipo, "Valor": val})
        
        st.plotly_chart(px.bar(pd.DataFrame(dados_desp_15001), x='Mês', y='Valor', color='Tipo', barmode='group', title="Movimentação Fonte 15001"), use_container_width=True)

        # Análise 25%
        st.subheader("🔹 3. Análise do Mínimo Constitucional (25%)")
        df_ana_25 = pd.DataFrame({
            "Descrição": ["Receitas (Bruto)", "Deduções", "Investimento Educação (15001)"],
            "Valor": [tot_receita_imp, tot_deducoes, tot_desp_15001]
        })
        fig_25 = px.bar(df_ana_25, x='Descrição', y='Valor', color='Descrição', text_auto='.2s')
        st.plotly_chart(fig_25, use_container_width=True)

else:
    st.error("Erro ao carregar as bases de dados de Alpinópolis.")