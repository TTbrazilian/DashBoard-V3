import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import plotly.graph_objects as go
import streamlit.components.v1 as components
import random

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="São Tomás de Aquino - Gestão Educação", layout="wide")

# --- ESTILIZAÇÃO E GRADE PADRONIZADA ---
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] ul li div:has(span:contains("Bom Jesus")),
        [data-testid="stSidebarNav"] ul li:has(span:contains("Bom Jesus")),
        [data-testid="stSidebarNav"] ul li:has(span:contains("Penha")),
        [data-testid="stSidebarNav"] ul li:has(span:contains("São José da Barra")) {
            display: none !important;
        }
        
        @keyframes subirBarra {
            from { clip-path: inset(100% 0 0 0); }
            to { clip-path: inset(0% 0 0 0); }
        }
        
        .js-plotly-plot .point path {
            animation: subirBarra 1.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;
            animation-delay: 0.3s; 
            clip-path: inset(100% 0 0 0);
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateX(20px); }
            to { opacity: 1; transform: translateX(0); }
        }

        .stButton button {
            width: 100% !important;
            height: 45px !important;
            padding: 0px !important;
            font-size: 10px !important;
            font-weight: 700 !important;
            border-radius: 4px !important;
            white-space: nowrap !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center;
            animation: slideIn 0.4s ease-out;
        }
        
        .stButton button:focus {
            outline: none !important;
            box-shadow: none !important;
        }

        [data-testid="column"] {
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

pio.templates.default = "plotly_white"
CONFIG_PT = {'displaylogo': False, 'showTips': False}

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

def abreviar_extremo(nome):
    if "📊" in nome: return "GERAL"
    n = nome.upper()
    mapeamento = {
        "IMPOSTO SOBRE A PROPRIEDADE PREDIAL E TERRITORIAL URBANA": "IPTU",
        "IMPOSTO SOBRE TRANSMISSÃO DE BENS IMÓVEIS": "ITBI",
        "IMPOSTO SOBRE SERVIÇOS DE QUALQUER NATUREZA": "ISS",
        "IMPOSTO SOBRE A RENDA": "IR",
        "IMPOSTO TERRITORIAL RURAL": "ITR",
        "DÍVIDA ATIVA": "D.A.",
        "CONTRIBUIÇÃO PARA O CUSTEIO DO SERVIÇO DE ILUMINAÇÃO PÚBLICA": "COSIP",
        "CONTRIBUIÇÃO": "CONTRIB."
    }
    for longo, curto in mapeamento.items():
        n = n.replace(longo, curto)
    n = n.replace("PRINCIPAL", "PRIN.")
    n = n.replace("MULTAS E JUROS", "M/J")
    n = n.replace("OUTRAS RECEITAS", "OUTR.")
    if "-" in n:
        partes = n.split("-")
        return f"{partes[0].strip()[:6]} {partes[1].strip()[:5]}"
    return n[:12]

def buscar_arquivo(nome):
    caminhos = [nome, os.path.join("..", nome), os.path.join("pages", nome),
                os.path.join(os.path.dirname(__file__), "..", nome)]
    for p in caminhos:
        if os.path.exists(p): return p
    return None

@st.cache_data
def load_all_data():
    # Atualizado para os arquivos de São Tomás de Aquino
    arquivo_f = "zEducação/São Tomás de Aquino.csv"
    arquivo_r = "zEducação/São Tomás de Aquino_R.csv"
    arquivo_df = "zEducação/São Tomás de Aquino_DF.csv"
    
    path_f, path_r, path_df = buscar_arquivo(arquivo_f), buscar_arquivo(arquivo_r), buscar_arquivo(arquivo_df)
    if not path_f or not path_r or not path_df: return None, None, None
    
    # Processamento do arquivo de Fichas (Hierárquico)
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]: new_cols.append(col[1].strip())
        else: new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols
    
    # Processamento do arquivo de Receitas
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=1)
    df_r.columns = [str(c).strip() for c in df_r.columns]
    
    # Processamento do arquivo consolidado (DF)
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

df_f_raw, df_r, df_df_raw = load_all_data()

