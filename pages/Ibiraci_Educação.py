import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import plotly.graph_objects as go
import streamlit.components.v1 as components
import random

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ibiraci - Gestão Educação", layout="wide")

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
    arquivo_f  = "zEducação/Ibiraci.csv"
    arquivo_r  = "zEducação/Ibiraci_R.csv"
    arquivo_df = "zEducação/Ibiraci_DF.csv"
    
    path_f, path_r, path_df = buscar_arquivo(arquivo_f), buscar_arquivo(arquivo_r), buscar_arquivo(arquivo_df)
    if not path_f or not path_r or not path_df: return None, None, None
    
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]: new_cols.append(col[1].strip())
        else: new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols
    
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=0)
    df_r.columns = [str(c).strip() for c in df_r.columns]
    
    df_df = pd.read_csv(path_df, sep=None, engine='python', encoding='utf-8')
    df_df.columns = [str(c).strip() for c in df_df.columns]
    
    meses_limpeza = ORDEM_MESES + [m.lower() for m in ORDEM_MESES] + ['Total', 'TOTAL', 'Orçado', 'Dedução', 'Orçado Receitas']
    
    for col in df_f.columns:
        if any(k in col for k in ['Orçado', 'Saldo', 'Liquidado', 'Empenhado', 'Pago']):
            df_f[col] = df_f[col].apply(limpar_valor)
    for col in df_r.columns:
        if col in meses_limpeza:
            df_r[col] = df_r[col].apply(limpar_valor)
    for col in df_df.columns:
        if col in meses_limpeza:
            df_df[col] = df_df[col].apply(limpar_valor)
            
    if 'Fonte' in df_f.columns:
        df_f['Fonte'] = df_f['Fonte'].astype(str).str.replace('.0', '', regex=False).str.strip()
    if 'Fonte' in df_df.columns:
        df_df['Fonte'] = df_df['Fonte'].astype(str).str.replace('.0', '', regex=False).str.strip()
        
    return df_f, df_r, df_df

