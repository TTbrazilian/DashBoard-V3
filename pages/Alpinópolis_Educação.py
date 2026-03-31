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
    
    # 1. Ler com header multinível
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    
    # 2. Criar uma lista fixa de nomes combinando Nível 1 + Nível 0 (ex: Orçado_Total)
    fixed_cols = []
    for col in df_f.columns:
        c0, c1 = str(col[0]).strip(), str(col[1]).strip()
        if "Unnamed" in c0: 
            fixed_cols.append(c1) # Colunas base como Ficha, Atividade
        else: 
            fixed_cols.append(f"{c1}_{c0}") # Colunas de valor como Orçado_Total, Saldo_Total
    
    # 3. Forçar os nomes fixos
    df_f.columns = fixed_cols

    # --- RESTANTE DA LEITURA ---
    # Base de Receitas
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=1)
    df_r.columns = [str(c).strip() for c in df_r.columns]

    # Base de Despesa por Fonte
    df_df = pd.read_csv(path_df, sep=None, engine='python', encoding='utf-8')
    df_df.columns = [str(c).strip() for c in df_df.columns]

    # Limpeza de valores (usando os novos nomes fixos para df_f)
    meses_limpeza_r_df = ['Janeiro', 'Fevereiro', 'Março', 'Total', 'Orçado', 'Dedução', 'Orçado Receitas']
    
    # Limpeza específica para df_f usando os nomes fixos gerados (ex: Orçado_Total)
    for col in df_f.columns:
        if any(k in col for k in ['Orçado_', 'Saldo_', 'Liquidado_', 'Empenhado_', 'Pago_']):
            df_f[col] = df_f[col].apply(limpar_valor)
            
    # Limpeza padrão para df_r e df_df
    for col in df_r.columns:
        if any(k in col for k in meses_limpeza_r_df):
            df_r[col] = df_r[col].apply(limpar_valor)
            
    for col in df_df.columns:
        if any(k in col for k in meses_limpeza_r_df):
            df_df[col] = df_df[col].apply(limpar_valor)
            
    if 'Fonte' in df_f.columns:
        df_f['Fonte'] = df_f['Fonte'].astype(str)
    return df_f, df_r, df_df

# --- PROCESSAMENTO INICIAL ---
df_f_raw, df_r, df_df_raw = load_all_data()