if df_f_raw is not None and df_r is not None:
    # --- SIDEBAR ---
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Filtrar Fichas:", "")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Setores")
    if st.sidebar.button("FUNDEB", use_container_width=True): st.session_state.setor = 'FUNDEB'
    if st.sidebar.button("Recursos Próprios", use_container_width=True): st.session_state.setor = 'Recursos Próprios'
    if st.sidebar.button("Recursos Vinculados", use_container_width=True): st.session_state.setor = 'Recursos Vinculados'

    if st.session_state.setor == 'FUNDEB':
        st.markdown("<h1 style='text-align: left;'>📖 São Tomás de Aquino - FUNDEB</h1>", unsafe_allow_html=True)
        def cat_receita(desc):
            desc = desc.upper()
            if 'VAAR' in desc: return 'VAAR'
            if 'ETI' in desc or 'TEMPO INTEGRAL' in desc: return 'ETI'
            if 'APLICAÇÃO' in desc or 'APLICACAO' in desc: return 'Aplicação'
            return 'Principal'
            
        meses_disponiveis = ['Janeiro', 'Fevereiro']
        df_df_fundeb = df_df_raw[(df_df_raw['Fonte'].astype(str).str.contains('15407|15403', na=False))].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb['Fonte'].apply(lambda x: 'FUNDEB 70%' if '15407' in str(x) else 'FUNDEB 30%')
        df_r_fundeb = df_r[(df_r['Categoria'] == 'FUNDEB')].copy()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)
        df_f_fundeb = df_f_raw[df_f_raw['Fonte'].str.contains('540|546', na=False)].copy()
        
        tot_rec_periodo = df_r_fundeb[meses_disponiveis].sum().sum()
        tot_prev_2026 = df_r_fundeb['Orçado Receitas'].sum()
        rec_base_70 = df_r_fundeb[df_r_fundeb['Subcategoria'] != 'VAAR'][meses_disponiveis].sum().sum()
        desp_70_val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & (df_df_fundeb['Tipo'] == 'Liquidado')][meses_disponiveis].sum().sum()
        
        perc_70_indice = (desp_70_val / rec_base_70 * 100) if rec_base_70 > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Previsão Orçamentária Receitas 2026", formar_real(tot_prev_2026))
        with m2: st.metric(f"Total Arrecadado ({meses_disponiveis[0]}-{meses_disponiveis[-1]})", formar_real(tot_rec_periodo))
        with m3:
            if perc_70_indice >= 70: st.metric("Aplicação em Pessoal (Mín. 70%)", f"✅ {perc_70_indice:.2f}%", delta=f"{perc_70_indice-70:.2f}%")
            else: st.metric("Aplicação em Pessoal (Mín. 70%)", f"⚠️ {perc_70_indice:.2f}%", delta=f"{perc_70_indice-70:.2f}%", delta_color="inverse")
        
        st.markdown("---")
        # --- 1. RECEITAS FUNDEB ---
        col_r_h, col_r_b = st.columns([3, 1])
        with col_r_h: st.subheader("🔹 1. Receitas FUNDEB")
        with col_r_b: tipo_r = st.segmented_control("Visualização Receita:", ["Acumulado", "Mensal"], default="Acumulado", key="r_btn")
        
        if tipo_r == "Acumulado":
            df_r_plot = df_r_fundeb.groupby('Subcategoria')[meses_disponiveis].sum().sum(axis=1).reset_index()
            df_r_plot.columns = ['Categoria', 'Valor']
            fig_r = px.bar(df_r_plot, x='Categoria', y='Valor', color='Categoria', text_auto='.2s',
                           color_discrete_map={'Principal':'#002147', 'VAAR':'#003366', 'ETI':'#00509d', 'Aplicação':'#6699cc'})
            fig_r.update_traces(hovertemplate="<b>Categoria:</b> %{x}<br><b>Valor:</b> R$ %{y:,.2f}<extra></extra>")
        else:
            dados_m_r = []
            for m in meses_disponiveis:
                for cat in df_r_fundeb['Subcategoria'].unique():
                    val = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat][m].sum()
                    dados_m_r.append({"Mês": m, "Categoria": cat, "Valor": val})
            fig_r = px.bar(pd.DataFrame(dados_m_r), x='Mês', y='Valor', color='Categoria', text_auto='.2s', barmode='stack',
                           color_discrete_map={'Principal':'#002147', 'VAAR':'#003366', 'ETI':'#00509d', 'Aplicação':'#6699cc'})
            fig_r.update_traces(hovertemplate="<b>Categoria:</b> %{fullData.name}<br><b>Mês:</b> %{x}<br><b>Valor:</b> R$ %{y:,.2f}<extra></extra>")
        
        fig_r.update_layout(separators=",.", yaxis={'showticklabels': False})
        st.plotly_chart(fig_r, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        # --- 2. DESPESAS COM PORCENTAGEM CORRETA ---
        col_f_h, col_f_b = st.columns([3, 1])
        with col_f_h: st.subheader("🔹 2. Despesas FUNDEB")
        with col_f_b: tipo_f = st.segmented_control("Visualização Despesa:", ["Acumulado", "Mensal"], default="Acumulado", key="f_btn")
        
        if tipo_f == "Acumulado":
            total_desp_acum = df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado'][meses_disponiveis].sum().sum()
            df_f_plot = []
            for fonte in ['FUNDEB 70%', 'FUNDEB 30%']:
                val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & (df_df_fundeb['Tipo'] == 'Liquidado')][meses_disponiveis].sum().sum()
                prop = (val / total_desp_acum * 100) if total_desp_acum > 0 else 0
                df_f_plot.append({"Fonte": fonte, "Valor": val, "Proporção": f"{prop:.2f}%"})
            
            fig_f = px.bar(pd.DataFrame(df_f_plot), x='Fonte', y='Valor', color='Fonte', text_auto='.2s',
                           custom_data=['Proporção'],
                           color_discrete_map={'FUNDEB 70%':'#660000', 'FUNDEB 30%':'#cc0000'})
            fig_f.update_traces(hovertemplate="<b>Fonte:</b> %{x}<br><b>Valor:</b> R$ %{y:,.2f}<br><b>% s/ Total Despesas:</b> %{customdata[0]}<extra></extra>")
        else:
            dados_m_f = []
            for m in meses_disponiveis:
                total_desp_mes = df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado'][m].sum()
                for fonte in ['FUNDEB 70%', 'FUNDEB 30%']:
                    val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & (df_df_fundeb['Tipo'] == 'Liquidado')][m].sum()
                    prop = (val / total_desp_mes * 100) if total_desp_mes > 0 else 0
                    dados_m_f.append({"Mês": m, "Fonte": fonte, "Valor": val, "Proporção": f"{prop:.2f}%"})
            
            fig_f = px.bar(pd.DataFrame(dados_m_f), x='Mês', y='Valor', color='Fonte', text_auto='.2s', barmode='stack',
                           custom_data=['Proporção'],
                           color_discrete_map={'FUNDEB 70%':'#660000', 'FUNDEB 30%':'#cc0000'})
            fig_f.update_traces(hovertemplate="<b>Fonte:</b> %{fullData.name}<br><b>Mês:</b> %{x}<br><b>Valor:</b> R$ %{y:,.2f}<br><b>% s/ Despesa do Mês:</b> %{customdata[0]}<extra></extra>")
        
        fig_f.update_layout(separators=",.", yaxis={'showticklabels': False})
        st.plotly_chart(fig_f, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        st.subheader("🔹 3. Comparativo de Aplicação (Índice 70%)")
        tipo_grafico = st.segmented_control("Visualização Comparativo:", ["Total Acumulado", "Mensal"], default="Total Acumulado")
        
        if tipo_grafico == "Total Acumulado":
            df_comp = pd.DataFrame({"Tipo": ["Receitas (Base)", "Despesas (70%)"], "Valor": [rec_base_70, desp_70_val]})
            fig_comp = px.bar(df_comp, x='Tipo', y='Valor', color='Tipo', text_auto='.3s',
                              color_discrete_map={"Receitas (Base)": "#003366", "Despesas (70%)": "#660000"})
            fig_comp.add_hline(y=rec_base_70 * 0.7, line_dash="dot", line_color="green", 
                               annotation_text=f"Meta 70% ({formar_real(rec_base_70 * 0.7)})", annotation_position="top left")
        else:
            dados_m_comp = []
            for m in meses_disponiveis:
                r_m = df_r_fundeb[df_r_fundeb['Subcategoria'] != 'VAAR'][m].sum()
                d_m = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & (df_df_fundeb['Tipo'] == 'Liquidado')][m].sum()
                dados_m_comp.append({"Mês": m, "Tipo": "Receitas (Base)", "Valor": r_m})
                dados_m_comp.append({"Mês": m, "Tipo": "Despesas (70%)", "Valor": d_m})
            fig_comp = px.bar(pd.DataFrame(dados_m_comp), x='Mês', y='Valor', color='Tipo', barmode='group', text_auto='.2s',
                              color_discrete_map={"Receitas (Base)": "#003366", "Despesas (70%)": "#660000"})
        
        fig_comp.update_layout(separators=",.")
        st.plotly_chart(fig_comp, use_container_width=True, config=CONFIG_PT)
        
        st.markdown("### 📋 Relatório de Fichas FUNDEB")
        col_liq_fichas = [c for c in df_f_fundeb.columns if any(m in c for m in meses_disponiveis) and 'Liquidado' in c]
        df_f_fundeb['Soma_Liquidado'] = df_f_fundeb[col_liq_fichas].sum(axis=1)
        df_f_fundeb['Fonte_Agrupada'] = df_f_fundeb['Fonte'].apply(lambda x: 'FUNDEB 70%' if '540' in str(x) else 'FUNDEB 30%')
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

    elif st.session_state.setor == 'Recursos Próprios':
        st.markdown("<h1 style='text-align: left;'>📖 São Tomás de Aquino - Recursos Próprios (25%)</h1>", unsafe_allow_html=True)
        meses_proprios = ['Janeiro', 'Fevereiro']
        df_r_imp = df_r[df_r['Categoria'].astype(str).str.upper().str.contains('IMPOSTO', na=False)].copy()
        df_df_15001 = df_df_raw[df_df_raw['Fonte'].astype(str) == '15001'].copy()
        df_f_15001 = df_f_raw[df_f_raw['Fonte'].str.contains('15001', na=False)].copy()
        
        total_impostos = df_r_imp[meses_proprios].sum().sum()
        total_deducoes = df_r_imp[[c for c in df_r_imp.columns if 'Dedução' in c]].sum().sum()
        base_calculo_25 = total_impostos - total_deducoes
        
        desp_fases = {fase: df_df_15001[df_df_15001['Tipo'] == fase][meses_proprios].sum().sum() for fase in ['Empenhado', 'Liquidado', 'Pago']}
        perc_25 = (desp_fases['Liquidado'] / base_calculo_25 * 100) if base_calculo_25 > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Previsão Orçamentária Receitas 2026", formar_real(df_r_imp['Orçado Receitas'].sum()))
        with m2: st.metric("Total Receitas de Impostos (Jan - Fev)", formar_real(total_impostos))
        with m3:
            if perc_25 >= 25: st.metric("Índice de Aplicação (Mín. 25%)", f"✅ {perc_25:.2f}%", delta=f"{perc_25-25:.2f}%")
            else: st.metric("Índice de Aplicação (Mín. 25%)", f"⚠️ {perc_25:.2f}%", delta=f"{perc_25-25:.2f}%", delta_color="inverse")
            
        st.markdown("---")
        st.subheader("🔹 Receitas de Impostos (Mensal)")
        lista_completa = ["📊 Acumulado Geral"] + df_r_imp['Descrição da Receita'].unique().tolist()
        if 'idx_nav' not in st.session_state: st.session_state.idx_nav = 0
        grid = st.columns([0.5, 1.2, 1.2, 1.2, 1.2, 1.2, 0.5])
        with grid[0]:
            if st.button("◀", key="nav_left"):
                st.session_state.idx_nav = max(0, st.session_state.idx_nav - 5)
                st.rerun()
        fim_idx = min(st.session_state.idx_nav + 5, len(lista_completa))
        fatia = lista_completa[st.session_state.idx_nav:fim_idx]
        for i, item in enumerate(fatia):
            with grid[i+1]:
                label = abreviar_extremo(item)
                if st.button(label, key=f"btn_{item}", help=item, use_container_width=True):
                    st.session_state['rp_ativo'] = item.replace("📊 ", "")
                    st.session_state['trigger_scroll'] = True
                    st.rerun()
        with grid[6]:
            if st.button("▶", key="nav_right"):
                if st.session_state.idx_nav + 5 < len(lista_completa):
                    st.session_state.idx_nav += 5
                    st.rerun()
                    
        if 'rp_ativo' in st.session_state:
            ativo = st.session_state['rp_ativo']
            st.markdown(f"#### 📈 {ativo}")
            df_aux = df_r_imp.copy() if ativo == "Acumulado Geral" else df_r_imp[df_r_imp['Descrição da Receita'] == ativo].copy()
            dados_r_mensal = []
            for m in meses_proprios:
                val_m = df_aux[m].sum()
                ded_m = df_aux[[c for c in df_aux.columns if 'Dedução' in c and m in c]].sum().sum()
                dados_r_mensal.append({"Mês": m, "Tipo": "Receita Mensal", "Valor": val_m})
                dados_r_mensal.append({"Mês": m, "Tipo": "Dedução", "Valor": abs(ded_m)})
            fig_r_prop = px.bar(pd.DataFrame(dados_r_mensal), x='Mês', y='Valor', color='Tipo', barmode='group',
                               color_discrete_map={"Receita Mensal": "#003366", "Dedução": "#6699cc"}, text_auto='.2s')
            fig_r_prop.update_layout(separators=",.", height=450)
            st.plotly_chart(fig_r_prop, use_container_width=True, config=CONFIG_PT, key="grafico_rp_dinamico")
            
        st.markdown("---")
        st.subheader("🔹 Despesas Fonte 15001 (Mensal)")
        dados_d_mensal = []
        for m in meses_proprios:
            for fase in ['Empenhado', 'Liquidado', 'Pago']:
                val_f = df_df_15001[df_df_15001['Tipo'] == fase][m].sum()
                dados_d_mensal.append({"Mês": m, "Fase": fase, "Valor": val_f})
        fig_d_prop = px.bar(pd.DataFrame(dados_d_mensal), x='Mês', y='Valor', color='Fase', barmode='group',
                           color_discrete_map={"Empenhado": "#660000", "Liquidado": "#cc0000", "Pago": "#ff4d4d"}, text_auto='.2s')
        fig_d_prop.update_layout(separators=",.")
        st.plotly_chart(fig_d_prop, use_container_width=True, config=CONFIG_PT)

    elif st.session_state.setor == 'Recursos Vinculados':
        st.markdown("<h1 style='text-align: left;'>📖 São Tomás de Aquino - Recursos Vinculados</h1>", unsafe_allow_html=True)
        meses_vinc = ['Janeiro', 'Fevereiro']
        programas = ['PNAE', 'PNATE', 'PTE', 'QESE']
        mapa_desp = {'PNAE': ['1552', '2552'], 'PNATE': ['1553', '2553'], 'PTE': ['1576', '2576'], 'QESE': ['1550', '2550']}
        todas_fontes_desp = [f for lista in mapa_desp.values() for f in lista]
        
        df_r_vinc = df_r[df_r['Descrição da Receita'].str.upper().str.strip().isin(programas)].copy()
        df_df_vinc = df_df_raw[df_df_raw['Fonte'].astype(str).isin(todas_fontes_desp)].copy()
        
        prev_vinc = df_r_vinc['Orçado Receitas'].sum()
        arrec_vinc = df_r_vinc[meses_vinc].sum().sum()
        liq_vinc = df_df_vinc[df_df_vinc['Tipo'] == 'Liquidado'][meses_vinc].sum().sum()
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Previsão Orçamentária Receitas 2026", formar_real(prev_vinc))
        with m2: st.metric(f"Total Arrecadado ({meses_vinc[0]}-{meses_vinc[-1]})", formar_real(arrec_vinc))
        with m3: st.metric(f"Total Liquidado ({meses_vinc[0]}-{meses_vinc[-1]})", formar_real(liq_vinc))
        
        st.markdown("---")
        st.subheader("🔹 1. Total de Receitas Recebidas")
        dados_r = []
        for m in meses_vinc:
            for prog in programas:
                val = df_r_vinc[df_r_vinc['Descrição da Receita'].str.upper().str.strip() == prog][m].sum()
                if val > 0: dados_r.append({"Mês": m, "Programa": prog, "Valor": val})
        if dados_r:
            fig_rec = px.bar(pd.DataFrame(dados_r), x='Mês', y='Valor', color='Programa', barmode='group', text_auto='.2s',
                            color_discrete_map={'PNAE':'#002147', 'PNATE':'#00509d', 'PTE':'#6699cc', 'QESE':'#99ccff'})
            st.plotly_chart(fig_rec, use_container_width=True, config=CONFIG_PT)
        
        st.subheader("🔹 2. Total de Despesas Liquidadas")
        dados_d = []
        for m in meses_vinc:
            for prog, fontes in mapa_desp.items():
                for f in fontes:
                    val_d = df_df_vinc[(df_df_vinc['Fonte'].astype(str) == f) & (df_df_vinc['Tipo'] == 'Liquidado')][m].sum()
                    if val_d > 0: dados_d.append({"Mês": m, "Programa": prog, "Fonte": f, "Valor": val_d})
        if dados_d:
            fig_desp = px.bar(pd.DataFrame(dados_d), x='Mês', y='Valor', color='Programa', barmode='group', text_auto='.2s',
                             color_discrete_map={'PNAE':'#660000', 'PNATE':'#990000', 'PTE':'#cc0000', 'QESE':'#ff4d4d'})
            st.plotly_chart(fig_desp, use_container_width=True, config=CONFIG_PT)

else:
    st.error("Erro ao carregar os arquivos CSV de São Tomás de Aquino. Verifique se os nomes dos arquivos na pasta zEducação estão corretos.")