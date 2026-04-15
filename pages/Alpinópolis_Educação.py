import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import plotly.graph_objects as go
import streamlit.components.v1 as components
import random

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Alpinópolis - Gestão Educação", layout="wide")

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

# CORREÇÃO 1: Mudar o tema padrão para 'plotly_dark' para escurecer o hover
pio.templates.default = "plotly_dark"
CONFIG_PT = {'displaylogo': False, 'showTips': False}
# Variável auxiliar para garantir o estilo do hover solicitado (Fonte branca, fundo preto, sem labels extras)
HOVER_STYLE = dict(bgcolor="rgba(0,0,0,0.9)", font_size=13, font_family="Arial", font_color="white")

# ORDEM CRONOLÓGICA DOS MESES
ORDEM_MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

if 'setor' not in st.session_state:
    st.session_state.setor = 'FUNDEB'

# --- FUNÇÕES UTILITÁRIAS ---
def limpar_valor(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "-", "R$ 0,00", "0"]:
        return 0.0
    s_valor = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try: 
        if '(' in s_valor and ')' in s_valor:
            s_valor = '-' + s_valor.replace('(', '').replace(')', '')
        return float(s_valor)
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
        "COTA-PARTE": "COTA"
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
    arquivo_f = "zEducação/Alpinópolis.csv"
    arquivo_r = "zEducação/Alpinópolis_R.csv"
    arquivo_df = "zEducação/Alpinópolis_DF.csv"
    
    path_f = buscar_arquivo(arquivo_f)
    path_r = buscar_arquivo(arquivo_r)
    path_df = buscar_arquivo(arquivo_df)
    
    if not path_f or not path_r or not path_df:
        return None, None, None

    # --- INÍCIO DA CORREÇÃO PARA ALPINÓPOLIS.CSV ---
    # Passo 1: Ler apenas as duas primeiras linhas para construir o cabeçalho manualmente
    # Isso evita o erro de "equal number of columns" do engine do pandas
    df_header = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=None, nrows=2)
    
    # Preencher valores nulos para evitar erros na concatenação
    h0 = df_header.iloc[0].fillna('').astype(str).tolist()
    h1 = df_header.iloc[1].fillna('').astype(str).tolist()
    
    final_columns = []
    for col_top, col_bottom in zip(h0, h1):
        c_top = col_top.strip()
        c_bottom = col_bottom.strip()
        
        # Lógica para combinar: Se o topo for vazio ou 'Unnamed', usa apenas o de baixo
        # Caso contrário, combina os dois para criar um nome único (Ex: Janeiro_Empenhado)
        if not c_top or "Unnamed" in c_top:
            final_columns.append(c_bottom)
        elif not c_bottom:
            final_columns.append(c_top)
        else:
            final_columns.append(f"{c_top}_{c_bottom}")

    # Passo 2: Carregar os dados reais pulando as duas linhas de cabeçalho
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', skiprows=2, names=final_columns)
    # --- FIM DA CORREÇÃO ---

    # Carregamento dos outros arquivos (permanece o padrão)
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=0)
    df_r.columns = [str(c).strip() for c in df_r.columns]
    
    df_df = pd.read_csv(path_df, sep=None, engine='python', encoding='utf-8', header=0)
    df_df.columns = [str(c).strip() for c in df_df.columns]

    # Lista de meses e termos para limpeza de valores monetários
    meses_limpeza = ORDEM_MESES + ['Total', 'Orçado', 'Dedução', 'Orçado Receitas', 'Toral']

    # Limpeza de strings para números (R$ 1.234,00 -> 1234.00)
    for col in df_f.columns:
        if any(k in col for k in ['Orçado', 'Saldo', 'Liquidado', 'Empenhado', 'Pago', 'Total', 'Toral']):
            df_f[col] = df_f[col].apply(limpar_valor)
            
    for col in df_r.columns:
        if col in meses_limpeza:
            df_r[col] = df_r[col].apply(limpar_valor)
            
    for col in df_df.columns:
        if col in meses_limpeza:
            df_df[col] = df_df[col].apply(limpar_valor)

    # Tratamento da coluna Fonte para evitar decimais indesejados (ex: 1500.0 -> 1500)
    if 'Fonte' in df_f.columns:
        df_f['Fonte'] = df_f['Fonte'].astype(str).str.replace('.0', '', regex=False).str.strip()
    if 'Fonte' in df_df.columns:
        df_df['Fonte'] = df_df['Fonte'].astype(str).str.replace('.0', '', regex=False).str.strip()

    return df_f, df_r, df_df