if df_f_raw is not None and df_r is not None:
    # --- SIDEBAR ---
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Filtrar:", "")
    
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
        
        # Checklist 1: Atualização de Título Receitas
        st.subheader("Previsão Orçamentária Receitas 2026")

        def cat_receita(desc):
            desc = desc.upper()
            if 'VAAR' in desc: return 'VAAR'
            if 'ETI' in desc or 'TEMPO INTEGRAL' in desc: return 'ETI'
            if 'APLICAÇÃO' in desc or 'APLICACAO' in desc: return 'Aplicação'
            return 'Principal'

        # Checklist 2: Correção de Período (Jan-Fev)
        meses_disponiveis = [c for c in df_r.columns if c in ['Janeiro', 'Fevereiro']]
        
        col_fonte_df = 'Fonte'
        df_df_fundeb = df_df_raw[(df_df_raw[col_fonte_df].astype(str).str.contains('15407|15403', na=False))].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb[col_fonte_df].apply(lambda x: 'FUNDEB 70%' if '15407' in str(x) else 'FUNDEB 30%')
        df_r_fundeb = df_r[(df_r['Categoria'] == 'FUNDEB')].copy()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)
        
        # Filtro de fichas usando a coluna 'Fonte' que definimos como fixa em load_all_data
        df_f_fundeb = df_f_raw[df_f_raw['Fonte'].str.contains('540|546', na=False)].copy()

        # Métricas (Usando Jan-Fev acumulado)
        tot_rec_ano = df_r_fundeb[meses_disponiveis].sum().sum()
        tot_prev_2026 = df_r_fundeb['Orçado Receitas'].sum()
        
        # Checklist 5 (Parte 1): Cálculo Acumulado (Receita Base vs Despesa 15407)
        rec_base_70 = df_r_fundeb[df_r_fundeb['Subcategoria'] != 'VAAR'][meses_disponiveis].sum().sum()
        desp_70_val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & (df_df_fundeb['Tipo'] == 'Liquidado')][meses_disponiveis].sum().sum()
        
        perc_70 = (desp_70_val / rec_base_70 * 100) if rec_base_70 > 0 else 0

        # Cabeçalho de Métricas (Seguindo o padrão visual limpo, sem HTML customizado)
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Previsão Orçamentária Receitas 2026", formar_real(tot_prev_2026))
        with m2: st.metric(f"Total Arrecadado ({meses_disponiveis[0]} - {meses_disponiveis[-1]})", formar_real(tot_rec_ano))
        
        # Checklist 6: Destaque Visual do Índice (Formatação Condicional nativa do st.metric)
        delta_70 = perc_70 - 70
        st.metric("Aplicação em Pessoal (70%)", f"{perc_70:.2f}%", delta=f"{delta_70:.2f}%")

        st.markdown("---")
        # Checklist 3 e 4: Gráficos Empilhados e Padronização de Cores (Azul sóbrio para Receitas)
        st.subheader("🔹 1. Receitas FUNDEB por Categoria (Empilhado - Escala de Azul)")
        
        dados_m_r = []
        for m in meses_disponiveis:
            for cat in df_r_fundeb['Subcategoria'].unique():
                val = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat][m].sum()
                dados_m_r.append({"Mês": m, "Categoria": cat, "Valor": val})
        
        df_plot_r = pd.DataFrame(dados_m_r)
        
        # AJUSTE: Cores em escala de Azul Sóbrio e barmode='stack'
        fig_r_bar = px.bar(df_plot_r, x='Mês', y='Valor', color='Valor', text='Categoria', 
                           barmode='stack', color_continuous_scale='dense')
        
        # Limpeza visual mantendo legenda (Ocultando a barra de cor lateral)
        fig_r_bar.update_layout(separators=',.', showlegend=False, coloraxis_showscale=False)
        fig_r_bar.update_yaxes(title_text="", showticklabels=False) 
        fig_r_bar.update_xaxes(title_text="") 
        fig_r_bar.update_traces(texttemplate='%{y:.2s}', textposition='inside', 
                                hovertemplate="<b>%{x}</b><br>%{text}<br>Valor: R$ %{y:,.2f}<extra></extra>")
        st.plotly_chart(fig_r_bar, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        # Checklist 3 e 4: Gráficos Empilhados e Padronização de Cores (Vermelho sóbrio para Despesas)
        st.subheader("🔹 2. Despesas FUNDEB por Parcela (Empilhado - Escala de Vermelho)")
        
        dados_m_f = []
        for m in meses_disponiveis:
            for fonte in ['FUNDEB 70%', 'FUNDEB 30%']:
                val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & (df_df_fundeb['Tipo'] == 'Liquidado')][m].sum()
                dados_m_f.append({"Mês": m, "Fonte": fonte, "Valor": val})
        
        df_plot_f = pd.DataFrame(dados_m_f)
        
        # AJUSTE: Cores em escala de Vermelho Sóbrio e barmode='stack'
        fig_f_bar = px.bar(df_plot_f, x='Mês', y='Valor', color='Valor', text='Fonte', 
                           barmode='stack', color_continuous_scale='burg')
        
        # Limpeza visual mantendo legenda (Ocultando a barra de cor lateral)
        fig_f_bar.update_layout(separators=',.', showlegend=False, coloraxis_showscale=False)
        fig_f_bar.update_yaxes(title_text="", showticklabels=False)
        fig_f_bar.update_xaxes(title_text="")
        fig_f_bar.update_traces(texttemplate='%{y:.2s}', textposition='inside', 
                                hovertemplate="<b>%{x}</b><br>%{text}<br>Valor: R$ %{y:,.2f}<extra></extra>")
        st.plotly_chart(fig_f_bar, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        # Checklist 5 (Parte 2): Gráfico específico para Análise dos 70% (Acumulado)
        st.subheader("🔹 3. Análise Acumulada do Índice FUNDEB 70% (Jan-Fev)")
        
        # Cor condicional sóbria para o gráfico
        cor_grafico_desp = "#d62728" if perc_70 < 70 else "#2ca02c"
        
        df_70_analise = pd.DataFrame({
            "Tipo": ["Receita Base (VAAR excluído)", "Despesa Pessoal (Liq. 15407)"],
            "Valor": [rec_base_70, desp_70_val]
        })
        
        fig_70 = px.bar(df_70_analise, x='Tipo', y='Valor', color='Tipo', text_auto='.3s',
                        color_discrete_map={"Receita Base (VAAR excluído)": "#1f77b4", "Despesa Pessoal (Liq. 15407)": cor_grafico_desp})
        
        # Limpeza visual mantendo legenda
        fig_70.update_layout(separators=',.', showlegend=True)
        fig_70.update_yaxes(title_text="", showticklabels=False)
        fig_70.update_xaxes(title_text="")
        fig_70.update_traces(hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>")
        st.plotly_chart(fig_70, use_container_width=True, config=CONFIG_PT)

        st.markdown("### 📋 Relatório de Fichas FUNDEB (Jan-Fev)")
        # Lógica de agrupamento e exibição das fichas (utilizando os nomes fixos do multinível)
        
        # Identifica as colunas de Liquidado para Jan e Fev
        col_liq_fichas = [c for c in df_f_fundeb.columns if any(m in c for m in meses_disponiveis) and 'Liquidado_' in c]
        
        # Soma o liquidado acumulado
        df_f_fundeb['Soma_Liquidado'] = df_f_fundeb[col_liq_fichas].sum(axis=1)
        
        # Agrupa Fonte 70/30 (usando a coluna 'Fonte' fixa)
        df_f_fundeb['Fonte_Agrupada'] = df_f_fundeb['Fonte'].apply(lambda x: 'FUNDEB 70%' if '540' in str(x) else 'FUNDEB 30%')
        
        # Define as colunas Orçado e Saldo fixas do multinível
        col_orc = 'Orçado_Total'
        col_sld = 'Saldo_Total'
        
        # Filtra e formata a tabela final
        df_f_final = df_f_fundeb[['Atividade', 'Ficha', 'Fonte_Agrupada', col_orc, col_sld, 'Soma_Liquidado']].copy()
        for col in [col_orc, col_sld, 'Soma_Liquidado']: 
            df_f_final[col] = df_f_final[col].apply(formar_real)
        
        st.dataframe(df_f_final, use_container_width=True, hide_index=True)

    # --- PÁGINA: RECURSOS PRÓPRIOS ---
    elif st.session_state.setor == 'Recursos Próprios':
        st.markdown("<h1 style='text-align: left;'>📘 Alpinópolis - Recursos Próprios</h1>", unsafe_allow_html=True)
        # Código preservado sem alterações
        df_r_imp = df_r[(df_r['Categoria'] == 'IMPOSTOS')].copy()
        df_df_15001 = df_df_raw[(df_df_raw['Fonte'].astype(str) == '15001')].copy()
        tot_receita_imp = df_r_imp['Total'].sum()
        col_deducoes = [c for c in df_r_imp.columns if 'Dedução' in c or 'DEDUÇÃO' in c.upper()]
        tot_deducoes = df_r_imp[col_deducoes].sum().sum()
        tot_desp_15001 = df_df_15001[df_df_15001['Tipo'] == 'Liquidado']['Total'].sum()
        base_calculo = tot_receita_imp - tot_deducoes
        perc_atual = (tot_desp_15001 / base_calculo * 100) if base_calculo > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Total Receitas de Impostos", formar_real(tot_receita_imp))
        with m2: st.metric("Despesas 15001 (Liq.)", formar_real(tot_desp_15001))
        with m3: st.metric("Percentual dos 25%", f"{perc_atual:.2f}%", delta=f"{perc_atual-25:.2f}%")

        meses_rp = [c for c in df_r_imp.columns if c in ['Janeiro', 'Fevereiro', 'Março']]
        dados_rec_mensal = []
        for m in meses_rp:
            val_r = df_r_imp[m].sum()
            dados_rec_mensal.append({"Mês": m, "Tipo": "Receita Impostos", "Valor": val_r})
        
        fig_rec = px.bar(pd.DataFrame(dados_rec_mensal), x='Mês', y='Valor', color='Tipo', barmode='group')
        st.plotly_chart(fig_rec, use_container_width=True, config=CONFIG_PT)

        df_f_15001_fichas = df_f_raw[df_f_raw['Fonte'].str.contains('15001', na=False)].copy()
        
        # Colunas fixas do multinível
        col_orc = 'Orçado_Total'
        col_sld = 'Saldo_Total'
        
        df_f_final_rp = df_f_15001_fichas[['Atividade', 'Ficha', 'Fonte', col_orc, col_sld]].copy()
        for col in [col_orc, col_sld]: 
            df_f_final_rp[col] = df_f_final_rp[col].apply(formar_real)
        st.dataframe(df_f_final_rp, use_container_width=True, hide_index=True)

    # --- PÁGINA: RECURSOS VINCULADOS ---
    elif st.session_state.setor == 'Recursos Vinculados':
        st.markdown("<h1 style='text-align: left;'>📘 Alpinópolis - Recursos Vinculados</h1>", unsafe_allow_html=True)
        # Código preservado sem alterações
        programas = ['QESE', 'PTE', 'PNAE', 'PNATE']
        fontes_vinc = '1550|1551|1552|1553|2550|2551|2552|2553|1569|1570'
        df_r_vinc = df_r[df_r['Descrição da Receita'].str.contains('|'.join(programas), case=False, na=False)].copy()
        df_df_vinc = df_df_raw[df_df_raw['Fonte'].astype(str).str.contains(fontes_vinc, na=False)].copy()
        df_f_vinc = df_f_raw[df_f_raw['Fonte'].str.contains(fontes_vinc, na=False)].copy()

        m1, m2 = st.columns(2)
        with m1: st.metric("Total Receitas Vinculadas", formar_real(df_r_vinc['Total'].sum()))
        with m2: st.metric("Total Despesas Vinculadas (Liq.)", formar_real(df_df_vinc[df_df_vinc['Tipo'] == 'Liquidado']['Total'].sum()))

        df_pie_r = df_r_vinc.groupby('Descrição da Receita')['Total'].sum().reset_index()
        fig_vinc_pie = px.pie(df_pie_r, values='Total', names='Descrição da Receita', hole=.4)
        st.plotly_chart(fig_vinc_pie, use_container_width=True, config=CONFIG_PT)

        # Colunas fixas do multinível
        col_orc = 'Orçado_Total'
        col_sld = 'Saldo_Total'
        
        df_f_vinc_final = df_f_vinc[['Atividade', 'Ficha', 'Fonte', col_orc, col_sld]].copy()
        for col in [col_orc, col_sld]: 
            df_f_vinc_final[col] = df_f_vinc_final[col].apply(formar_real)
        st.dataframe(df_f_vinc_final, use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar as bases de dados de Alpinópolis.")