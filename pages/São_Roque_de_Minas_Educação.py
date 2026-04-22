
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import plotly.graph_objects as go
import streamlit.components.v1 as components
import random

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="São Roque de Minas - Gestão Educação", layout="wide")

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

pio.templates.default = "plotly_dark"
CONFIG_PT = {'displaylogo': False, 'showTips': False}
HOVER_STYLE = dict(bgcolor="rgba(0,0,0,0.9)", font_size=13, font_family="Arial", font_color="white")

ORDEM_MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

if 'setor' not in st.session_state:
    st.session_state.setor = 'FUNDEB'

# --- FUNÇÕES UTILITÁRIAS ---
def metric_contabil(label, valor_atual, meta):
    delta = valor_atual - meta
    status_icon = "✅" if valor_atual >= meta else "⚠️"
    return st.metric(
        label=label,
        value=f"{status_icon} {valor_atual:.2f}%",
        delta=f"{delta:.2f}%",
        delta_color="normal"
    )

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
    arquivo_f  = "zEducação/São Roque de Minas.csv"
    arquivo_r  = "zEducação/São Roque de Minas_R.csv"
    arquivo_df = "zEducação/São Roque de Minas_DF.csv"
    
    path_f  = buscar_arquivo(arquivo_f)
    path_r  = buscar_arquivo(arquivo_r)
    path_df = buscar_arquivo(arquivo_df)

    if not path_f or not path_r or not path_df:
        return None, None, None
    
    # --- Arquivo de fichas (F) ---
    # Este arquivo tem cabeçalho duplo: linha 0 = tipo (Empenhado/Liquidado/Pago),
    # linha 1 = mês. As colunas ficam no formato "Mês_Tipo".
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]:
            new_cols.append(col[1].strip())
        else:
            new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols

    # --- Arquivo de receitas (R) ---
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8')
    df_r.columns = [str(c).strip() for c in df_r.columns]

    # --- Arquivo de despesas por fonte (DF) ---
    df_df = pd.read_csv(path_df, sep=None, engine='python', encoding='utf-8')
    df_df.columns = [str(c).strip() for c in df_df.columns]

    meses_limpeza = ORDEM_MESES + ['Total', 'Orçado', 'Dedução', 'Orçamento Receitas']

    # Limpar colunas numéricas do arquivo F
    for col in df_f.columns:
        if any(k in col for k in ['Orçado', 'Saldo', 'Liquidado', 'Empenhado', 'Pago',
                                   'Creditado', 'Anulado']):
            df_f[col] = df_f[col].apply(limpar_valor)

    # Limpar colunas de meses do arquivo R
    for col in df_r.columns:
        if col in meses_limpeza:
            df_r[col] = df_r[col].apply(limpar_valor)

    # Limpar colunas de meses do arquivo DF
    for col in df_df.columns:
        if col in meses_limpeza:
            df_df[col] = df_df[col].apply(limpar_valor)

    # Padronizar coluna Fonte
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
    if st.sidebar.button("FUNDEB", use_container_width=True):
        st.session_state.setor = 'FUNDEB'
    if st.sidebar.button("Recursos Próprios", use_container_width=True):
        st.session_state.setor = 'Recursos Próprios'
    if st.sidebar.button("Recursos Vinculados", use_container_width=True):
        st.session_state.setor = 'Recursos Vinculados'

    # =========================================================================
    # SETOR FUNDEB
    # =========================================================================
    if st.session_state.setor == 'FUNDEB':
        st.markdown(
            "<h1 style='text-align: left;'>📖 São Roque de Minas - FUNDEB</h1>",
            unsafe_allow_html=True,
        )

        def cat_receita(desc):
            desc = desc.upper()
            if 'VAAR' in desc:
                return 'VAAR'
            if 'ETI' in desc or 'TEMPO INTEGRAL' in desc:
                return 'ETI'
            if 'APLICAÇÃO' in desc or 'RENDIMENTOS' in desc:
                return 'Aplicação'
            return 'Principal'

        # --- Filtros de dados ---
        df_df_fundeb = df_df_raw[df_df_raw['Fonte'].isin(['15407', '15403', '25407', '25403'])].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb['Fonte'].apply(
            lambda x: 'FUNDEB 70%' if x in ['15407', '25407'] else 'FUNDEB 30%'
        )

        df_r_fundeb = df_r[df_r['Categoria'].str.strip() == 'FUNDEB'].copy()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)

        # Fichas FUNDEB: Fontes 154xx / 254xx
        df_f_fundeb = df_f_raw[
            df_f_raw['Fonte'].str.contains('154|254', na=False)
        ].copy()

        # --- Métricas ---
        tot_rec_periodo  = df_r_fundeb[meses_disponiveis].sum().sum()
        tot_prev_2026    = df_r_fundeb['Orçamento Receitas'].sum()

        # Colunas de liquidado para os meses disponíveis no arquivo DF
        cols_liq_df = [f"{m}_Liquidado" if f"{m}_Liquidado" in df_df_fundeb.columns else m
                       for m in meses_disponiveis]
        # O arquivo DF tem colunas diretas por mês (sem sufixo de tipo)
        desp_70_val = (
            df_df_fundeb[
                (df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') &
                (df_df_fundeb['Tipo'] == 'Liquidado')
            ][meses_disponiveis].sum().sum()
        )

        perc_70_indice = (desp_70_val / tot_rec_periodo * 100) if tot_rec_periodo > 0 else 0

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Previsão Orçamentária Receitas 2026", formar_real(tot_prev_2026))
        with m2:
            st.metric(
                f"Total Arrecadado ({meses_disponiveis[0]}-{meses_disponiveis[-1]})",
                formar_real(tot_rec_periodo),
            )
        with m3:
            metric_contabil("Aplicação em Pessoal (Mín. 70%)", perc_70_indice, 70.0)

        st.markdown("---")

        # ---- 1. Receitas FUNDEB ----
        st.subheader("🔹 1. Receitas FUNDEB")
        tipo_r = st.segmented_control(
            "Visualização Receita:", ["Acumulado", "Mensal"], default="Mensal", key="r_btn"
        )

        if tipo_r == "Acumulado":
            df_r_plot = (
                df_r_fundeb.groupby('Subcategoria')[meses_disponiveis]
                .sum()
                .sum(axis=1)
                .reset_index()
            )
            df_r_plot.columns = ['Categoria', 'Valor']
            fig_r = px.bar(
                df_r_plot, x='Categoria', y='Valor', color='Categoria', text_auto='.2s',
                color_discrete_map={
                    'Principal': '#002147', 'VAAR': '#003366',
                    'ETI': '#00509d', 'Aplicação': '#6699cc',
                },
            )
        else:
            dados_m_r = []
            for m in meses_disponiveis:
                for cat in df_r_fundeb['Subcategoria'].unique():
                    val = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat][m].sum()
                    dados_m_r.append({"Mês": m, "Categoria": cat, "Valor": val})
            fig_r = px.bar(
                pd.DataFrame(dados_m_r), x='Mês', y='Valor', color='Categoria',
                text_auto='.2s', barmode='stack',
                color_discrete_map={
                    'Principal': '#002147', 'VAAR': '#003366',
                    'ETI': '#00509d', 'Aplicação': '#6699cc',
                },
                category_orders={"Mês": ORDEM_MESES},
            )

        fig_r.update_layout(separators=",.", yaxis={'showticklabels': False})
        fig_r.update_traces(
            hovertemplate=(
                "<span style='color:white;'><b>%{x}</b><br>"
                "Valor: R$ %{y:,.2f}</span><extra></extra>"
            ),
            hoverlabel=HOVER_STYLE,
        )
        st.plotly_chart(fig_r, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

        # ---- 2. Despesas FUNDEB ----
            

        # ---- 3. Comparativo de Aplicação (Índice 70%) ----
        st.subheader("🔹 3. Comparativo de Aplicação (Índice 70%)")
        tipo_grafico = st.segmented_control(
            "Visualização Comparativo:", ["Total Acumulado", "Mensal"], default="Mensal", key="comp_btn"
        )

        if tipo_grafico == "Total Acumulado":
            # Garantir que tot_rec_periodo e desp_70_val venham do cálculo global atualizado
            df_comp = pd.DataFrame(
                {"Tipo": ["Receita Total", "Despesas (70%)"],
                "Valor": [tot_rec_periodo, desp_70_val]}
            )
            fig_comp = px.bar(
                df_comp, x='Tipo', y='Valor', color='Tipo',
                text_auto='.3s',
                color_discrete_map={"Receita Total": "#003366", "Despesas (70%)": "#660000"},
            )
            # Adiciona o texto do percentual manualmente sobre a barra de despesa
            fig_comp.add_annotation(x="Despesas (70%)", y=desp_70_val, text=f"{perc_70_indice:.2f}%", showarrow=False, yshift=10)
            
            fig_comp.add_hline(
                y=tot_rec_periodo * 0.7, line_dash="dot", line_color="green",
                annotation_text="Meta 70%", annotation_position="top left"
            )
        else:
            dados_m_comp = []
            for m in meses_disponiveis:
                # Receita FUNDEB do mês (Ex: Código 1751...)
                r_m = df_r_fundeb[m].sum()
                
                # Despesa FUNDEB 70% Liquidada do mês
                d_m = df_df_fundeb[
                    (df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & 
                    (df_df_fundeb['Tipo'] == 'Liquidado')
                ][m].sum()
                
                perc_m = (d_m / r_m * 100) if r_m > 0 else 0
                
                dados_m_comp.append({"Mês": m, "Tipo": "Receita Total", "Valor": r_m, "Texto": ""})
                dados_m_comp.append({"Mês": m, "Tipo": "Despesas (70%)", "Valor": d_m, "Texto": f"{perc_m:.1f}%"})

            df_m_comp = pd.DataFrame(dados_m_comp)
            fig_comp = px.bar(
                df_m_comp, x='Mês', y='Valor', color='Tipo',
                barmode='group', text='Texto',
                color_discrete_map={"Receita Total": "#003366", "Despesas (70%)": "#660000"},
                category_orders={"Mês": ORDEM_MESES},
            )

            # Linha de Meta 70% dinâmica por mês
            df_meta = df_m_comp[df_m_comp['Tipo'] == 'Receita Total'].copy()
            df_meta['Meta 70%'] = df_meta['Valor'] * 0.7
            
            fig_comp.add_trace(go.Scatter(
                x=df_meta['Mês'], y=df_meta['Meta 70%'],
                mode='lines+markers', name='Meta 70%',
                line=dict(color='#28a745', width=2, dash='dot')
            ))

        fig_comp.update_layout(separators=",.", legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_comp, use_container_width=True, config=CONFIG_PT)

        # ---- Relatório de Fichas FUNDEB ----
        st.markdown("### 📋 Relatório de Fichas FUNDEB")

        # Colunas de liquidado no formato "Mês_Liquidado"
        col_liq_fichas = [
            f"{m}_Liquidado" for m in meses_disponiveis
            if f"{m}_Liquidado" in df_f_fundeb.columns
        ]
        df_f_fundeb['Soma_Liquidado'] = df_f_fundeb[col_liq_fichas].sum(axis=1)
        df_f_fundeb['Fonte_Agrupada'] = df_f_fundeb['Fonte'].apply(
            lambda x: 'FUNDEB 70%' if '154' in str(x) or '254' in str(x) else 'FUNDEB 30%'
        )

        cols_show = ['Atividade', 'Ficha', 'Fonte_Agrupada']
        orc_col = [c for c in df_f_fundeb.columns if 'Orçado' in c]
        if orc_col:
            cols_show.append(orc_col[0])
        cols_show.append('Soma_Liquidado')

        # Filtro de busca
        df_show = df_f_fundeb.copy()
        if search_term:
            mask = df_show.apply(
                lambda row: row.astype(str).str.contains(search_term, case=False).any(),
                axis=1,
            )
            df_show = df_show[mask]

        st.dataframe(df_show[cols_show], use_container_width=True, hide_index=True)

    # =========================================================================
    # SETOR RECURSOS PRÓPRIOS
    # =========================================================================
    
    elif st.session_state.setor == 'Recursos Próprios':
        st.markdown("<h1 style='text-align: left;'>📖 São Roque de Minas - Recursos Próprios (25%)</h1>", unsafe_allow_html=True)

        # --- 0. FUNÇÃO DE LIMPEZA ROBUSTA ---
        def limpar_valor(v):
            if isinstance(v, str):
                v = v.replace("R$", "").replace(" ", "").strip()
                if not v or v == "0,00": return 0.0
                # Se houver parênteses ou sinal de negativo no final (comum em deduções)
                v = v.replace("(", "").replace(")", "")
                return float(v.replace(".", "").replace(",", "."))
            return float(v) if v else 0.0

        # --- 1. PREPARAÇÃO DAS RECEITAS (Base 25% e Dedução) ---
        df_r_clean = df_r.copy()
        for m in meses_disponiveis:
            df_r_clean[m] = df_r_clean[m].apply(limpar_valor)

        # Base de Cálculo: Impostos e Cota-Parte
        df_r_base = df_r_clean[df_r_clean['Categoria'].str.strip().isin(['Impostos', 'Cota-Parte'])].copy()
        
        # Dedução FUNDEB (Sempre pegamos o valor absoluto para somar ao esforço)
        df_r_ded = df_r_clean[df_r_clean['Categoria'].str.strip() == 'Dedução FUNDEB'].copy()

        # --- 2. PREPARAÇÃO DAS DESPESAS 15001 ---
        # Garantir que estamos usando o df de despesas limpo
        df_desp_rp = df_df_raw.copy()
        for m in meses_disponiveis:
            if m in df_desp_rp.columns:
                df_desp_rp[m] = df_desp_rp[m].apply(limpar_valor)

        # Seletor de Fase
        fase_despesa = st.segmented_control(
            "Fase da Despesa (Impacta Indicadores Superiores):",
            ["Empenhado", "Liquidado", "Pago"],
            default="Liquidado",
            key="fase_desp_rp"
        )

        # Filtrar apenas Fonte 15001 e a Fase selecionada
        df_15001_filtrado = df_desp_rp[
            (df_desp_rp['Fonte'].astype(str).str.strip() == '15001') & 
            (df_desp_rp['Tipo'].astype(str).str.strip() == fase_despesa)
        ].copy()

        # --- 3. CÁLCULOS TOTAIS (CORRIGIDOS) ---
        total_rec_base = df_r_base[meses_disponiveis].sum().sum()
        total_desp_15001 = df_15001_filtrado[meses_disponiveis].sum().sum()
        # As deduções no CSV são negativas, usamos abs() para somar ao investimento
        total_deducoes = abs(df_r_ded[meses_disponiveis].sum().sum())

        esforco_total = total_desp_15001 + total_deducoes
        perc_25 = (esforco_total / total_rec_base * 100) if total_rec_base > 0 else 0
        meta_financeira_25 = total_rec_base * 0.25
        saldo_necessario_25 = max(0, meta_financeira_25 - esforco_total)

        # --- 4. DASHBOARD DE MÉTRICAS ---
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Despesas Fonte 15001", formar_real(total_desp_15001))
        with m2:
            st.metric("Total Deduções FUNDEB", formar_real(total_deducoes))
        with m3:
            metric_contabil("Índice de Aplicação (Mín. 25%)", perc_25, 25.0)

        st.markdown("---")

        # --- 5. GRÁFICO DE RECEITAS (FEVEREIRO CORRIGIDO) ---
        st.subheader("🔹 Receitas Recursos Próprios")
        view_rp = st.segmented_control("Visualização:", ["Acumulado", "Mensal"], default="Mensal", key="v_rp")
        
        # Lógica de navegação simplificada e filtrada
        ativo = st.session_state.get('ativo_rp', "Acumulado Geral")
        df_plot_rec = df_r_base if ativo == "Acumulado Geral" else df_r_base[df_r_base['Descrição da Receita'] == ativo]

        if view_rp == "Mensal":
            dados_m = [{"Mês": m, "Valor": df_plot_rec[m].sum()} for m in meses_disponiveis]
            fig_r = px.bar(pd.DataFrame(dados_m), x='Mês', y='Valor', text_auto='.2s', color_discrete_sequence=['#003366'])
        else:
            fig_r = px.bar(x=[ativo], y=[df_plot_rec[meses_disponiveis].sum().sum()], text_auto='.3s')
        
        st.plotly_chart(fig_r, use_container_width=True)

        # --- 6. COMPARATIVO FINAL ---
        st.subheader("🔹 Análise Comparativa e Meta")
        
        # Gráfico que mostra Receita Base vs O que foi aplicado (Despesa + Dedução)
        dados_comp = [
            {"Categoria": "Receita Base (100%)", "Valor": total_rec_base},
            {"Categoria": "Aplicação Real (15001 + Ded.)", "Valor": esforco_total}
        ]
        fig_comp = px.bar(pd.DataFrame(dados_comp), x='Categoria', y='Valor', color='Categoria',
                        color_discrete_map={"Receita Base (100%)": "#003366", "Aplicação Real (15001 + Ded.)": "#27ae60"})
        
        # Linha da Meta 25%
        fig_comp.add_hline(y=meta_financeira_25, line_dash="dash", line_color="#f39c12", 
                        annotation_text="Meta 25%", annotation_position="top left")
        
        st.plotly_chart(fig_comp, use_container_width=True)

    # =========================================================================
    # SETOR RECURSOS VINCULADOS
    # =========================================================================
    elif st.session_state.setor == 'Recursos Vinculados':
        st.markdown(
            "<h1 style='text-align: left;'>📖 São Roque de Minas - Recursos Vinculados</h1>",
            unsafe_allow_html=True,
        )

        # Fontes vinculadas presentes nos dados de São Roque (sem par 2xxx)
        mapa_desp = {
            'PNAE':  ['1552'],
            'PNATE': ['1553'],
            'PTE':   ['1576'],
            'QESE':  ['1550'],
        }
        programas = ['PNAE', 'PNATE', 'PTE', 'QESE']

        df_r_vinc = df_r[
            df_r['Descrição da Receita'].str.upper().str.strip().isin(programas)
        ].copy()

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                "Previsão Vinculados 2026",
                formar_real(df_r_vinc['Orçamento Receitas'].sum()),
            )
        with m2:
            st.metric(
                f"Arrecadado ({meses_disponiveis[0]}-{meses_disponiveis[-1]})",
                formar_real(df_r_vinc[meses_disponiveis].sum().sum()),
            )
        with m3:
            fontes_v = [f for sub in mapa_desp.values() for f in sub]
            total_liq_vinc = (
                df_df_raw[
                    (df_df_raw['Fonte'].isin(fontes_v)) &
                    (df_df_raw['Tipo'] == 'Liquidado')
                ][meses_disponiveis].sum().sum()
            )
            st.metric(
                f"Liquidado ({meses_disponiveis[0]}-{meses_disponiveis[-1]})",
                formar_real(total_liq_vinc),
            )

        st.markdown("---")

        st.subheader("🔹 1. Detalhamento de Receitas e Despesas por Programa")
        tipo_vinc = st.segmented_control(
            "Visualização:", ["Acumulado", "Mensal"], default="Mensal", key="vinc_btn"
        )

        for prog in programas:
            st.markdown(f"#### 📊 Programa: {prog}")
            prev_prog = df_r_vinc[
                df_r_vinc['Descrição da Receita'].str.upper().str.strip() == prog
            ]['Orçamento Receitas'].sum()
            st.markdown(f"**Previsão total de Receitas para 2026:** {formar_real(prev_prog)}")

            if tipo_vinc == "Acumulado":
                dados_comp_v = []
                rec  = df_r_vinc[
                    df_r_vinc['Descrição da Receita'].str.upper().str.strip() == prog
                ][meses_disponiveis].sum().sum()
                desp = df_df_raw[
                    (df_df_raw['Fonte'].isin(mapa_desp[prog])) &
                    (df_df_raw['Tipo'] == 'Liquidado')
                ][meses_disponiveis].sum().sum()
                dados_comp_v.append({"Tipo": "Receita", "Valor": rec})
                dados_comp_v.append({"Tipo": "Despesa", "Valor": desp})

                fig_rec_v = px.bar(
                    pd.DataFrame(dados_comp_v), x='Tipo', y='Valor', color='Tipo',
                    barmode='group', text_auto='.2s',
                    color_discrete_map={'Receita': '#002147', 'Despesa': '#660000'},
                )
                fig_rec_v.update_traces(
                    hovertemplate=(
                        "<span style='color:white;'><b>%{x}</b><br>"
                        "Valor: R$ %{y:,.2f}</span><extra></extra>"
                    ),
                    hoverlabel=HOVER_STYLE,
                )
                fig_rec_v.update_layout(separators=",.")
                st.plotly_chart(fig_rec_v, use_container_width=True, config=CONFIG_PT)

            else:
                dados_d_v = []
                for m in meses_disponiveis:
                    rec_m = df_r_vinc[
                        df_r_vinc['Descrição da Receita'].str.upper().str.strip() == prog
                    ][m].sum()
                    desp_m = df_df_raw[
                        (df_df_raw['Fonte'].isin(mapa_desp[prog])) &
                        (df_df_raw['Tipo'] == 'Liquidado')
                    ][m].sum()
                    dados_d_v.append({"Mês": m, "Tipo": "Receita", "Valor": rec_m})
                    dados_d_v.append({"Mês": m, "Tipo": "Despesa", "Valor": desp_m})

                if dados_d_v:
                    fig_desp_v = px.bar(
                        pd.DataFrame(dados_d_v), x='Mês', y='Valor', color='Tipo',
                        barmode='group', text_auto='.2s',
                        color_discrete_map={'Receita': '#002147', 'Despesa': '#660000'},
                        category_orders={"Mês": ORDEM_MESES},
                    )
                    fig_desp_v.update_traces(
                        hovertemplate=(
                            "<span style='color:white;'><b>%{x}</b><br>"
                            "Tipo: %{data.name}<br>"
                            "Valor: R$ %{y:,.2f}</span><extra></extra>"
                        ),
                        hoverlabel=HOVER_STYLE,
                    )
                    fig_desp_v.update_layout(separators=",.")
                    st.plotly_chart(fig_desp_v, use_container_width=True, config=CONFIG_PT)

            st.markdown("---")

    # =========================================================================
    # RELATÓRIO DE FICHAS GLOBAL
    # =========================================================================
    st.markdown("### 📋 Relatório Geral de Fichas")
    df_f_filt = df_f_raw[
        df_f_raw['Atividade'].str.contains(search_term, na=False, case=False)
    ].copy()
    st.dataframe(df_f_filt, use_container_width=True, hide_index=True)

else:
    st.error(
        "Erro ao carregar os arquivos CSV. Verifique a pasta 'zEducação' ou o upload dos arquivos."
    )