df_f_raw, df_r, df_df_raw = load_all_data()

# --- DEFINIÇÃO DE MESES COM DADOS REAIS ---
meses_disponiveis = ['Janeiro', 'Fevereiro']

if df_f_raw is not None and df_r is not None:
    # --- SIDEBAR ---
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Filtrar Fichas:", "")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Setores")
    if st.sidebar.button("FUNDEB", use_container_width=True): st.session_state.setor = 'FUNDEB'
    if st.sidebar.button("Recursos Próprios", use_container_width=True): st.session_state.setor = 'Recursos Próprios'
    if st.sidebar.button("Recursos Vinculados", use_container_width=True): st.session_state.setor = 'Recursos Vinculados'

    # --- SETOR FUNDEB ---
    if st.session_state.setor == 'FUNDEB':
        st.markdown("<h1 style='text-align: left;'>📖 Alpinópolis - FUNDEB</h1>", unsafe_allow_html=True)
        def cat_receita(desc):
            desc = desc.upper()
            if 'VAAR' in desc: return 'VAAR'
            if 'ETI' in desc or 'TEMPO INTEGRAL' in desc: return 'ETI'
            if 'APLICAÇÃO' in desc or 'RENDIMENTOS' in desc: return 'Aplicação'
            return 'Principal'
            
        df_df_fundeb = df_df_raw[df_df_raw['Fonte'].isin(['15407', '15403'])].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb['Fonte'].apply(lambda x: 'FUNDEB 70%' if '15407' in str(x) else 'FUNDEB 30%')
        
        df_r_fundeb = df_r[(df_r['Categoria'].str.strip() == 'FUNDEB')].copy()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)
        
        df_f_fundeb = df_f_raw[df_f_raw['Fonte'].str.contains('540|546', na=False)].copy()
        
        tot_rec_periodo = df_r_fundeb[meses_disponiveis].sum().sum()
        tot_prev_2026 = df_r_fundeb['Orçado Receitas'].sum()
        
        desp_70_val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & (df_df_fundeb['Tipo'] == 'Liquidado')][meses_disponiveis].sum().sum()
        
        perc_70_indice = (desp_70_val / tot_rec_periodo * 100) if tot_rec_periodo > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Previsão Orçamentária Receitas 2026", formar_real(tot_prev_2026))
        with m2: st.metric(f"Total Arrecadado ({meses_disponiveis[0]}-{meses_disponiveis[-1]})", formar_real(tot_rec_periodo))
        with m3:
            if perc_70_indice >= 70: st.metric("Aplicação em Pessoal (Mín. 70%)", f"✅ {perc_70_indice:.2f}%", delta=f"{perc_70_indice-70:.2f}%")
            else: st.metric("Aplicação em Pessoal (Mín. 70%)", f"⚠️ {perc_70_indice:.2f}%", delta=f"{perc_70_indice-70:.2f}%", delta_color="inverse")
        
        st.markdown("---")
        st.subheader("🔹 1. Receitas FUNDEB")
        tipo_r = st.segmented_control("Visualização Receita:", ["Acumulado", "Mensal"], default="Mensal", key="r_btn")
        
        if tipo_r == "Acumulado":
            df_r_plot = df_r_fundeb.groupby('Subcategoria')[meses_disponiveis].sum().sum(axis=1).reset_index()
            df_r_plot.columns = ['Categoria', 'Valor']
            fig_r = px.bar(df_r_plot, x='Categoria', y='Valor', color='Categoria', text_auto='.2s',
                           color_discrete_map={'Principal':'#002147', 'VAAR':'#003366', 'ETI':'#00509d', 'Aplicação':'#6699cc'})
        else:
            dados_m_r = []
            for m in meses_disponiveis:
                for cat in df_r_fundeb['Subcategoria'].unique():
                    val = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat][m].sum()
                    dados_m_r.append({"Mês": m, "Categoria": cat, "Valor": val})
            fig_r = px.bar(pd.DataFrame(dados_m_r), x='Mês', y='Valor', color='Categoria', text_auto='.2s', barmode='stack',
                           color_discrete_map={'Principal':'#002147', 'VAAR':'#003366', 'ETI':'#00509d', 'Aplicação':'#6699cc'},
                           category_orders={"Mês": ORDEM_MESES})
        
        fig_r.update_layout(separators=",.", yaxis={'showticklabels': False})
        fig_r.update_traces(hovertemplate="<span style='color:white;'><b>%{x}</b><br>Valor: R$ %{y:,.2f}</span><extra></extra>", hoverlabel=HOVER_STYLE)
        st.plotly_chart(fig_r, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        st.subheader("🔹 2. Despesas FUNDEB")
        tipo_f = st.segmented_control("Visualização Despesa:", ["Acumulado", "Mensal"], default="Mensal", key="f_btn")
        
        if tipo_f == "Acumulado":
            total_desp_acum = df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado'][meses_disponiveis].sum().sum()
            df_f_plot = []
            for fonte in ['FUNDEB 70%', 'FUNDEB 30%']:
                val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & (df_df_fundeb['Tipo'] == 'Liquidado')][meses_disponiveis].sum().sum()
                prop = (val / total_desp_acum * 100) if total_desp_acum > 0 else 0
                df_f_plot.append({"Fonte": fonte, "Valor": val, "Proporção": f"{prop:.2f}%"})
            fig_f = px.bar(pd.DataFrame(df_f_plot), x='Fonte', y='Valor', color='Fonte', text_auto='.2s',
                           custom_data=['Proporção'], color_discrete_map={'FUNDEB 70%':'#660000', 'FUNDEB 30%':'#cc0000'})
        else:
            dados_m_f = []
            for m in meses_disponiveis:
                total_desp_mes = df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado'][m].sum()
                for fonte in ['FUNDEB 70%', 'FUNDEB 30%']:
                    val = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & (df_df_fundeb['Tipo'] == 'Liquidado')][m].sum()
                    prop = (val / total_desp_mes * 100) if total_desp_mes > 0 else 0
                    dados_m_f.append({"Mês": m, "Fonte": fonte, "Valor": val, "Proporção": f"{prop:.2f}%"})
            fig_f = px.bar(pd.DataFrame(dados_m_f), x='Mês', y='Valor', color='Fonte', text_auto='.2s', barmode='stack',
                           custom_data=['Proporção'], color_discrete_map={'FUNDEB 70%':'#660000', 'FUNDEB 30%':'#cc0000'},
                           category_orders={"Mês": ORDEM_MESES})
        
        fig_f.update_traces(hovertemplate="<span style='color:white;'><b>%{x}</b><br>Valor: R$ %{y:,.2f}<br>Proporção: %{customdata[0]}</span><extra></extra>", hoverlabel=HOVER_STYLE)
        fig_f.update_layout(separators=",.", yaxis={'showticklabels': False})
        st.plotly_chart(fig_f, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        st.subheader("🔹 3. Comparativo de Aplicação (Índice 70%)")
        tipo_grafico = st.segmented_control("Visualização Comparativo:", ["Total Acumulado", "Mensal"], default="Mensal")
        
        if tipo_grafico == "Total Acumulado":
            df_comp = pd.DataFrame({"Tipo": ["Receita Total", "Despesas (70%)"], "Valor": [tot_rec_periodo, desp_70_val]})
            fig_comp = px.bar(df_comp, x='Tipo', y='Valor', color='Tipo', 
                              text=[f"", f"{perc_70_indice:.2f}%"],
                              color_discrete_map={"Receita Total": "#003366", "Despesas (70%)": "#660000"})
            fig_comp.add_hline(y=tot_rec_periodo * 0.7, line_dash="dot", line_color="green", annotation_text=f"Meta 70%")
        else:
            dados_m_comp = []
            for m in meses_disponiveis:
                r_m = df_r_fundeb[m].sum()
                d_m = df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & (df_df_fundeb['Tipo'] == 'Liquidado')][m].sum()
                perc_m = (d_m / r_m * 100) if r_m > 0 else 0
                dados_m_comp.append({"Mês": m, "Tipo": "Receita Total", "Valor": r_m, "Texto": ""})
                dados_m_comp.append({"Mês": m, "Tipo": "Despesas (70%)", "Valor": d_m, "Texto": f"{perc_m:.2f}%"})
            
            fig_comp = px.bar(pd.DataFrame(dados_m_comp), x='Mês', y='Valor', color='Tipo', barmode='group', 
                              text='Texto',
                              color_discrete_map={"Receita Total": "#003366", "Despesas (70%)": "#660000"},
                              category_orders={"Mês": ORDEM_MESES})
            
            # Adicionando a linha da meta de 70% também na visão mensal
            df_linha_70 = pd.DataFrame(dados_m_comp)
            df_linha_70 = df_linha_70[df_linha_70['Tipo'] == 'Receita Total'].copy()
            df_linha_70['Meta 70%'] = df_linha_70['Valor'] * 0.7
            fig_comp.add_trace(go.Scatter(x=df_linha_70['Mês'], y=df_linha_70['Meta 70%'], mode='lines+markers', name='Meta 70% (Mensal)', line=dict(color='green', dash='dot')))
        
        fig_comp.update_traces(hovertemplate="<span style='color:white;'><b>%{x}</b><br>Valor: R$ %{y:,.2f}</span><extra></extra>", hoverlabel=HOVER_STYLE)
        fig_comp.update_layout(separators=",.") 
        st.plotly_chart(fig_comp, use_container_width=True, config=CONFIG_PT)

        st.markdown("### 📋 Relatório de Fichas FUNDEB")
        col_liq_fichas = [c for c in df_f_fundeb.columns if any(m in c for m in meses_disponiveis) and 'Liquidado' in c]
        df_f_fundeb['Soma_Liquidado'] = df_f_fundeb[col_liq_fichas].sum(axis=1)
        df_f_fundeb['Fonte_Agrupada'] = df_f_fundeb['Fonte'].apply(lambda x: 'FUNDEB 70%' if '540' in str(x) else 'FUNDEB 30%')
        cols_show = ['Atividade', 'Ficha', 'Fonte_Agrupada']
        orc_col = [c for c in df_f_fundeb.columns if 'Orçado' in c]
        if orc_col: cols_show.append(orc_col[0])
        cols_show.append('Soma_Liquidado')
        st.dataframe(df_f_fundeb[cols_show], use_container_width=True, hide_index=True)
        # --- SETOR RECURSOS PRÓPRIOS ---
    elif st.session_state.setor == 'Recursos Próprios':
        st.markdown("<h1 style='text-align: left;'>📖 Alpinópolis - Recursos Próprios (25%)</h1>", unsafe_allow_html=True)
        
        # 1. Base de Cálculo (Denominador): Impostos e Cota-Parte
        df_r_base = df_r[df_r['Categoria'].str.strip().isin(['Impostos', 'Cota-Parte'])].copy()
        
        # 2. Dedução FUNDEB (Ajustado com str.contains para evitar falhas por espaçamentos)
        df_r_ded = df_r[df_r['Categoria'].astype(str).str.contains('Dedução', case=False, na=False)].copy()
        
        # Seletor Global de Fase para Despesas 15001
        fase_despesa = st.segmented_control(" (Impacta Indicadores Superiores):", ["Empenhado", "Liquidado", "Pago"], default="Liquidado", key="fase_desp_rp")

        # 3. Despesas 15001
        df_df_15001 = df_df_raw[(df_df_raw['Fonte'] == '15001') & (df_df_raw['Tipo'] == fase_despesa)].copy()
        
        total_rec_base = df_r_base[meses_disponiveis].sum().sum()
        total_desp_15001 = df_df_15001[meses_disponiveis].sum().sum()
        total_deducoes = abs(df_r_ded[meses_disponiveis].sum().sum())
        
        # Lógica de cálculo para o índice
        esforco_total = total_desp_15001 + total_deducoes
        perc_25 = (esforco_total / total_rec_base * 100) if total_rec_base > 0 else 0
        
        # Cálculo de quanto falta gastar para o secretário atingir a meta
        meta_financeira_25 = total_rec_base * 0.25
        saldo_necessario_25 = max(0, meta_financeira_25 - esforco_total)
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Total das Despesas (Fonte 15001)", formar_real(total_desp_15001))
        with m2: st.metric("Saldo para atingir a meta (25%)", formar_real(saldo_necessario_25))
        with m3:
            if perc_25 >= 25: st.metric("Índice de Aplicação (Mín. 25%)", f"✅ {perc_25:.2f}%", delta=f"{perc_25-25:.2f}%")
            else: st.metric("Índice de Aplicação (Mín. 25%)", f"⚠️ {perc_25:.2f}%", delta=f"{perc_25-25:.2f}%", delta_color="inverse")
            
        st.markdown("---")
        
        # --- RECEITAS ---
        st.subheader("🔹 Receitas Recursos Próprios (Impostos e Cota-Parte)")
        view_rp = st.segmented_control("Visualização Receitas:", ["Acumulado", "Mensal"], default="Mensal", key="view_rp")

        lista_completa = ["📊 Acumulado Geral"] + df_r_base['Descrição da Receita'].unique().tolist()
        if 'idx_nav_rp' not in st.session_state: st.session_state.idx_nav_rp = 0
        
        grid = st.columns([0.5, 1.2, 1.2, 1.2, 1.2, 1.2, 0.5])
        with grid[0]:
            if st.button("◀", key="rp_left"): 
                st.session_state.idx_nav_rp = max(0, st.session_state.idx_nav_rp - 5)
                st.rerun()
        
        fim_idx = min(st.session_state.idx_nav_rp + 5, len(lista_completa))
        fatia = lista_completa[st.session_state.idx_nav_rp:fim_idx]
        
        for i, item in enumerate(fatia):
            with grid[i+1]:
                label = abreviar_extremo(item)
                if st.button(label, key=f"rp_btn_{item}", help=item, use_container_width=True):
                    st.session_state['ativo_rp'] = item.replace("📊 ", "")
                    st.rerun()
        
        with grid[6]:
            if st.button("▶", key="rp_right"):
                if st.session_state.idx_nav_rp + 5 < len(lista_completa): 
                    st.session_state.idx_nav_rp += 5
                    st.rerun()
                    
        ativo = st.session_state.get('ativo_rp', "Acumulado Geral")
        st.markdown(f"#### 📈 {ativo}")
        df_aux = df_r_base.copy() if ativo == "Acumulado Geral" else df_r_base[df_r_base['Descrição da Receita'] == ativo].copy()
        
        if view_rp == "Acumulado":
            fig_rp = px.bar(x=[ativo], y=[df_aux[meses_disponiveis].sum().sum()], text_auto='.3s', color_discrete_sequence=['#003366'])
        else:
            dados_m = [{"Mês": m, "Valor": df_aux[m].sum()} for m in meses_disponiveis]
            fig_rp = px.bar(pd.DataFrame(dados_m), x='Mês', y='Valor', text_auto='.2s', color_discrete_sequence=['#003366'],
                            category_orders={"Mês": ORDEM_MESES})
        
        fig_rp.update_traces(
            hovertemplate="<span style='color:white;'><b>%{x}</b><br>Setor: Recursos Próprios<br>Fonte: " + ativo + "<br>Valor: R$ %{y:,.2f}</span><extra></extra>",
            hoverlabel=HOVER_STYLE
        )
        fig_rp.update_layout(separators=",.") 
        st.plotly_chart(fig_rp, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        
        # --- DESPESAS FONTE 15001 ---
        st.subheader("🔹 Despesas Fonte 15001")
        st.markdown("Detalhamento Acumulado e Mensal por Estágio (Empenhado, Liquidado, Pago)")
        view_desp = st.segmented_control("Visualização Despesas:", ["Acumulado", "Mensal"], default="Mensal", key="view_desp")
        
        df_15001_todas = df_df_raw[(df_df_raw['Fonte'] == '15001') & (df_df_raw['Tipo'].isin(['Empenhado', 'Liquidado', 'Pago']))].copy()
        
        if view_desp == "Acumulado":
            total_desp_acum_rp = df_15001_todas[meses_disponiveis].sum().sum()
            df_desp_plot = []
            for fase in ["Empenhado", "Liquidado", "Pago"]:
                val = df_15001_todas[df_15001_todas['Tipo'] == fase][meses_disponiveis].sum().sum()
                prop = (val / total_desp_acum_rp * 100) if total_desp_acum_rp > 0 else 0
                df_desp_plot.append({"Fase": fase, "Valor": val, "Proporção": f"{prop:.2f}%", "Dedução": total_deducoes, "Despesa": val})
            df_desp_plot = pd.DataFrame(df_desp_plot)
            df_desp_plot['Fase'] = pd.Categorical(df_desp_plot['Fase'], ["Empenhado", "Liquidado", "Pago"])
            
            fig_d = px.bar(df_desp_plot, x='Fase', y='Valor', color='Fase', text_auto='.3s', 
                           custom_data=['Proporção', 'Dedução', 'Despesa'],
                           color_discrete_map={'Empenhado':"#fa3d3d", 'Liquidado':"#860000", 'Pago':"#470000"})
        else:
            dados_d_m = []
            for m in meses_disponiveis:
                total_mes_rp = df_15001_todas[m].sum()
                deducao_mes = abs(df_r_ded[m].sum())
                for fase in ['Empenhado', 'Liquidado', 'Pago']:
                    val = df_15001_todas[df_15001_todas['Tipo'] == fase][m].sum()
                    prop = (val / total_mes_rp * 100) if total_mes_rp > 0 else 0
                    dados_d_m.append({"Mês": m, "Fase": fase, "Valor": val, "Proporção": f"{prop:.2f}%", "Dedução": deducao_mes, "Despesa": val})
            df_dados_d_m = pd.DataFrame(dados_d_m)
            df_dados_d_m['Fase'] = pd.Categorical(df_dados_d_m['Fase'], ["Empenhado", "Liquidado", "Pago"])
            
            fig_d = px.bar(df_dados_d_m, x='Mês', y='Valor', color='Fase', barmode='group', text_auto='.2s',
                           custom_data=['Proporção', 'Dedução', 'Despesa'],
                           color_discrete_map={'Empenhado':'#fa3d3d', 'Liquidado':'#860000', 'Pago':'#470000'},
                           category_orders={"Mês": ORDEM_MESES, "Fase": ["Empenhado", "Liquidado", "Pago"]})
        
        fig_d.update_traces(
            hovertemplate="<span style='color:white;'><b>%{x}</b><br>Status: %{fullData.name}<br>Valor do Investimento (15001): R$ %{customdata[2]:,.2f}<br>Valor da Dedução: R$ %{customdata[1]:,.2f}<br>Proporção (do Mês/Total): %{customdata[0]}</span><extra></extra>",
            hoverlabel=HOVER_STYLE
        )
        fig_d.update_layout(separators=",.") 
        st.plotly_chart(fig_d, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")
        
        # --- ANÁLISE COMPARATIVA E META ---
        st.subheader("🔹 Análise Comparativa e Meta (Mínimo 25%)")
        view_meta = st.segmented_control("Visualização Meta:", ["Acumulado", "Mensal"], default="Mensal", key="view_meta")

        cor_aplicacao = "#27ae60" if perc_25 >= 25 else "#e74c3c"

        if view_meta == "Acumulado":
            df_meta = pd.DataFrame({
                "Categoria": ["Receitas Base", "Aplicação Total"],
                "Valor": [total_rec_base, esforco_total],
                "Deducao": [0, total_deducoes],
                "Despesa15001": [0, total_desp_15001]
            })
            fig_meta = px.bar(df_meta, x='Categoria', y='Valor', color='Categoria', 
                              text=["", f"{perc_25:.2f}%"],
                              custom_data=['Deducao', 'Despesa15001'],
                              color_discrete_map={"Receitas Base": "#003366", "Aplicação Total": cor_aplicacao})
            
            fig_meta.update_traces(
                hovertemplate="<span style='color:white;'><b>%{x}</b><br>Total (Aplicação): R$ %{y:,.2f}<br>Valor da Dedução: R$ %{customdata[0]:,.2f}<br>Valor do Investimento (15001): R$ %{customdata[1]:,.2f}</span><extra></extra>",
                hoverlabel=HOVER_STYLE
            )
            fig_meta.add_hline(y=total_rec_base * 0.25, line_dash="dash", line_color="#f39c12", annotation_text="Meta Constitucional (25%)", annotation_position="top left")
        else:
            dados_meta_m = []
            for m in meses_disponiveis:
                r_m = df_r_base[m].sum()
                d_m = df_df_15001[m].sum()
                ded_m = abs(df_r_ded[m].sum())
                
                perc_m = ((d_m + ded_m) / r_m * 100) if r_m > 0 else 0
                cor_m = "#27ae60" if perc_m >= 25 else "#e74c3c"
                
                dados_meta_m.append({"Mês": m, "Tipo": "Receitas Base", "Valor": r_m, "Dedução": 0, "Desp": 0, "Texto": ""})
                dados_meta_m.append({"Mês": m, "Tipo": "Aplicação Total", "Valor": d_m + ded_m, "Dedução": ded_m, "Desp": d_m, "Texto": f"{perc_m:.2f}%"})
            
            df_meta_m = pd.DataFrame(dados_meta_m)
            fig_meta = px.bar(df_meta_m, x='Mês', y='Valor', color='Tipo', barmode='group', text='Texto',
                              custom_data=['Dedução', 'Desp'], 
                              color_discrete_map={"Receitas Base": "#003366", "Aplicação Total": cor_aplicacao},
                              category_orders={"Mês": ORDEM_MESES}) 
            
            fig_meta.update_traces(
                hovertemplate="<span style='color:white;'><b>%{x} - %{data.name}</b><br>Total (Aplicação): R$ %{y:,.2f}<br>Valor da Dedução: R$ %{customdata[0]:,.2f}<br>Valor do Investimento (15001): R$ %{customdata[1]:,.2f}</span><extra></extra>",
                hoverlabel=HOVER_STYLE
            )
            
            df_linha_meta = df_meta_m[df_meta_m['Tipo'] == 'Receitas Base'].copy()
            df_linha_meta['Meta Mensal (25%)'] = df_linha_meta['Valor'] * 0.25
            fig_meta.add_trace(go.Scatter(x=df_linha_meta['Mês'], y=df_linha_meta['Meta Mensal (25%)'], mode='lines+markers', name='Meta 25% (Mensal)', line=dict(color='#f39c12', dash='dash')))

        fig_meta.update_layout(separators=",.") 
        st.plotly_chart(fig_meta, use_container_width=True, config=CONFIG_PT)

    # --- SETOR RECURSOS VINCULADOS ---
    elif st.session_state.setor == 'Recursos Vinculados':
        st.markdown("<h1 style='text-align: left;'>📖 Alpinópolis - Recursos Vinculados</h1>", unsafe_allow_html=True)
        mapa_desp = {'PNAE': ['1552', '2552'], 'PNATE': ['1553', '2553'], 'PTE': ['1576', '2576'], 'QESE': ['1550', '2550']}
        programas = ['PNAE', 'PNATE', 'PTE', 'QESE']
        
        df_r_vinc = df_r[df_r['Descrição da Receita'].str.upper().str.strip().isin(programas)].copy()
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Previsão Vinculados 2026", formar_real(df_r_vinc['Orçado Receitas'].sum()))
        with m2: st.metric(f"Arrecadado ({meses_disponiveis[0]}-{meses_disponiveis[-1]})", formar_real(df_r_vinc[meses_disponiveis].sum().sum()))
        with m3:
            fontes_v = [f for sub in mapa_desp.values() for f in sub]
            total_liq_vinc = df_df_raw[(df_df_raw['Fonte'].isin(fontes_v)) & (df_df_raw['Tipo'] == 'Liquidado')][meses_disponiveis].sum().sum()
            st.metric(f"Liquidado ({meses_disponiveis[0]}-{meses_disponiveis[-1]})", formar_real(total_liq_vinc))

        st.markdown("---")
        
        st.subheader("🔹 1. Detalhamento de Receitas e Despesas por Programa")
        tipo_vinc = st.segmented_control("Visualização:", ["Acumulado", "Mensal"], default="Mensal", key="vinc_btn")

        for prog in programas:
            st.markdown(f"#### 📊 Programa: {prog}")
            prev_prog = df_r_vinc[df_r_vinc['Descrição da Receita'].str.upper().str.strip() == prog]['Orçado Receitas'].sum()
            st.markdown(f"**Previsão total de Receitas para 2026:** {formar_real(prev_prog)}")

            if tipo_vinc == "Acumulado":
                dados_comp_v = []
                rec = df_r_vinc[df_r_vinc['Descrição da Receita'].str.upper().str.strip() == prog][meses_disponiveis].sum().sum()
                desp = df_df_raw[(df_df_raw['Fonte'].isin(mapa_desp[prog])) & (df_df_raw['Tipo'] == 'Liquidado')][meses_disponiveis].sum().sum()
                dados_comp_v.append({"Tipo": "Receita", "Valor": rec})
                dados_comp_v.append({"Tipo": "Despesa", "Valor": desp})
                
                fig_rec_v = px.bar(pd.DataFrame(dados_comp_v), x='Tipo', y='Valor', color='Tipo', barmode='group', text_auto='.2s',
                                  color_discrete_map={'Receita':'#002147', 'Despesa':'#660000'})
                fig_rec_v.update_traces(hovertemplate="<span style='color:white;'><b>%{x}</b><br>Valor: R$ %{y:,.2f}</span><extra></extra>", hoverlabel=HOVER_STYLE)
                fig_rec_v.update_layout(separators=",.") 
                st.plotly_chart(fig_rec_v, use_container_width=True, config=CONFIG_PT)

            else:
                dados_d_v = []
                for m in meses_disponiveis:
                    rec_m = df_r_vinc[df_r_vinc['Descrição da Receita'].str.upper().str.strip() == prog][m].sum()
                    desp_m = df_df_raw[(df_df_raw['Fonte'].isin(mapa_desp[prog])) & (df_df_raw['Tipo'] == 'Liquidado')][m].sum()
                    dados_d_v.append({"Mês": m, "Tipo": "Receita", "Valor": rec_m})
                    dados_d_v.append({"Mês": m, "Tipo": "Despesa", "Valor": desp_m})

                if dados_d_v:
                    fig_desp_v = px.bar(pd.DataFrame(dados_d_v), x='Mês', y='Valor', color='Tipo', barmode='group', text_auto='.2s',
                                       color_discrete_map={'Receita':'#002147', 'Despesa':'#660000'},
                                       category_orders={"Mês": ORDEM_MESES})
                    fig_desp_v.update_traces(hovertemplate="<span style='color:white;'><b>%{x}</b><br>Tipo: %{data.name}<br>Valor: R$ %{y:,.2f}</span><extra></extra>", hoverlabel=HOVER_STYLE)
                    fig_desp_v.update_layout(separators=",.") 
                    st.plotly_chart(fig_desp_v, use_container_width=True, config=CONFIG_PT)
            
            st.markdown("---")

    # --- RELATÓRIO DE FICHAS GLOBAL ---
    st.markdown("### 📋 Relatório Geral de Fichas")
    df_f_filt = df_f_raw[df_f_raw['Atividade'].str.contains(search_term, na=False, case=False)].copy()
    st.dataframe(df_f_filt, use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar os arquivos CSV. Verifique a pasta 'zEducação' ou o upload dos arquivos.")