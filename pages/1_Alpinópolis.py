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
    arquivo_df = "Alpinópolis_DF.csv" 
    
    path_f, path_r, path_df = buscar_arquivo(arquivo_f), buscar_arquivo(arquivo_r), buscar_arquivo(arquivo_df)
    if not path_f or not path_r or not path_df: return None, None, None
    
    # Base de Fichas
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]: new_cols.append(col[1].strip())
        else: new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols

    # Base de Receitas
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=1)
    df_r.columns = [str(c).strip() for c in df_r.columns]

    # Base de Despesa por Fonte (CONSOLIDADO)
    df_df = pd.read_csv(path_df, sep=None, engine='python', encoding='utf-8')
    df_df.columns = [str(c).strip() for c in df_df.columns]

    # Limpeza de valores - Ajustado para capturar "Março " com espaço conforme o CSV
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

# --- PROCESSAMENTO INICIAL ---
df_f_raw, df_r, df_df_raw = load_all_data()

if df_f_raw is not None and df_r is not None:
    # --- SIDEBAR E BOTÕES DE NAVEGAÇÃO ---
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

        col_fonte_df = 'Fonte'
        
        df_df_fundeb = df_df_raw[df_df_raw[col_fonte_df].astype(str).str.contains('15407|15403', na=False)].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb[col_fonte_df].apply(lambda x: 'FUNDEB 70%' if '15407' in str(x) else 'FUNDEB 30%')

        df_r_fundeb = df_r[df_r['Categoria'] == 'FUNDEB'].copy()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)
        
        df_f_fundeb = df_f[df_f['Fonte'].str.contains('540|546', na=False)].copy()
        def cat_fonte_desp(fonte):
            if '15407' in fonte: return 'FUNDEB 70%'
            if '15403' in fonte: return 'FUNDEB 30%'
            if '1546' in fonte: return 'FUNDEB ETI'
            if '2540' in fonte: return 'FUNDEB Superávit'
            return 'Outras Fontes'
        df_f_fundeb['Fonte_Agrupada'] = df_f_fundeb['Fonte'].apply(cat_fonte_desp)

        tot_rec_ano = df_r_fundeb['Total'].sum()
        tot_prev_2026 = df_r_fundeb['Orçado Receitas'].sum()
        rec_base_70 = df_r_fundeb[df_r_fundeb['Subcategoria'] != 'VAAR']['Total'].sum()
        
        desp_70_val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & 
                                   (df_df_fundeb['Tipo'] == 'Liquidado')]['Total'].sum()
        
        perc_70 = (desp_70_val / rec_base_70 * 100) if rec_base_70 > 0 else 0

        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Previsão Orçamentária 2026", formar_real(tot_prev_2026))
        with m2: st.metric("Total Arrecadado (Jan - Mar)", formar_real(tot_rec_ano))
        with m3: st.metric("Aplicação em Pessoal (70%)", f"{perc_70:.2f}%", delta=f"{perc_70-70:.2f}%")

        st.markdown("---")
        st.subheader("🔹 1. Receitas FUNDEB")
        fig_r_pie = px.pie(df_r_fundeb, values='Total', names='Subcategoria', hole=.4,
                           color_discrete_map={'Principal':'#636EFA', 'VAAR':'#00CC96', 'ETI':'#EF553B', 'Aplicação':'#AB63FA'})
        fig_r_pie.update_traces(textinfo='label+percent', hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<extra></extra>")
        fig_r_pie.update_layout(separators=',.')
        st.plotly_chart(fig_r_pie, use_container_width=True, config=CONFIG_PT)

        meses = ['Janeiro', 'Fevereiro', 'Março ']
        dados_m_r = []
        for m in meses:
            for cat in df_r_fundeb['Subcategoria'].unique():
                val = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat][m].sum() if m in df_r_fundeb.columns else 0.0
                dados_m_r.append({"Mês": m.strip(), "Categoria": cat, "Valor": val})
        fig_r_bar = px.bar(pd.DataFrame(dados_m_r), x='Mês', y='Valor', color='Categoria', barmode='group')
        fig_r_bar.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>Valor: R$ %{y:,.2f}<extra></extra>")
        fig_r_bar.update_layout(separators=',.')
        st.plotly_chart(fig_r_bar, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        st.subheader("🔹 2. Despesas FUNDEB (Parcela Liquidada)")
        
        df_plot_f = df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado'].groupby('Fonte_Nome')['Total'].sum().reset_index()
        
        fig_f_pie = px.pie(df_plot_f, values='Total', names='Fonte_Nome', hole=.4,
                           color_discrete_map={'FUNDEB 70%':'#4169E1', 'FUNDEB 30%':'#FF4500'})
        fig_f_pie.update_traces(textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Total Liquidado: R$ %{value:,.2f}<extra></extra>")
        fig_f_pie.update_layout(separators=',.')
        st.plotly_chart(fig_f_pie, use_container_width=True, config=CONFIG_PT)

        dados_m_f = []
        for m in meses:
            for fonte in ['FUNDEB 70%', 'FUNDEB 30%']:
                val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & 
                                   (df_df_fundeb['Tipo'] == 'Liquidado')][m].sum() if m in df_df_fundeb.columns else 0.0
                dados_m_f.append({"Mês": m.strip(), "Fonte": fonte, "Valor": val})
        
        fig_f_bar = px.bar(pd.DataFrame(dados_m_f), x='Mês', y='Valor', color='Fonte', barmode='group')
        fig_f_bar.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>Valor: R$ %{y:,.2f}<extra></extra>")
        fig_f_bar.update_layout(separators=',.')
        st.plotly_chart(fig_f_bar, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        st.subheader("🔹 3. Análises e Equilíbrio")
        total_desp_liq = df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado']['Total'].sum() 
        df_comp = pd.DataFrame({"Tipo": ["Total Receitas", "Total Despesas (Liq.)"], "Valor": [tot_rec_ano, total_desp_liq]})
        fig_comp = px.bar(df_comp, x='Tipo', y='Valor', color='Tipo')
        fig_comp.update_traces(hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>")
        fig_comp.update_layout(separators=',.')
        st.plotly_chart(fig_comp, use_container_width=True, config=CONFIG_PT)

        st.markdown("### 📋 Relatório de Fichas FUNDEB (Detalhamento)")
        col_liq_fichas = [c for c in df_f.columns if 'Liquidado' in c]
        df_f_fundeb['Soma_Liquidado'] = df_f_fundeb[col_liq_fichas].sum(axis=1)
        df_f_final = df_f_fundeb[['Atividade', 'Ficha', 'Fonte_Agrupada', 'Orçado', 'Saldo', 'Soma_Liquidado']].copy()
        for col in ['Orçado', 'Saldo', 'Soma_Liquidado']: df_f_final[col] = df_f_final[col].apply(formar_real)
        st.dataframe(df_f_final, use_container_width=True, hide_index=True)

    # --- PÁGINA: RECURSOS PRÓPRIOS ---
    elif st.session_state.setor == 'Recursos Próprios':
        st.markdown("<h1 style='text-align: left;'>📙 Alpinópolis - Recursos Próprios (Educação)</h1>", unsafe_allow_html=True)
        
        df_r_imp = df_r[df_r['Categoria'] == 'IMPOSTOS'].copy()
        df_df_15001 = df_df_raw[df_df_raw['Fonte'].astype(str) == '15001'].copy()
        
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

        st.markdown("---")
        st.subheader("🔹 1. Análise de Receitas e Impostos")
        meses = ['Janeiro', 'Fevereiro', 'Março ']
        
        dados_rec_mensal = []
        for m in meses:
            val_r = df_r_imp[m].sum() if m in df_r_imp.columns else 0.0
            col_ded_m = [c for c in df_r_imp.columns if m.strip() in c and ('Dedução' in c or 'DEDUÇÃO' in c.upper())]
            val_d = df_r_imp[col_ded_m[0]].sum() if col_ded_m else 0.0
            dados_rec_mensal.append({"Mês": m.strip(), "Tipo": "Receita Impostos", "Valor": val_r})
            dados_rec_mensal.append({"Mês": m.strip(), "Tipo": "Deduções", "Valor": val_d})
        
        fig_rec = px.bar(pd.DataFrame(dados_rec_mensal), x='Mês', y='Valor', color='Tipo', barmode='group', title="Receitas vs Deduções Mensais")
        fig_rec.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>Valor: R$ %{y:,.2f}<extra></extra>")
        fig_rec.update_layout(separators=',.')
        st.plotly_chart(fig_rec, use_container_width=True, config=CONFIG_PT)

        st.subheader("🔹 2. Despesas Fonte 15001 (Mensal)")
        dados_desp_15001 = []
        for m in meses:
            for tipo in ['Empenhado', 'Liquidado', 'Pago']:
                val = df_df_15001[df_df_15001['Tipo'] == tipo][m].sum() if m in df_df_15001.columns else 0.0
                dados_desp_15001.append({"Mês": m.strip(), "Tipo": tipo, "Valor": val})
        
        fig_desp = px.bar(pd.DataFrame(dados_desp_15001), x='Mês', y='Valor', color='Tipo', barmode='group', title="Movimentação Fonte 15001")
        fig_desp.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>Valor: R$ %{y:,.2f}<extra></extra>")
        fig_desp.update_layout(separators=',.')
        st.plotly_chart(fig_desp, use_container_width=True, config=CONFIG_PT)

        st.subheader("🔹 3. Análise do Mínimo Constitucional (25%)")
        df_ana_25 = pd.DataFrame({
            "Descrição": ["Receitas (Bruto)", "Deduções", "Investimento Educação (15001)"],
            "Valor": [tot_receita_imp, tot_deducoes, tot_desp_15001]
        })
        fig_25 = px.bar(df_ana_25, x='Descrição', y='Valor', color='Descrição', text_auto='.2s')
        fig_25.update_traces(hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>")
        fig_25.update_layout(separators=',.')
        st.plotly_chart(fig_25, use_container_width=True, config=CONFIG_PT)

        st.markdown("### 📋 Relatório de Fichas Recursos Próprios (Detalhamento)")
        df_f_15001_fichas = df_f[df_f['Fonte'].str.contains('15001', na=False)].copy()
        df_f_final_rp = df_f_15001_fichas[['Atividade', 'Ficha', 'Fonte', 'Orçado', 'Saldo']].copy()
        for col in ['Orçado', 'Saldo']: df_f_final_rp[col] = df_f_final_rp[col].apply(formar_real)
        st.dataframe(df_f_final_rp, use_container_width=True, hide_index=True)

    # --- PÁGINA: RECURSOS VINCULADOS ---
    elif st.session_state.setor == 'Recursos Vinculados':
        st.markdown("<h1 style='text-align: left;'>🟢 Alpinópolis - Recursos Vinculados</h1>", unsafe_allow_html=True)
        
        pat_vinc = 'PTE|PNATE|PNAE|QESE|SALÁRIO EDUCAÇÃO'
        df_r_vinc = df_r[df_r['Descrição da Receita'].str.contains(pat_vinc, case=False, na=False)].copy()
        df_df_vinc = df_df_raw[df_df_raw['Nomenclatura'].str.contains(pat_vinc, case=False, na=False)].copy()
        
        fontes_vinc = '1550|1551|1552|1553|1569|1570|2550|2551|2552|2553'
        df_f_vinc = df_f[df_f['Fonte'].str.contains(fontes_vinc, na=False)].copy()

        tot_rec_vinc = df_r_vinc['Total'].sum()
        tot_desp_vinc = df_df_vinc[df_df_vinc['Tipo'] == 'Liquidado']['Total'].sum()
        
        m1, m2 = st.columns(2)
        with m1: st.metric("Total Receitas Vinculadas", formar_real(tot_rec_vinc))
        with m2: st.metric("Total Despesas Vinculadas (Liq.)", formar_real(tot_desp_vinc))
        
        st.markdown("---")
        st.subheader("🔹 1. Distribuição de Receitas por Programa")
        if not df_r_vinc.empty:
            fig_vinc_r = px.pie(df_r_vinc, values='Total', names='Descrição da Receita', hole=.4)
            fig_vinc_r.update_traces(textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Receita: R$ %{value:,.2f}<extra></extra>")
            fig_vinc_r.update_layout(separators=',.')
            st.plotly_chart(fig_vinc_r, use_container_width=True, config=CONFIG_PT)
        
        st.subheader("🔹 2. Acompanhamento Mensal (Receita vs Despesa)")
        
        programas = ['QESE', 'PTE', 'PNAE', 'PNATE']
        meses_vinc = ['Janeiro', 'Fevereiro', 'Março ']
        dados_vinc_m = []
        
        for prog in programas:
            df_r_prog = df_r_vinc[df_r_vinc['Descrição da Receita'].str.contains(prog, case=False, na=False)]
            df_d_prog = df_df_vinc[df_df_vinc['Nomenclatura'].str.contains(prog, case=False, na=False)]
            
            for m in meses_vinc:
                r_val = df_r_prog[m].sum() if m in df_r_prog.columns else 0.0
                d_val = df_d_prog[df_d_prog['Tipo'] == 'Liquidado'][m].sum() if m in df_d_prog.columns else 0.0
                
                if r_val > 0:
                    dados_vinc_m.append({"Mês": m.strip(), "Programa": prog, "Tipo": f"Receita ({prog})", "Valor": r_val})
                if d_val > 0:
                    dados_vinc_m.append({"Mês": m.strip(), "Programa": prog, "Tipo": f"Despesa ({prog})", "Valor": d_val})
            
        df_plot_vinc = pd.DataFrame(dados_vinc_m)

        if not df_plot_vinc.empty:
            # Gráfico unificado com barras lado a lado (colorido por Programa/Tipo)
            fig_vinc_bar = px.bar(
                df_plot_vinc, 
                x='Mês', 
                y='Valor', 
                color='Tipo', 
                barmode='group',
                category_orders={"Mês": ["Janeiro", "Fevereiro", "Março"]}
            )
            
            fig_vinc_bar.update_traces(
                hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>Valor: R$ %{y:,.2f}<extra></extra>"
            )
            
            fig_vinc_bar.update_layout(
                separators=',.', 
                yaxis_tickformat=',.2f',
                legend_title_text='Programas e Tipos',
                xaxis_title="Meses do Ano",
                yaxis_title="Valor (R$)"
            )
            
            st.plotly_chart(fig_vinc_bar, use_container_width=True, config=CONFIG_PT)
        else:
            st.info("Sem dados mensais para os programas selecionados.")
        
        st.markdown("### 📋 Detalhamento de Fichas (Recursos Vinculados)")
        if not df_f_vinc.empty:
            df_f_vinc_final = df_f_vinc[['Atividade', 'Ficha', 'Fonte', 'Orçado', 'Saldo']].copy()
            for col in ['Orçado', 'Saldo']: 
                df_f_vinc_final[col] = df_f_vinc_final[col].apply(formar_real)
            st.dataframe(df_f_vinc_final, use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar as bases de dados de Alpinópolis.")