df_f_raw, df_r, df_df_raw = load_all_data()

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

    # =========================================================================
    # SETOR FUNDEB
    # =========================================================================
    if st.session_state.setor == 'FUNDEB':
        st.markdown("<h1 style='text-align: left;'>📖 Ibiraci - FUNDEB</h1>", unsafe_allow_html=True)

        # ── FUNÇÕES DE SUPORTE ────────────────────────────────────────────────
        def cat_receita(desc):
            desc = str(desc).upper().strip()
            if 'VAAR' in desc or 'VAAT' in desc: return 'VAAR/VAAT'
            if 'ETI' in desc or 'TEMPO INTEGRAL' in desc: return 'ETI'
            if 'APLICAÇÃO' in desc or 'RENDIMENTOS' in desc: return 'Rendimentos'
            return 'Principal'

        def obter_soma_mensal_robusta(df, meses):
            """Soma colunas de meses independentemente de maiúsculas/minúsculas."""
            colunas_map = {c.strip().lower(): c for c in df.columns}
            cols = [colunas_map[m.strip().lower()] for m in meses if m.strip().lower() in colunas_map]
            return df[cols].sum().sum() if cols else 0.0

        # ── RECEITAS ─────────────────────────────────────────────────────────
        df_r_fundeb = df_r[df_r['Categoria'].str.strip() == 'FUNDEB'].copy()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)

        # Previsão Orçamento Município = só linha Principal
        tot_prev_municipio = df_r_fundeb[df_r_fundeb['Subcategoria'] == 'Principal']['Orçado Receitas'].sum()
        # Previsão Portaria Interministerial = soma de todas as previsões
        tot_prev_portaria  = df_r_fundeb['Orçado Receitas'].sum()
        # Total arrecadado no período (todas as subcategorias)
        tot_rec_periodo    = obter_soma_mensal_robusta(df_r_fundeb, meses_disponiveis)

        # ETI: valor recebido no período
        tot_eti = obter_soma_mensal_robusta(
            df_r_fundeb[df_r_fundeb['Subcategoria'] == 'ETI'], meses_disponiveis
        )

        # ── DESPESAS — APENAS FONTES DO ANO VIGENTE (15407 / 15403) ──────────
        # Fontes 25407 / 25403 = superávit de anos anteriores → aparecem no
        # gráfico com destaque diferenciado, mas NÃO entram no índice 70%.
        df_df_fundeb = df_df_raw[
            df_df_raw['Fonte'].str.contains('1540|2540', na=False)
        ].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb['Fonte'].apply(
            lambda x: 'FUNDEB 70%' if '15407' in str(x) or '25407' in str(x) else 'FUNDEB 30%'
        )
        df_df_fundeb['Ano_Vigente'] = df_df_fundeb['Fonte'].apply(
            lambda x: True if x in ['15407', '15403'] else False
        )

        # Índice 70%: Liquidado FUNDEB 70% SOMENTE do ano vigente (15407)
        # VAAR e ETI não entram no denominador — base = Principal + Rendimentos
        base_indice_70 = obter_soma_mensal_robusta(
            df_r_fundeb[df_r_fundeb['Subcategoria'].isin(['Principal', 'Rendimentos'])],
            meses_disponiveis
        )
        desp_70_vigente = obter_soma_mensal_robusta(
            df_df_fundeb[
                (df_df_fundeb['Fonte'] == '15407') &
                (df_df_fundeb['Tipo'] == 'Liquidado')
            ],
            meses_disponiveis
        )
        perc_70_indice = (desp_70_vigente / base_indice_70 * 100) if base_indice_70 > 0 else 0.0

        # Total despesas liquidadas no período (ano vigente)
        tot_desp_vigente = obter_soma_mensal_robusta(
            df_df_fundeb[
                df_df_fundeb['Ano_Vigente'] &
                (df_df_fundeb['Tipo'] == 'Liquidado')
            ],
            meses_disponiveis
        )
        # Superávit de anos anteriores (25407 / 25403)
        tot_desp_superavit = obter_soma_mensal_robusta(
            df_df_fundeb[
                ~df_df_fundeb['Ano_Vigente'] &
                (df_df_fundeb['Tipo'] == 'Liquidado')
            ],
            meses_disponiveis
        )

        # ── ITEM 1: CARDS DE PREVISÃO (sem percentual) ───────────────────────
        st.markdown("##### Previsões Orçamentárias")
        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric(
                "Previsão Receitas (Orçamento Município)",
                formar_real(tot_prev_municipio)
            )
        with p2:
            st.metric(
                "Previsão de Receitas (Port. Intermin. nº 14/dez 2025)",
                formar_real(tot_prev_portaria)
            )
        with p3:
            st.metric("Atualização Quadrimestral", "—")

        st.markdown("---")

        # ── GRÁFICO 1: RECEITAS + DESPESAS UNIFICADO ─────────────────────────
        st.subheader("🔹 1. Receitas e Despesas FUNDEB")

        # Totalizadores abaixo do título
        t1, t2, t3 = st.columns(3)
        with t1:
            st.metric(
                f"Total Receitas ({meses_disponiveis[0]}–{meses_disponiveis[-1]})",
                formar_real(tot_rec_periodo)
            )
        with t2:
            st.metric(
                f"Total Despesas Liquidadas – Ano Vigente",
                formar_real(tot_desp_vigente)
            )
        with t3:
            saldo = tot_rec_periodo - tot_desp_vigente
            exec_perc = (tot_desp_vigente / tot_rec_periodo * 100) if tot_rec_periodo > 0 else 0
            st.metric(
                "Saldo (Receitas − Despesas Vigentes)",
                formar_real(saldo),
                delta=f"{exec_perc:.1f}% executado",
                delta_color="inverse"
            )

        # ITEM 5: Mensal primeiro, depois Acumulado
        tipo_rd = st.segmented_control(
            "Visualização:", ["Mensal", "Acumulado"], default="Mensal", key="rd_btn_f"
        )

        # Paleta de cores para receitas (verde/teal/azul — imagem enviada)
        COR_REC = {
            'Principal':    '#1a7a4a',   # verde escuro
            'VAAR/VAAT':    '#2ecc71',   # verde médio
            'ETI':          '#17a589',   # teal
            'Rendimentos':  '#1abc9c',   # teal claro
        }
        COR_DESP = {
            'FUNDEB 70% – Vigente':    '#660000',
            'FUNDEB 30% – Vigente':    '#cc0000',
            'FUNDEB 70% – Superávit':  '#8B4513',
            'FUNDEB 30% – Superávit':  '#CD853F',
        }

        if tipo_rd == "Mensal":
            fig_rd = go.Figure()
            categorias_rec = list(df_r_fundeb['Subcategoria'].unique())
            legendas_usadas = set()

            for m in meses_disponiveis:
                tot_rec_m  = obter_soma_mensal_robusta(df_r_fundeb, [m])
                tot_desp_m = obter_soma_mensal_robusta(
                    df_df_fundeb[df_df_fundeb['Ano_Vigente'] & (df_df_fundeb['Tipo'] == 'Liquidado')], [m]
                )

                # ─ Receitas empilhadas por subcategoria ─
                for cat in categorias_rec:
                    val = obter_soma_mensal_robusta(
                        df_r_fundeb[df_r_fundeb['Subcategoria'] == cat], [m]
                    )
                    desc_list = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat]['Descrição da Receita'].str.strip().unique().tolist()
                    show_leg  = f"rec_{cat}" not in legendas_usadas
                    legendas_usadas.add(f"rec_{cat}")
                    part = f"{(val/tot_rec_m*100):.1f}%" if tot_rec_m > 0 else "—"

                    # Texto dentro da barra apenas se valor > 0
                    texto_barra = formar_real(val) if val > 0 else ""

                    fig_rd.add_trace(go.Bar(
                        name=cat,
                        x=[[m], ["Receitas"]],
                        y=[val],
                        marker_color=COR_REC.get(cat, '#27ae60'),
                        legendgroup=f"rec_{cat}",
                        showlegend=show_leg,
                        text=texto_barra,
                        textposition='inside',
                        insidetextanchor='middle',
                        customdata=[[cat, "FUNDEB", " | ".join(desc_list),
                                     formar_real(val), formar_real(tot_rec_m), part, m]],
                        hovertemplate=(
                            "<span style='color:white;'>"
                            "<b>📥 %{customdata[6]} — Receita %{customdata[0]}</b><br>"
                            "Categoria: %{customdata[0]}<br>"
                            "Fundo: %{customdata[1]}<br>"
                            "Rubrica(s): %{customdata[2]}<br>"
                            "─────────────────────<br>"
                            "Valor: <b>%{customdata[3]}</b><br>"
                            "Total Rec. mês: %{customdata[4]}<br>"
                            "Participação: %{customdata[5]}"
                            "</span><extra></extra>"
                        ),
                    ))

                # ─ Despesas ano vigente empilhadas ─
                for fonte_cod, label_desp in [('15407','FUNDEB 70% – Vigente'), ('15403','FUNDEB 30% – Vigente')]:
                    val = obter_soma_mensal_robusta(
                        df_df_fundeb[(df_df_fundeb['Fonte'] == fonte_cod) & (df_df_fundeb['Tipo'] == 'Liquidado')], [m]
                    )
                    show_leg = label_desp not in legendas_usadas
                    legendas_usadas.add(label_desp)
                    prop = f"{(val/tot_desp_m*100):.1f}%" if tot_desp_m > 0 else "—"
                    texto_barra = formar_real(val) if val > 0 else ""
                    fig_rd.add_trace(go.Bar(
                        name=label_desp,
                        x=[[m], ["Despesas"]],
                        y=[val],
                        marker_color=COR_DESP[label_desp],
                        legendgroup=label_desp,
                        showlegend=show_leg,
                        text=texto_barra,
                        textposition='inside',
                        insidetextanchor='middle',
                        customdata=[[fonte_cod, "Liquidado – Ano Vigente",
                                     prop, formar_real(val), formar_real(tot_desp_m), prop, m]],
                        hovertemplate=(
                            "<span style='color:white;'>"
                            "<b>📤 %{customdata[6]} — %{customdata[0]}</b><br>"
                            "Fonte: %{customdata[0]}<br>"
                            "Estágio: %{customdata[1]}<br>"
                            "─────────────────────<br>"
                            "Valor: <b>%{customdata[3]}</b><br>"
                            "Total Desp. vigentes mês: %{customdata[4]}<br>"
                            "Participação: %{customdata[5]}"
                            "</span><extra></extra>"
                        ),
                    ))

                # ─ Despesas superávit (anos anteriores) ─
                for fonte_cod, label_desp in [('25407','FUNDEB 70% – Superávit'), ('25403','FUNDEB 30% – Superávit')]:
                    val = obter_soma_mensal_robusta(
                        df_df_fundeb[(df_df_fundeb['Fonte'] == fonte_cod) & (df_df_fundeb['Tipo'] == 'Liquidado')], [m]
                    )
                    if val == 0: continue
                    show_leg = label_desp not in legendas_usadas
                    legendas_usadas.add(label_desp)
                    texto_barra = f"⚠️ {formar_real(val)}"
                    fig_rd.add_trace(go.Bar(
                        name=label_desp,
                        x=[[m], ["Despesas"]],
                        y=[val],
                        marker_color=COR_DESP[label_desp],
                        marker_pattern_shape="/",
                        legendgroup=label_desp,
                        showlegend=show_leg,
                        text=texto_barra,
                        textposition='inside',
                        insidetextanchor='middle',
                        customdata=[[fonte_cod, "Liquidado – Superávit Anos Anteriores",
                                     "⚠️ Não computa no índice 70% do ano vigente",
                                     formar_real(val), m]],
                        hovertemplate=(
                            "<span style='color:white;'>"
                            "<b>⚠️ %{customdata[4]} — Superávit Anos Anteriores</b><br>"
                            "Fonte: %{customdata[0]}<br>"
                            "Estágio: %{customdata[1]}<br>"
                            "Obs.: %{customdata[2]}<br>"
                            "─────────────────────<br>"
                            "Valor: <b>%{customdata[3]}</b>"
                            "</span><extra></extra>"
                        ),
                    ))

        else:  # ACUMULADO
            fig_rd = go.Figure()
            categorias_rec  = list(df_r_fundeb['Subcategoria'].unique())
            legendas_usadas = set()

            # ─ Receitas ─
            for cat in categorias_rec:
                val = obter_soma_mensal_robusta(
                    df_r_fundeb[df_r_fundeb['Subcategoria'] == cat], meses_disponiveis
                )
                desc_list = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat]['Descrição da Receita'].str.strip().unique().tolist()
                part = f"{(val/tot_rec_periodo*100):.1f}%" if tot_rec_periodo > 0 else "—"
                texto_barra = formar_real(val) if val > 0 else ""
                fig_rd.add_trace(go.Bar(
                    name=cat,
                    x=[["Acumulado"], ["Receitas"]],
                    y=[val],
                    marker_color=COR_REC.get(cat, '#27ae60'),
                    legendgroup=f"rec_{cat}",
                    showlegend=True,
                    text=texto_barra,
                    textposition='inside',
                    insidetextanchor='middle',
                    customdata=[[cat, "FUNDEB", " | ".join(desc_list),
                                 formar_real(val), formar_real(tot_rec_periodo), part]],
                    hovertemplate=(
                        "<span style='color:white;'>"
                        "<b>📥 Receita — %{customdata[0]}</b><br>"
                        "Categoria: %{customdata[0]}<br>"
                        "Fundo: %{customdata[1]}<br>"
                        "Rubrica(s): %{customdata[2]}<br>"
                        "─────────────────────<br>"
                        "Valor: <b>%{customdata[3]}</b><br>"
                        "Total Receitas: %{customdata[4]}<br>"
                        "Participação: %{customdata[5]}"
                        "</span><extra></extra>"
                    ),
                ))

            # ─ Despesas vigentes ─
            for fonte_cod, label_desp in [('15407','FUNDEB 70% – Vigente'), ('15403','FUNDEB 30% – Vigente')]:
                val = obter_soma_mensal_robusta(
                    df_df_fundeb[(df_df_fundeb['Fonte'] == fonte_cod) & (df_df_fundeb['Tipo'] == 'Liquidado')],
                    meses_disponiveis
                )
                prop = f"{(val/tot_desp_vigente*100):.1f}%" if tot_desp_vigente > 0 else "—"
                texto_barra = formar_real(val) if val > 0 else ""
                fig_rd.add_trace(go.Bar(
                    name=label_desp,
                    x=[["Acumulado"], ["Despesas"]],
                    y=[val],
                    marker_color=COR_DESP[label_desp],
                    legendgroup=label_desp,
                    showlegend=True,
                    text=texto_barra,
                    textposition='inside',
                    insidetextanchor='middle',
                    customdata=[[fonte_cod, "Liquidado – Ano Vigente",
                                 prop, formar_real(val), formar_real(tot_desp_vigente), prop]],
                    hovertemplate=(
                        "<span style='color:white;'>"
                        "<b>📤 Despesa — %{customdata[0]}</b><br>"
                        "Fonte: %{customdata[0]}<br>"
                        "Estágio: %{customdata[1]}<br>"
                        "─────────────────────<br>"
                        "Valor: <b>%{customdata[3]}</b><br>"
                        "Total Desp. vigentes: %{customdata[4]}<br>"
                        "Participação: %{customdata[5]}"
                        "</span><extra></extra>"
                    ),
                ))

            # ─ Despesas superávit ─
            for fonte_cod, label_desp in [('25407','FUNDEB 70% – Superávit'), ('25403','FUNDEB 30% – Superávit')]:
                val = obter_soma_mensal_robusta(
                    df_df_fundeb[(df_df_fundeb['Fonte'] == fonte_cod) & (df_df_fundeb['Tipo'] == 'Liquidado')],
                    meses_disponiveis
                )
                if val == 0: continue
                texto_barra = f"⚠️ {formar_real(val)}"
                fig_rd.add_trace(go.Bar(
                    name=label_desp,
                    x=[["Acumulado"], ["Despesas"]],
                    y=[val],
                    marker_color=COR_DESP[label_desp],
                    marker_pattern_shape="/",
                    legendgroup=label_desp,
                    showlegend=True,
                    text=texto_barra,
                    textposition='inside',
                    insidetextanchor='middle',
                    customdata=[[fonte_cod, "Liquidado – Superávit Anos Anteriores",
                                 "⚠️ Não computa no índice 70% vigente",
                                 formar_real(val)]],
                    hovertemplate=(
                        "<span style='color:white;'>"
                        "<b>⚠️ Superávit Anos Anteriores — %{customdata[0]}</b><br>"
                        "Fonte: %{customdata[0]}<br>"
                        "Estágio: %{customdata[1]}<br>"
                        "Obs.: %{customdata[2]}<br>"
                        "─────────────────────<br>"
                        "Valor: <b>%{customdata[3]}</b>"
                        "</span><extra></extra>"
                    ),
                ))

        fig_rd.update_layout(
            separators=",.",
            barmode='stack',
            hoverlabel=HOVER_STYLE,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.30, xanchor="center", x=0.5),
            height=500,
            yaxis=dict(showticklabels=False),
            uniformtext_minsize=9,
            uniformtext_mode='hide',
        )
        st.plotly_chart(fig_rd, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

        # ── GRÁFICO 2: COMPARATIVO ÍNDICE 70% — SOMENTE ACUMULADO ───────────
        # ITEM 6: destaque do índice 70% apenas no acumulado
        st.subheader("🔹 2. Índice de Aplicação em Pessoal (Mín. 70%)")

        # Nota metodológica
        st.info(
            "**Base de cálculo:** receitas de Principal + Rendimentos (VAAR/VAAT e ETI não compõem o denominador). "
            "**Numerador:** despesas liquidadas pela fonte 15407 (ano vigente). "
            "Despesas de fontes 25407/25403 (superávit de anos anteriores) são exibidas no gráfico mas **não** compõem o índice."
        )

        # Cards do índice
        i1, i2, i3 = st.columns(3)
        with i1: st.metric("Base de Cálculo (Principal + Rendimentos)", formar_real(base_indice_70))
        with i2: st.metric("Despesas FUNDEB 70% – Ano Vigente (Liquidado)", formar_real(desp_70_vigente))
        with i3: metric_contabil("Aplicação em Pessoal (Mín. 70%)", perc_70_indice, 70.0)

        # Gráfico acumulado de comparação
        df_c = pd.DataFrame({
            "Categoria": ["Receita Base\n(Principal + Rendimentos)", "Despesas 70%\n(Ano Vigente)"],
            "Valor":     [base_indice_70, desp_70_vigente],
            "Texto":     [formar_real(base_indice_70), f"{formar_real(desp_70_vigente)}\n({perc_70_indice:.2f}%)"],
        })
        cor_barra = "#27ae60" if perc_70_indice >= 70 else "#e74c3c"
        fig_70 = go.Figure()
        fig_70.add_trace(go.Bar(
            x=["Receita Base\n(Principal + Rendimentos)"],
            y=[base_indice_70],
            name="Receita Base",
            marker_color="#003366",
            text=[formar_real(base_indice_70)],
            textposition='inside',
            insidetextanchor='middle',
            hovertemplate="<span style='color:white;'><b>Receita Base FUNDEB</b><br>Principal + Rendimentos<br>Valor: <b>" + formar_real(base_indice_70) + "</b></span><extra></extra>",
        ))
        fig_70.add_trace(go.Bar(
            x=["Despesas 70%\n(Ano Vigente – Liquidado)"],
            y=[desp_70_vigente],
            name=f"Despesas 70% — {perc_70_indice:.2f}%",
            marker_color=cor_barra,
            text=[f"{formar_real(desp_70_vigente)}\n({perc_70_indice:.2f}%)"],
            textposition='inside',
            insidetextanchor='middle',
            hovertemplate=(
                "<span style='color:white;'><b>Despesas FUNDEB 70% – Vigente</b><br>"
                "Fonte: 15407 | Liquidado<br>"
                "Valor: <b>" + formar_real(desp_70_vigente) + "</b><br>"
                "Índice: <b>" + f"{perc_70_indice:.2f}%" + "</b></span><extra></extra>"
            ),
        ))
        fig_70.add_hline(
            y=base_indice_70 * 0.70,
            line_dash="dot", line_color="green", line_width=2,
            annotation_text=f"Meta 70% = {formar_real(base_indice_70 * 0.70)}",
            annotation_position="top left",
        )
        fig_70.update_layout(
            separators=",.",
            barmode='group',
            hoverlabel=HOVER_STYLE,
            yaxis=dict(showticklabels=False),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.20, xanchor="center", x=0.5),
            height=420,
        )
        st.plotly_chart(fig_70, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

        # ── ITEM 8: GRÁFICO 3 — PERCENTUAL TEMPO INTEGRAL (ETI) ─────────────
        st.subheader("🔹 3. Percentual Tempo Integral (ETI)")

        meta_eti_perc  = 4.0  # mínimo legal: 4% do total FUNDEB
        val_meta_eti   = base_indice_70 * (meta_eti_perc / 100)
        perc_eti_real  = (tot_eti / base_indice_70 * 100) if base_indice_70 > 0 else 0.0

        e1, e2, e3 = st.columns(3)
        with e1: st.metric("Receita ETI Recebida (período)", formar_real(tot_eti))
        with e2: st.metric(f"Valor Equivalente a {meta_eti_perc:.0f}% da Receita Base", formar_real(val_meta_eti))
        with e3: metric_contabil(f"ETI sobre Receita Base (Ref. {meta_eti_perc:.0f}%)", perc_eti_real, meta_eti_perc)

        cor_eti = "#27ae60" if perc_eti_real >= meta_eti_perc else "#e74c3c"
        fig_eti = go.Figure()
        fig_eti.add_trace(go.Bar(
            x=["Receita Base FUNDEB"],
            y=[base_indice_70],
            name="Receita Base",
            marker_color="#003366",
            text=[formar_real(base_indice_70)],
            textposition='inside',
            insidetextanchor='middle',
            hovertemplate="<span style='color:white;'><b>Receita Base FUNDEB</b><br>Valor: <b>" + formar_real(base_indice_70) + "</b></span><extra></extra>",
        ))
        fig_eti.add_trace(go.Bar(
            x=["ETI Recebido (período)"],
            y=[tot_eti],
            name=f"ETI — {perc_eti_real:.2f}% da base",
            marker_color=cor_eti,
            text=[f"{formar_real(tot_eti)}\n({perc_eti_real:.2f}%)"],
            textposition='inside',
            insidetextanchor='middle',
            hovertemplate=(
                "<span style='color:white;'><b>Receita ETI</b><br>"
                "Valor recebido: <b>" + formar_real(tot_eti) + "</b><br>"
                "% sobre receita base: <b>" + f"{perc_eti_real:.2f}%" + "</b><br>"
                "Meta de referência: <b>" + f"{meta_eti_perc:.0f}%" + " = " + formar_real(val_meta_eti) + "</b></span><extra></extra>"
            ),
        ))
        fig_eti.add_hline(
            y=val_meta_eti,
            line_dash="dot", line_color="#f39c12", line_width=2,
            annotation_text=f"Referência {meta_eti_perc:.0f}% = {formar_real(val_meta_eti)}",
            annotation_position="top left",
        )
        fig_eti.update_layout(
            separators=",.",
            barmode='group',
            hoverlabel=HOVER_STYLE,
            yaxis=dict(showticklabels=False),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.20, xanchor="center", x=0.5),
            height=400,
        )
        st.plotly_chart(fig_eti, use_container_width=True, config=CONFIG_PT)
        
        # --- SETOR RECURSOS PRÓPRIOS ---
    elif st.session_state.setor == 'Recursos Próprios':
        st.markdown("<h1 style='text-align: left;'>📖 Ibiraci - Recursos Próprios (25%)</h1>", unsafe_allow_html=True)
        
        # 1. Base de Cálculo (Denominador): Impostos e Cota-Parte
        df_r_base = df_r[df_r['Categoria'].str.strip().isin(['Impostos', 'Cota-Parte'])].copy()
        
        # --- CORREÇÃO DO ERRO (KEYERROR): Normalização de colunas ---
        # Garante que 'fevereiro' vire 'Fevereiro' para coincidir com meses_disponiveis
        df_r_base.columns = [c.capitalize() if c.lower() in [m.lower() for m in ORDEM_MESES] else c for c in df_r_base.columns]
        
        # 2. Correção na Coleta de Deduções
        df_r_ded = df_r[df_r['Categoria'].str.contains('Dedução', case=False, na=False)].copy()
        # Normaliza colunas das deduções também
        df_r_ded.columns = [c.capitalize() if c.lower() in [m.lower() for m in ORDEM_MESES] else c for c in df_r_ded.columns]
        
        # Seletor Global de Fase para Despesas 15001
        fase_despesa = st.segmented_control(" (Impacta Indicadores Superiores):", ["Empenhado", "Liquidado", "Pago"], default="Liquidado", key="fase_desp_rp")

        # 3. Despesas 15001
        df_df_15001 = df_df_raw[(df_df_raw['Fonte'] == '15001') & (df_df_raw['Tipo'] == fase_despesa)].copy()
        
        # Filtra meses que realmente existem após a normalização para evitar o crash no .sum()
        meses_reais = [m for m in meses_disponiveis if m in df_r_base.columns]
        
        total_rec_base = df_r_base[meses_reais].sum().sum()
        total_desp_15001 = df_df_15001[meses_reais].sum().sum()
        total_deducoes = abs(df_r_ded[meses_reais].sum().sum())
        
        # Lógica de cálculo para o índice
        esforco_total = total_desp_15001 + total_deducoes
        perc_25 = (esforco_total / total_rec_base * 100) if total_rec_base > 0 else 0
        
        meta_financeira_25 = total_rec_base * 0.25
        saldo_necessario_25 = max(0, meta_financeira_25 - esforco_total)
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Total das Despesas (Fonte 15001)", formar_real(total_desp_15001))
        with m2: st.metric("Saldo para atingir a meta (25%)", formar_real(saldo_necessario_25))
        with m3:
            # Supondo que perc_25 seja seu cálculo
            metric_contabil("Índice de Aplicação (Mín. 25%)", perc_25, 25.0)

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
        st.markdown("<h1 style='text-align: left;'>📖 Ibiraci - Recursos Vinculados</h1>", unsafe_allow_html=True)
        
        mapa_desp = {'PNAE': ['1552', '2552'], 'PNATE': ['1553', '2553'], 'PTE': ['1576', '2576'], 'QESE': ['1550', '2550']}
        programas = ['PNAE', 'PNATE', 'PTE', 'QESE']
        
        # Filtra as receitas e normaliza os nomes das colunas (limpa espaços e padroniza Capitalize)
        df_r_vinc = df_r[df_r['Descrição da Receita'].str.upper().str.strip().isin(programas)].copy()
        
        # --- NORMALIZAÇÃO DE COLUNAS (Evita KeyError: 'Março ') ---
        colunas_limpas_r = {c.strip().capitalize(): c for c in df_r_vinc.columns}
        colunas_limpas_df = {c.strip().capitalize(): c for c in df_df_raw.columns}
        
        meses_reais_r = [colunas_limpas_r[m] for m in meses_disponiveis if m in colunas_limpas_r]
        meses_reais_df = [colunas_limpas_df[m] for m in meses_disponiveis if m in colunas_limpas_df]

        # --- MÉTRICAS SUPERIORES ---
        m1, m2, m3 = st.columns(3)
        with m1: 
            st.metric("Previsão Vinculados 2026", formar_real(df_r_vinc['Orçado Receitas'].sum()))
        with m2: 
            total_arrec_vinc = df_r_vinc[meses_reais_r].sum().sum() if meses_reais_r else 0
            st.metric(f"Arrecadado ({meses_disponiveis[0]}-{meses_disponiveis[-1]})", formar_real(total_arrec_vinc))
        with m3:
            fontes_v = [f for sub in mapa_desp.values() for f in sub]
            df_vinc_filtro = df_df_raw[(df_df_raw['Fonte'].isin(fontes_v)) & (df_df_raw['Tipo'] == 'Liquidado')]
            total_liq_vinc = df_vinc_filtro[meses_reais_df].sum().sum() if meses_reais_df else 0
            st.metric(f"Liquidado ({meses_disponiveis[0]}-{meses_disponiveis[-1]})", formar_real(total_liq_vinc))

        st.markdown("---")
        st.subheader("🔹 1. Detalhamento de Receitas e Despesas por Programa")
        tipo_vinc = st.segmented_control("Visualização:", ["Acumulado", "Mensal"], default="Mensal", key="vinc_btn")

        for prog in programas:
            st.markdown(f"#### 📊 Programa: {prog}")
            prev_prog = df_r_vinc[df_r_vinc['Descrição da Receita'].str.upper().str.strip() == prog]['Orçado Receitas'].sum()
            st.markdown(f"**Previsão total de Receitas para 2026:** {formar_real(prev_prog)}")

            if tipo_vinc == "Acumulado":
                rec = df_r_vinc[df_r_vinc['Descrição da Receita'].str.upper().str.strip() == prog][meses_reais_r].sum().sum()
                desp = df_df_raw[(df_df_raw['Fonte'].isin(mapa_desp[prog])) & (df_df_raw['Tipo'] == 'Liquidado')][meses_reais_df].sum().sum()
                
                df_acum = pd.DataFrame({"Tipo": ["Receita", "Despesa"], "Valor": [rec, desp]})
                fig_vinc = px.bar(df_acum, x='Tipo', y='Valor', color='Tipo', text_auto='.2s',
                                  color_discrete_map={'Receita':'#002147', 'Despesa':'#660000'})
            else:
                dados_d_v = []
                for m in meses_disponiveis:
                    c_r = colunas_limpas_r.get(m)
                    c_df = colunas_limpas_df.get(m)
                    
                    rec_m = df_r_vinc[df_r_vinc['Descrição da Receita'].str.upper().str.strip() == prog][c_r].sum() if c_r else 0
                    desp_m = df_df_raw[(df_df_raw['Fonte'].isin(mapa_desp[prog])) & (df_df_raw['Tipo'] == 'Liquidado')][c_df].sum() if c_df else 0
                    
                    dados_d_v.append({"Mês": m, "Tipo": "Receita", "Valor": rec_m})
                    dados_d_v.append({"Mês": m, "Tipo": "Despesa", "Valor": desp_m})

                fig_vinc = px.bar(pd.DataFrame(dados_d_v), x='Mês', y='Valor', color='Tipo', barmode='group',
                                 color_discrete_map={'Receita':'#002147', 'Despesa':'#660000'},
                                 category_orders={"Mês": ORDEM_MESES})

            # --- FORMATAÇÃO PADRÃO DO HOVER (Selector evita erro de ValueError) ---
            fig_vinc.update_traces(
                selector=dict(type='bar'),
                hovertemplate="<span style='color:white;'><b>%{x}</b><br>Tipo: %{data.name}<br>Valor: R$ %{y:,.2f}</span><extra></extra>",
                hoverlabel=HOVER_STYLE,
                textposition='outside'
            )

            fig_vinc.update_layout(
                separators=",.", 
                xaxis_title=None, 
                yaxis_title="Valor (R$)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_vinc, use_container_width=True, config=CONFIG_PT)
            st.markdown("---")

    # --- RELATÓRIO DE FICHAS GLOBAL ---
    st.markdown("### 📋 Relatório Geral de Fichas")
    df_f_filt = df_f_raw[df_f_raw['Atividade'].str.contains(search_term, na=False, case=False)].copy()
    st.dataframe(df_f_filt, use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar os arquivos CSV. Verifique se os arquivos de Ibiraci estão no diretório correto.")