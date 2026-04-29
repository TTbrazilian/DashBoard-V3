import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import plotly.graph_objects as go
import streamlit.components.v1 as components

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="São Tomás de Aquino - Gestão Educação", layout="wide")

# --- ESTILIZAÇÃO ---
st.markdown("""
    <style>
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
            width: 100% !important; height: 45px !important;
            padding: 0px !important; font-size: 10px !important;
            font-weight: 700 !important; border-radius: 4px !important;
            white-space: nowrap !important;
            display: flex !important; align-items: center !important;
            justify-content: center !important; text-align: center;
            animation: slideIn 0.4s ease-out;
        }
        .stButton button:focus { outline: none !important; box-shadow: none !important; }
        [data-testid="column"] { display: flex; align-items: center; justify-content: center; }
    </style>
""", unsafe_allow_html=True)

pio.templates.default = "plotly_dark"
CONFIG_PT  = {'displaylogo': False, 'showTips': False}
HOVER_STYLE = dict(bgcolor="rgba(0,0,0,0.9)", font_size=13, font_family="Arial", font_color="white")

ORDEM_MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

if 'setor' not in st.session_state:
    st.session_state.setor = 'FUNDEB'

# --- FUNÇÕES UTILITÁRIAS ---
def limpar_valor(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "-", "R$ 0,00", "0"]:
        return 0.0
    s = str(valor).replace('R$','').replace(' ','').replace('.','').replace(',','.')
    try:
        if '(' in s and ')' in s: s = '-' + s.replace('(','').replace(')','')
        return float(s)
    except: return 0.0

def formar_real(valor):
    return f"R$ {valor:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def metric_contabil(label, valor_atual, meta):
    delta = valor_atual - meta
    status_icon = "✅" if valor_atual >= meta else "⚠️"
    return st.metric(label=label,
                     value=f"{status_icon} {valor_atual:.2f}%",
                     delta=f"{delta:.2f}%",
                     delta_color="normal")

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
    for longo, curto in mapeamento.items(): n = n.replace(longo, curto)
    n = n.replace("PRINCIPAL","PRIN.").replace("MULTAS E JUROS","M/J").replace("OUTRAS RECEITAS","OUTR.")
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
    arquivo_f  = "zEducação/São Tomás de Aquino.csv"
    arquivo_r  = "zEducação/São Tomás de Aquino_R.csv"
    arquivo_df = "zEducação/São Tomás de Aquino_DF.csv"

    path_f  = buscar_arquivo(arquivo_f)
    path_r  = buscar_arquivo(arquivo_r)
    path_df = buscar_arquivo(arquivo_df)
    if not path_f or not path_r or not path_df: return None, None, None

    # ── Fichas (F): cabeçalho duplo ──────────────────────────────────────────
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]: new_cols.append(col[1].strip())
        else: new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols

    # ── Receitas (R): header=0 — NÃO usar header=1 ───────────────────────────
    # O arquivo tem cabeçalho na linha 0 (Código, Categoria, Descrição da Receita,
    # Janeiro, Fevereiro, ..., Orçado Receitas, Repasse, 2025).
    # Usar header=1 destrói os nomes das colunas e invalida todos os dados.
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=0)
    df_r.columns = [str(c).strip() for c in df_r.columns]

    # ── Despesas por fonte (DF) ───────────────────────────────────────────────
    df_df = pd.read_csv(path_df, sep=None, engine='python', encoding='utf-8')
    df_df.columns = [str(c).strip() for c in df_df.columns]

    # ── Limpeza numérica ─────────────────────────────────────────────────────
    # F: colunas com sufixo de tipo
    for col in df_f.columns:
        if any(k in col for k in ['Orçado','Saldo','Liquidado','Empenhado','Pago','Creditado','Anulado']):
            df_f[col] = df_f[col].apply(limpar_valor)

    # R: todos os meses + colunas financeiras extras do São Tomás
    COLS_NUM_R = ORDEM_MESES + ['Total', 'Orçado Receitas', 'Repasse', '2025']
    for col in df_r.columns:
        if col in COLS_NUM_R:
            df_r[col] = df_r[col].apply(limpar_valor)

    # DF: todos os meses
    for col in df_df.columns:
        if col in ORDEM_MESES + ['Total']:
            df_df[col] = df_df[col].apply(limpar_valor)

    # ── Padronizar Fonte ──────────────────────────────────────────────────────
    if 'Fonte' in df_f.columns:
        df_f['Fonte'] = df_f['Fonte'].astype(str).str.replace('.0','',regex=False).str.strip()
    if 'Fonte' in df_df.columns:
        df_df['Fonte'] = df_df['Fonte'].astype(str).str.replace('.0','',regex=False).str.strip()

    return df_f, df_r, df_df

df_f_raw, df_r, df_df_raw = load_all_data()

# --- MESES DISPONÍVEIS ---
meses_disponiveis = ['Janeiro', 'Fevereiro']

if df_f_raw is not None and df_r is not None:
    # --- SIDEBAR ---
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Filtrar Fichas:", "")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Setores")
    if st.sidebar.button("FUNDEB", use_container_width=True):           st.session_state.setor = 'FUNDEB'
    if st.sidebar.button("Recursos Próprios", use_container_width=True): st.session_state.setor = 'Recursos Próprios'
    if st.sidebar.button("Recursos Vinculados", use_container_width=True): st.session_state.setor = 'Recursos Vinculados'

    # =========================================================================
    # SETOR FUNDEB
    # =========================================================================
    if st.session_state.setor == 'FUNDEB':
        st.markdown("<h1 style='text-align: left;'>📖 São Tomás de Aquino - FUNDEB</h1>",
                    unsafe_allow_html=True)

        def cat_receita(desc):
            d = str(desc).upper().strip()
            if 'VAAR' in d or 'VAAT' in d:             return 'VAAR/VAAT'
            if 'ETI' in d or 'TEMPO INTEGRAL' in d:    return 'ETI'
            if 'APLICAÇÃO' in d or 'RENDIMENTOS' in d: return 'Rendimentos'
            return 'Principal'

        def soma(df, cols):
            presentes = [c for c in cols if c in df.columns]
            return df[presentes].sum().sum() if presentes else 0.0

        # ── RECEITAS ─────────────────────────────────────────────────────────
        df_r_fundeb = df_r[df_r['Categoria'].str.strip() == 'FUNDEB'].copy()
        df_r_fundeb['Descrição da Receita'] = df_r_fundeb['Descrição da Receita'].str.strip()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)

        tot_prev_municipio = df_r_fundeb[
            df_r_fundeb['Subcategoria'] == 'Principal'
        ]['Orçado Receitas'].sum()                          # R$ 6.650.000,00

        tot_prev_portaria  = df_r_fundeb['Repasse'].sum()   # R$ 6.351.300,40
        tot_rec_periodo    = soma(df_r_fundeb, meses_disponiveis)  # R$ 1.170.192,01
        tot_eti            = soma(df_r_fundeb[df_r_fundeb['Subcategoria'] == 'ETI'],
                                  meses_disponiveis)        # R$ 0,00

        # ── DESPESAS — APENAS FONTES DO ANO VIGENTE (15407 / 15403) ──────────
        df_df_fundeb = df_df_raw[
            df_df_raw['Fonte'].isin(['15407', '15403'])
        ].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb['Fonte'].apply(
            lambda x: 'FUNDEB 70%' if x == '15407' else 'FUNDEB 30%'
        )

        base_indice_70  = soma(
            df_r_fundeb[df_r_fundeb['Subcategoria'].isin(['Principal', 'Rendimentos'])],
            meses_disponiveis
        )                                                   # R$ 1.170.192,01
        desp_70_vigente = soma(
            df_df_fundeb[(df_df_fundeb['Fonte'] == '15407') & (df_df_fundeb['Tipo'] == 'Liquidado')],
            meses_disponiveis
        )                                                   # R$ 1.010.067,36
        desp_30_vigente = soma(
            df_df_fundeb[(df_df_fundeb['Fonte'] == '15403') & (df_df_fundeb['Tipo'] == 'Liquidado')],
            meses_disponiveis
        )                                                   # R$ 40.399,44
        tot_desp_vigente = desp_70_vigente + desp_30_vigente   # R$ 1.050.466,80
        perc_70_indice   = (desp_70_vigente / base_indice_70 * 100) if base_indice_70 > 0 else 0.0
        # 86,32%

        # ── CARDS DE PREVISÃO ─────────────────────────────────────────────────
        st.markdown("##### Previsões Orçamentárias")
        p1, p2, p3 = st.columns(3)
        with p1: st.metric("Previsão Receitas (Orçamento Município)",
                            formar_real(tot_prev_municipio))
        with p2: st.metric("Previsão de Receitas (Port. Intermin. nº 14/dez 2025)",
                            formar_real(tot_prev_portaria))
        with p3: st.metric("Atualização Quadrimestral", "—")

        st.markdown("---")

        # ── GRÁFICO 1: RECEITAS + DESPESAS ───────────────────────────────────
        st.subheader("🔹 1. Receitas e Despesas FUNDEB")

        t1, t2, t3 = st.columns(3)
        with t1: st.metric(f"Total Receitas ({meses_disponiveis[0]}–{meses_disponiveis[-1]})",
                            formar_real(tot_rec_periodo))
        with t2: st.metric("Total Despesas Liquidadas – Ano Vigente",
                            formar_real(tot_desp_vigente))
        with t3:
            saldo     = tot_rec_periodo - tot_desp_vigente
            exec_perc = (tot_desp_vigente / tot_rec_periodo * 100) if tot_rec_periodo > 0 else 0
            st.metric("Saldo (Receitas − Despesas Vigentes)", formar_real(saldo),
                      delta=f"{exec_perc:.1f}% executado", delta_color="inverse")

        tipo_rd = st.segmented_control("Visualização:", ["Mensal", "Acumulado"],
                                       default="Mensal", key="rd_btn_f")

        # ── CORES RECEITAS: verde/azul por subcategoria ───────────────────────
        # Principal    → verde escuro
        # Rendimentos  → azul
        # VAAR/VAAT    → verde claro
        # ETI          → azul claro
        COR_REC = {
            'Principal':   '#1a7a4a',   # verde escuro
            'Rendimentos': '#1565c0',   # azul
            'VAAR/VAAT':   '#66bb6a',   # verde claro
            'ETI':         '#42a5f5',   # azul claro
        }
        # ── CORES DESPESAS: vermelho — 70% mais escuro, 30% mais claro ────────
        COR_DESP = {
            'FUNDEB 70% – Vigente': '#8b0000',   # vermelho escuro
            'FUNDEB 30% – Vigente': '#e53935',   # vermelho mais claro
        }

        fig_rd = go.Figure()
        categorias_rec  = list(df_r_fundeb['Subcategoria'].unique())
        legendas_usadas = set()

        if tipo_rd == "Mensal":
            for m in meses_disponiveis:
                tot_rec_m  = soma(df_r_fundeb, [m])
                tot_desp_m = soma(df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado'], [m])

                for cat in categorias_rec:
                    val = soma(df_r_fundeb[df_r_fundeb['Subcategoria'] == cat], [m])
                    desc_list = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat][
                        'Descrição da Receita'].unique().tolist()
                    show_leg = f"rec_{cat}" not in legendas_usadas
                    legendas_usadas.add(f"rec_{cat}")
                    part = f"{(val/tot_rec_m*100):.1f}%" if tot_rec_m > 0 else "—"
                    fig_rd.add_trace(go.Bar(
                        name=cat, x=[[m], ["Receitas"]], y=[val],
                        marker_color=COR_REC.get(cat, '#27ae60'),
                        legendgroup=f"rec_{cat}", showlegend=show_leg,
                        text=formar_real(val) if val > 0 else "",
                        textposition='inside', insidetextanchor='middle',
                        customdata=[[cat, "FUNDEB", " | ".join(desc_list),
                                     formar_real(val), formar_real(tot_rec_m), part, m]],
                        hovertemplate=(
                            "<span style='color:white;'>"
                            "<b>📥 %{customdata[6]} — Receita %{customdata[0]}</b><br>"
                            "Categoria: %{customdata[0]}<br>Fundo: %{customdata[1]}<br>"
                            "Rubrica(s): %{customdata[2]}<br>─────────────────────<br>"
                            "Valor: <b>%{customdata[3]}</b><br>"
                            "Total Rec. mês: %{customdata[4]}<br>"
                            "Participação: %{customdata[5]}</span><extra></extra>"
                        ),
                    ))

                for fonte_cod, label_desp in [('15407', 'FUNDEB 70% – Vigente'),
                                              ('15403', 'FUNDEB 30% – Vigente')]:
                    val = soma(df_df_fundeb[
                        (df_df_fundeb['Fonte'] == fonte_cod) &
                        (df_df_fundeb['Tipo'] == 'Liquidado')], [m])
                    show_leg = label_desp not in legendas_usadas
                    legendas_usadas.add(label_desp)
                    prop = f"{(val/tot_desp_m*100):.1f}%" if tot_desp_m > 0 else "—"
                    fig_rd.add_trace(go.Bar(
                        name=label_desp, x=[[m], ["Despesas"]], y=[val],
                        marker_color=COR_DESP[label_desp],
                        legendgroup=label_desp, showlegend=show_leg,
                        text=formar_real(val) if val > 0 else "",
                        textposition='inside', insidetextanchor='middle',
                        customdata=[[fonte_cod, "Liquidado – Ano Vigente", prop,
                                     formar_real(val), formar_real(tot_desp_m), prop, m]],
                        hovertemplate=(
                            "<span style='color:white;'>"
                            "<b>📤 %{customdata[6]} — %{customdata[0]}</b><br>"
                            "Fonte: %{customdata[0]}<br>Estágio: %{customdata[1]}<br>"
                            "─────────────────────<br>Valor: <b>%{customdata[3]}</b><br>"
                            "Total Desp. mês: %{customdata[4]}<br>"
                            "Participação: %{customdata[5]}</span><extra></extra>"
                        ),
                    ))

        else:  # ACUMULADO
            for cat in categorias_rec:
                val = soma(df_r_fundeb[df_r_fundeb['Subcategoria'] == cat], meses_disponiveis)
                desc_list = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat][
                    'Descrição da Receita'].unique().tolist()
                part = f"{(val/tot_rec_periodo*100):.1f}%" if tot_rec_periodo > 0 else "—"
                fig_rd.add_trace(go.Bar(
                    name=cat, x=[["Acumulado"], ["Receitas"]], y=[val],
                    marker_color=COR_REC.get(cat, '#27ae60'),
                    legendgroup=f"rec_{cat}", showlegend=True,
                    text=formar_real(val) if val > 0 else "",
                    textposition='inside', insidetextanchor='middle',
                    customdata=[[cat, "FUNDEB", " | ".join(desc_list),
                                 formar_real(val), formar_real(tot_rec_periodo), part]],
                    hovertemplate=(
                        "<span style='color:white;'>"
                        "<b>📥 Receita — %{customdata[0]}</b><br>"
                        "Categoria: %{customdata[0]}<br>Fundo: %{customdata[1]}<br>"
                        "Rubrica(s): %{customdata[2]}<br>─────────────────────<br>"
                        "Valor: <b>%{customdata[3]}</b><br>"
                        "Total Receitas: %{customdata[4]}<br>"
                        "Participação: %{customdata[5]}</span><extra></extra>"
                    ),
                ))

            for fonte_cod, label_desp in [('15407', 'FUNDEB 70% – Vigente'),
                                          ('15403', 'FUNDEB 30% – Vigente')]:
                val = soma(df_df_fundeb[
                    (df_df_fundeb['Fonte'] == fonte_cod) &
                    (df_df_fundeb['Tipo'] == 'Liquidado')], meses_disponiveis)
                prop = f"{(val/tot_desp_vigente*100):.1f}%" if tot_desp_vigente > 0 else "—"
                fig_rd.add_trace(go.Bar(
                    name=label_desp, x=[["Acumulado"], ["Despesas"]], y=[val],
                    marker_color=COR_DESP[label_desp],
                    legendgroup=label_desp, showlegend=True,
                    text=formar_real(val) if val > 0 else "",
                    textposition='inside', insidetextanchor='middle',
                    customdata=[[fonte_cod, "Liquidado – Ano Vigente", prop,
                                 formar_real(val), formar_real(tot_desp_vigente), prop]],
                    hovertemplate=(
                        "<span style='color:white;'>"
                        "<b>📤 Despesa — %{customdata[0]}</b><br>"
                        "Fonte: %{customdata[0]}<br>Estágio: %{customdata[1]}<br>"
                        "─────────────────────<br>Valor: <b>%{customdata[3]}</b><br>"
                        "Total Desp. vigentes: %{customdata[4]}<br>"
                        "Participação: %{customdata[5]}</span><extra></extra>"
                    ),
                ))

        fig_rd.update_layout(
            separators=",.", barmode='stack', hoverlabel=HOVER_STYLE,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.30, xanchor="center", x=0.5),
            height=500, yaxis=dict(showticklabels=False),
            uniformtext_minsize=9, uniformtext_mode='hide',
        )
        st.plotly_chart(fig_rd, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

        # ── GRÁFICO 2: ÍNDICE 70% — MENSAL E ACUMULADO ───────────────────────
        # Card de índice removido conforme solicitado.
        # Aplicação (metric_contabil) exibida apenas na visão Acumulado.
        # Despesas sempre em tons de vermelho.
        st.subheader("🔹 2. Índice de Aplicação em Pessoal (Mín. 70%)")

        tipo_70 = st.segmented_control("Visualização:", ["Mensal", "Acumulado"],
                                       default="Mensal", key="tipo_70_btn")

        if tipo_70 == "Acumulado":
            # Exibe o metric_contabil apenas no acumulado
            a1, a2 = st.columns(2)
            with a1: st.metric("Base de Cálculo (Principal + Rendimentos)",
                                formar_real(base_indice_70))
            with a2: st.metric("Despesas FUNDEB 70% – Liquidado",
                                formar_real(desp_70_vigente))
            metric_contabil("Aplicação em Pessoal (Mín. 70%)", perc_70_indice, 70.0)

            cor_barra = "#27ae60" if perc_70_indice >= 70 else "#e74c3c"
            fig_70 = go.Figure()
            fig_70.add_trace(go.Bar(
                x=["Receita Base\n(Principal + Rendimentos)"], y=[base_indice_70],
                name="Receita Base", marker_color="#003366",
                text=[formar_real(base_indice_70)],
                textposition='inside', insidetextanchor='middle',
                hovertemplate=("<span style='color:white;'><b>Receita Base FUNDEB</b><br>"
                               "Valor: <b>" + formar_real(base_indice_70) +
                               "</b></span><extra></extra>"),
            ))
            fig_70.add_trace(go.Bar(
                x=["Despesas 70%\n(Liquidado)"], y=[desp_70_vigente],
                name=f"Despesas 70% — {perc_70_indice:.2f}%",
                marker_color='#8b0000',   # vermelho escuro
                text=[f"{formar_real(desp_70_vigente)}\n({perc_70_indice:.2f}%)"],
                textposition='inside', insidetextanchor='middle',
                hovertemplate=("<span style='color:white;'><b>Despesas FUNDEB 70%</b><br>"
                               "Fonte: 15407 | Liquidado<br>"
                               "Valor: <b>" + formar_real(desp_70_vigente) + "</b><br>"
                               "Índice: <b>" + f"{perc_70_indice:.2f}%" +
                               "</b></span><extra></extra>"),
            ))
            fig_70.add_hline(y=base_indice_70 * 0.70, line_dash="dot", line_color="green",
                             annotation_text=f"Meta 70% = {formar_real(base_indice_70 * 0.70)}",
                             annotation_position="top left")
            fig_70.update_layout(
                separators=",.", barmode='group', hoverlabel=HOVER_STYLE,
                yaxis=dict(showticklabels=False), showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.20,
                            xanchor="center", x=0.5), height=420
            )
            st.plotly_chart(fig_70, use_container_width=True, config=CONFIG_PT)

        else:  # MENSAL
            # Sem metric_contabil no mensal
            dados_70_m = []
            for m in meses_disponiveis:
                base_m   = soma(df_r_fundeb[df_r_fundeb['Subcategoria'].isin(
                                    ['Principal', 'Rendimentos'])], [m])
                liq_70_m = soma(df_df_fundeb[
                    (df_df_fundeb['Fonte'] == '15407') &
                    (df_df_fundeb['Tipo'] == 'Liquidado')], [m])
                liq_30_m = soma(df_df_fundeb[
                    (df_df_fundeb['Fonte'] == '15403') &
                    (df_df_fundeb['Tipo'] == 'Liquidado')], [m])
                perc_m   = (liq_70_m / base_m * 100) if base_m > 0 else 0.0
                dados_70_m.append({"Mês": m, "Tipo": "Receita Base",
                                   "Valor": base_m, "Texto": ""})
                dados_70_m.append({"Mês": m, "Tipo": "FUNDEB 70% (Liquidado)",
                                   "Valor": liq_70_m, "Texto": f"{perc_m:.1f}%"})
                dados_70_m.append({"Mês": m, "Tipo": "FUNDEB 30% (Liquidado)",
                                   "Valor": liq_30_m, "Texto": ""})

            fig_70 = px.bar(
                pd.DataFrame(dados_70_m), x='Mês', y='Valor', color='Tipo',
                barmode='group', text='Texto',
                color_discrete_map={
                    "Receita Base":            "#003366",
                    "FUNDEB 70% (Liquidado)":  "#8b0000",   # vermelho escuro
                    "FUNDEB 30% (Liquidado)":  "#e53935",   # vermelho claro
                },
                category_orders={"Mês": ORDEM_MESES}
            )

            # Linha de meta 70% por mês
            df_meta_linha = pd.DataFrame([
                {"Mês": m,
                 "Meta 70%": soma(df_r_fundeb[df_r_fundeb['Subcategoria'].isin(
                     ['Principal', 'Rendimentos'])], [m]) * 0.70}
                for m in meses_disponiveis
            ])
            fig_70.add_trace(go.Scatter(
                x=df_meta_linha['Mês'], y=df_meta_linha['Meta 70%'],
                mode='lines+markers', name='Meta 70% (Mensal)',
                line=dict(color='green', dash='dot')
            ))

            fig_70.update_traces(
                selector=dict(type='bar'), textposition='outside',
                hovertemplate=(
                    "<span style='color:white;'><b>%{x} — %{data.name}</b><br>"
                    "Valor: <b>R$ %{y:,.2f}</b></span><extra></extra>"
                ),
                hoverlabel=HOVER_STYLE
            )
            fig_70.update_layout(
                separators=",.", yaxis=dict(showticklabels=False), showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.20,
                            xanchor="center", x=0.5), height=420
            )
            st.plotly_chart(fig_70, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

        # ── GRÁFICO 3: ETI ────────────────────────────────────────────────────
        # Removido o ícone de +/- (metric_contabil substituído por st.metric simples).
        # Exibe: total das receitas FUNDEB e equivalente a 4%.
        st.subheader("🔹 3. Percentual Tempo Integral (ETI)")

        meta_eti_perc = 4.0
        val_meta_eti  = base_indice_70 * (meta_eti_perc / 100)   # R$ 46.807,68
        perc_eti_real = (tot_eti / base_indice_70 * 100) if base_indice_70 > 0 else 0.0

        e1, e2 = st.columns(2)
        with e1:
            st.metric("Total Receitas FUNDEB (período)", formar_real(tot_rec_periodo))
        with e2:
            st.metric(f"Equivalente a {meta_eti_perc:.0f}% da Receita Base",
                      formar_real(val_meta_eti))

        cor_eti = "#27ae60" if perc_eti_real >= meta_eti_perc else "#e74c3c"
        fig_eti = go.Figure()
        fig_eti.add_trace(go.Bar(
            x=["Receita Base FUNDEB"], y=[base_indice_70],
            name="Receita Base", marker_color="#003366",
            text=[formar_real(base_indice_70)],
            textposition='inside', insidetextanchor='middle',
            hovertemplate=("<span style='color:white;'><b>Receita Base FUNDEB</b><br>"
                           "Valor: <b>" + formar_real(base_indice_70) +
                           "</b></span><extra></extra>"),
        ))
        fig_eti.add_trace(go.Bar(
            x=["ETI Recebido (período)"], y=[tot_eti],
            name=f"ETI — {perc_eti_real:.2f}% da base",
            marker_color=cor_eti,
            text=[f"{formar_real(tot_eti)}\n({perc_eti_real:.2f}%)"],
            textposition='inside', insidetextanchor='middle',
            hovertemplate=("<span style='color:white;'><b>Receita ETI</b><br>"
                           "Valor recebido: <b>" + formar_real(tot_eti) + "</b><br>"
                           "% sobre receita base: <b>" + f"{perc_eti_real:.2f}%" + "</b><br>"
                           "Meta: <b>" + f"{meta_eti_perc:.0f}%" +
                           " = " + formar_real(val_meta_eti) +
                           "</b></span><extra></extra>"),
        ))
        fig_eti.add_hline(
            y=val_meta_eti, line_dash="dot", line_color="#f39c12",
            annotation_text=f"Referência {meta_eti_perc:.0f}% = {formar_real(val_meta_eti)}",
            annotation_position="top left"
        )
        fig_eti.update_layout(
            separators=",.", barmode='group', hoverlabel=HOVER_STYLE,
            yaxis=dict(showticklabels=False), showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.20,
                        xanchor="center", x=0.5), height=400
        )
        st.plotly_chart(fig_eti, use_container_width=True, config=CONFIG_PT)
#-----------------RECURSOS PRÓPRIOS-----------------------------
    elif st.session_state.setor == 'Recursos Próprios':
        st.markdown("<h1 style='text-align: left;'>📖 São Tomás de Aquino - Recursos Próprios (25%)</h1>",
                    unsafe_allow_html=True)

        # ── FUNÇÃO AUXILIAR ───────────────────────────────────────────────────
        def obter_soma_rp(df, meses):
            """Soma robusta ignorando case nos nomes dos meses."""
            col_map = {c.strip().lower(): c for c in df.columns}
            cols = [col_map[m.lower()] for m in meses if m.lower() in col_map]
            return df[cols].sum().sum() if cols else 0.0

        # ── ABREVIAÇÕES DOS IMPOSTOS ──────────────────────────────────────────
        ABREV_IMPOSTO = {
            'PROPRIEDADE PREDIAL E TERRITORIAL URBANA': 'IPTU',
            'TRANSMISSÃO "INTER VIVOS"':                'ITBI',
            'TRANSMISSÃO INTER VIVOS':                  'ITBI',
            'RENDA - RETIDO NA FONTE':                  'IR',
            'RENDA – RETIDO NA FONTE':                  'IR',
            'SERVIÇOS DE QUALQUER NATUREZA':            'ISS',
            'FUNDO DE PARTICIPAÇÃO DOS MUNICÍPIOS':     'FPM',
            'FUNDO DE PARTICIPAÇÃO DO MUNICÍPIOS':      'FPM',
            'PROPRIEDADE TERRITORIAL RURAL':            'ITR',
            'ICMS':                                     'ICMS',
            'IPVA':                                     'IPVA',
            'IPI':                                      'IPI',
            'INSS':                                     'INSS',
        }

        def abrev_imposto(desc):
            desc_up = str(desc).upper()
            for longo, curto in ABREV_IMPOSTO.items():
                if longo in desc_up:
                    if 'DÍVIDA ATIVA' in desc_up and 'MULTAS' in desc_up: return f"{curto} – D.A. M/J"
                    if 'DÍVIDA ATIVA' in desc_up:                          return f"{curto} – D.A."
                    if 'MULTAS' in desc_up:                                return f"{curto} – M/J"
                    if 'OUTROS RENDIMENTOS' in desc_up:                    return f"{curto} – Outros"
                    if '1% DEZEMBRO' in desc_up or 'DEZEMBRO' in desc_up:  return f"{curto} – Dez"
                    if '1% JULHO' in desc_up or 'JULHO' in desc_up:        return f"{curto} – Jul/Set"
                    return curto
            return desc[:20]

        # ── PALETA ───────────────────────────────────────────────────────────
        PALETA_RP = [
            '#1a7a4a','#27ae60','#17a589','#1abc9c',
            '#2980b9','#1565c0','#0288d1','#00838f',
            '#00acc1','#26c6da','#43a047','#66bb6a',
            '#80cbc4','#4dd0e1',
        ]

        # ── BASES DE DADOS ────────────────────────────────────────────────────
        # São Tomás: 'Cota-Parte ' tem espaço no final — usar str.strip() no filtro
        df_r_base = df_r[
            df_r['Categoria'].str.strip().isin(['Impostos', 'Cota-Parte'])
        ].copy()
        df_r_base['Abrev'] = df_r_base['Descrição da Receita'].apply(abrev_imposto)

        # Dedução: duas variações ('Dedução ' com espaço e 'Dedução' sem espaço)
        df_r_ded = df_r[
            df_r['Categoria'].str.strip().str.startswith('Dedução', na=False)
        ].copy()

        # Previsão orçamentária — coluna 'Orçado Receitas' já limpa pelo load_all_data
        prev_impostos = df_r[
            df_r['Categoria'].str.strip() == 'Impostos'
        ]['Orçado Receitas'].sum()                          # R$ 4.283.300,00

        prev_total_rp = df_r_base['Orçado Receitas'].sum()

        # Arrecadado no período
        tot_rec_base  = obter_soma_rp(df_r_base, meses_disponiveis)   # R$ 6.952.692,00
        tot_deducoes  = abs(obter_soma_rp(df_r_ded, meses_disponiveis))  # R$ 1.292.208,11
        meta_25_valor = tot_rec_base * 0.25                            # R$ 1.738.173,00

        # Fase de despesa selecionável
        fase_despesa = st.segmented_control(
            " (Impacta Indicadores Superiores):",
            ["Empenhado", "Liquidado", "Pago"],
            default="Liquidado", key="fase_desp_rp"
        )
        df_df_15001 = df_df_raw[
            (df_df_raw['Fonte'] == '15001') & (df_df_raw['Tipo'] == fase_despesa)
        ].copy()

        total_desp_15001 = df_df_15001[meses_disponiveis].sum().sum()
        # Liquidado: R$ 405.327,20 | Empenhado: R$ 532.419,94 | Pago: R$ 337.982,18
        esforco_total    = total_desp_15001 + tot_deducoes
        perc_25          = (esforco_total / tot_rec_base * 100) if tot_rec_base > 0 else 0.0
        saldo_nec_25     = max(0.0, meta_25_valor - esforco_total)

        # Fontes 150xx além de 15001 (fonte 1500 — anos anteriores)
        df_15000_outras = df_df_raw[
            df_df_raw['Fonte'].str.match(r'^150\d*$', na=False) &
            (df_df_raw['Fonte'] != '15001') &
            (df_df_raw['Tipo'] == 'Liquidado')
        ].copy()
        val_outras_fontes = df_15000_outras[meses_disponiveis].sum().sum()
        # Fonte 1500 Liquidado: Jan 43.594,31 + Fev 81.673,37 = 125.267,68

        # ── CARDS SUPERIORES ──────────────────────────────────────────────────
        st.markdown("##### Previsões e Arrecadação")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Previsão Orçamentária — Impostos", formar_real(prev_impostos))
        with c2:
            st.metric(
                f"Receitas Arrecadadas ({meses_disponiveis[0]}–{meses_disponiveis[-1]})",
                formar_real(tot_rec_base)
            )
        with c3:
            st.metric(
                "Meta 25% (sobre o arrecadado)",
                formar_real(meta_25_valor),
                delta=f"Saldo: {formar_real(saldo_nec_25)}" if saldo_nec_25 > 0 else "✅ Meta atingida",
                delta_color="inverse" if saldo_nec_25 > 0 else "normal"
            )

        st.markdown("---")

        # ── RECEITAS POR IMPOSTO ──────────────────────────────────────────────
        st.subheader("🔹 Receitas Recursos Próprios (Impostos e Cota-Parte)")

        abrevs_unicas = list(df_r_base['Abrev'].unique())
        mapa_cores_rp = {a: PALETA_RP[i % len(PALETA_RP)] for i, a in enumerate(abrevs_unicas)}

        view_rp = st.segmented_control(
            "Visualização Receitas:", ["Mensal", "Acumulado"], default="Mensal", key="view_rp"
        )

        lista_completa = ["📊 Acumulado Geral"] + df_r_base['Descrição da Receita'].unique().tolist()
        if 'idx_nav_rp' not in st.session_state: st.session_state.idx_nav_rp = 0

        grid = st.columns([0.5, 1.2, 1.2, 1.2, 1.2, 1.2, 0.5])
        with grid[0]:
            if st.button("◀", key="rp_left"):
                st.session_state.idx_nav_rp = max(0, st.session_state.idx_nav_rp - 5)
                st.rerun()

        fim_idx = min(st.session_state.idx_nav_rp + 5, len(lista_completa))
        fatia   = lista_completa[st.session_state.idx_nav_rp:fim_idx]

        for i, item in enumerate(fatia):
            with grid[i + 1]:
                label = abrev_imposto(item) if "📊" not in item else "GERAL"
                if st.button(label, key=f"rp_btn_{item}", help=item, use_container_width=True):
                    st.session_state['ativo_rp'] = item.replace("📊 ", "")
                    st.rerun()

        with grid[6]:
            if st.button("▶", key="rp_right"):
                if st.session_state.idx_nav_rp + 5 < len(lista_completa):
                    st.session_state.idx_nav_rp += 5
                    st.rerun()

        ativo  = st.session_state.get('ativo_rp', "Acumulado Geral")
        st.markdown(f"#### 📈 {abrev_imposto(ativo) if ativo != 'Acumulado Geral' else 'Acumulado Geral'}")

        df_aux = (
            df_r_base.copy()
            if ativo == "Acumulado Geral"
            else df_r_base[df_r_base['Descrição da Receita'] == ativo].copy()
        )

        if view_rp == "Acumulado":
            if ativo == "Acumulado Geral":
                dados_acum = []
                for abr in df_aux['Abrev'].unique():
                    val = obter_soma_rp(df_aux[df_aux['Abrev'] == abr], meses_disponiveis)
                    dados_acum.append({"Imposto": abr, "Valor": val})
                df_acum = pd.DataFrame(dados_acum).sort_values("Valor", ascending=False)
                fig_rp = px.bar(df_acum, x="Imposto", y="Valor", color="Imposto",
                                color_discrete_map=mapa_cores_rp, text_auto='.3s')
            else:
                val = obter_soma_rp(df_aux, meses_disponiveis)
                fig_rp = px.bar(
                    x=[abrev_imposto(ativo)], y=[val], text_auto='.3s',
                    color_discrete_sequence=[mapa_cores_rp.get(
                        df_aux['Abrev'].iloc[0] if len(df_aux) > 0 else '', '#003366'
                    )]
                )
        else:  # Mensal
            if ativo == "Acumulado Geral":
                dados_m = []
                for m in meses_disponiveis:
                    col_map = {c.strip().lower(): c for c in df_aux.columns}
                    col = col_map.get(m.lower())
                    for abr in df_aux['Abrev'].unique():
                        val = df_aux[df_aux['Abrev'] == abr][col].sum() if col else 0
                        dados_m.append({"Mês": m, "Imposto": abr, "Valor": val})
                fig_rp = px.bar(
                    pd.DataFrame(dados_m), x='Mês', y='Valor', color='Imposto',
                    barmode='stack', text_auto='.2s',
                    color_discrete_map=mapa_cores_rp,
                    category_orders={"Mês": ORDEM_MESES}
                )
            else:
                col_map = {c.strip().lower(): c for c in df_aux.columns}
                dados_m = [
                    {"Mês": m, "Valor": df_aux[col_map[m.lower()]].sum()
                     if m.lower() in col_map else 0}
                    for m in meses_disponiveis
                ]
                fig_rp = px.bar(
                    pd.DataFrame(dados_m), x='Mês', y='Valor', text_auto='.2s',
                    color_discrete_sequence=[mapa_cores_rp.get(
                        df_aux['Abrev'].iloc[0] if len(df_aux) > 0 else '', '#003366'
                    )],
                    category_orders={"Mês": ORDEM_MESES}
                )

        fig_rp.update_traces(
            hovertemplate=(
                "<span style='color:white;'><b>%{x}</b><br>"
                "Setor: Recursos Próprios<br>"
                "Valor: R$ %{y:,.2f}</span><extra></extra>"
            ),
            hoverlabel=HOVER_STYLE
        )
        fig_rp.update_layout(separators=",.", yaxis=dict(showticklabels=False))
        st.plotly_chart(fig_rp, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

        # ── DESPESAS FONTE 15001 ──────────────────────────────────────────────
        st.subheader("🔹 Despesas Fonte 15001")
        st.markdown("Detalhamento por Estágio (Empenhado, Liquidado, Pago)")
        view_desp = st.segmented_control(
            "Visualização Despesas:", ["Mensal", "Acumulado"], default="Mensal", key="view_desp"
        )

        df_15001_todas = df_df_raw[
            (df_df_raw['Fonte'] == '15001') &
            (df_df_raw['Tipo'].isin(['Empenhado', 'Liquidado', 'Pago']))
        ].copy()

        if view_desp == "Acumulado":
            total_desp_acum_rp = df_15001_todas[meses_disponiveis].sum().sum()
            df_desp_plot = []
            for fase in ["Empenhado", "Liquidado", "Pago"]:
                val  = df_15001_todas[df_15001_todas['Tipo'] == fase][meses_disponiveis].sum().sum()
                prop = (val / total_desp_acum_rp * 100) if total_desp_acum_rp > 0 else 0
                df_desp_plot.append({
                    "Fase": fase, "Valor": val,
                    "Proporção": f"{prop:.2f}%",
                    "Dedução": tot_deducoes, "Despesa": val
                })
            df_desp_plot = pd.DataFrame(df_desp_plot)
            df_desp_plot['Fase'] = pd.Categorical(
                df_desp_plot['Fase'], ["Empenhado", "Liquidado", "Pago"]
            )
            fig_d = px.bar(
                df_desp_plot, x='Fase', y='Valor', color='Fase', text_auto='.3s',
                custom_data=['Proporção', 'Dedução', 'Despesa'],
                color_discrete_map={
                    'Empenhado': "#fa3d3d", 'Liquidado': "#860000", 'Pago': "#470000"
                }
            )
        else:  # Mensal
            dados_d_m = []
            for m in meses_disponiveis:
                col_d   = m if m in df_15001_todas.columns else None
                col_ded = m if m in df_r_ded.columns else None
                total_mes_rp = df_15001_todas[col_d].sum() if col_d else 0
                deducao_mes  = abs(df_r_ded[col_ded].sum()) if col_ded else 0
                for fase in ['Empenhado', 'Liquidado', 'Pago']:
                    val  = df_15001_todas[df_15001_todas['Tipo'] == fase][col_d].sum() if col_d else 0
                    prop = (val / total_mes_rp * 100) if total_mes_rp > 0 else 0
                    dados_d_m.append({
                        "Mês": m, "Fase": fase, "Valor": val,
                        "Proporção": f"{prop:.2f}%",
                        "Dedução": deducao_mes, "Despesa": val
                    })
            df_dados_d_m = pd.DataFrame(dados_d_m)
            df_dados_d_m['Fase'] = pd.Categorical(
                df_dados_d_m['Fase'], ["Empenhado", "Liquidado", "Pago"]
            )
            fig_d = px.bar(
                df_dados_d_m, x='Mês', y='Valor', color='Fase', barmode='group',
                text_auto='.2s', custom_data=['Proporção', 'Dedução', 'Despesa'],
                color_discrete_map={
                    'Empenhado': '#fa3d3d', 'Liquidado': '#860000', 'Pago': '#470000'
                },
                category_orders={"Mês": ORDEM_MESES, "Fase": ["Empenhado", "Liquidado", "Pago"]}
            )

        fig_d.update_traces(
            hovertemplate=(
                "<span style='color:white;'><b>%{x}</b><br>"
                "Estágio: %{fullData.name}<br>"
                "Valor (15001): R$ %{customdata[2]:,.2f}<br>"
                "Dedução FUNDEB: R$ %{customdata[1]:,.2f}<br>"
                "Proporção: %{customdata[0]}</span><extra></extra>"
            ),
            hoverlabel=HOVER_STYLE
        )
        fig_d.update_layout(separators=",.", yaxis=dict(showticklabels=False))
        st.plotly_chart(fig_d, use_container_width=True, config=CONFIG_PT)

        if val_outras_fontes > 0:
            st.info(
                f"ℹ️ **Outras despesas de anos anteriores (Fonte 1500 — Liquidado):** "
                f"{formar_real(val_outras_fontes)} — não compõem o índice do ano vigente."
            )

        st.markdown("---")

        # ── ANÁLISE COMPARATIVA E META ────────────────────────────────────────
        st.subheader("🔹 Análise Comparativa e Meta (Mínimo 25%)")
        view_meta = st.segmented_control(
            "Visualização Meta:", ["Mensal", "Acumulado"], default="Mensal", key="view_meta"
        )

        cor_aplicacao = "#27ae60" if perc_25 >= 25 else "#e74c3c"

        if view_meta == "Acumulado":
            # Índice 25% só no acumulado
            idx1, idx2, idx3 = st.columns(3)
            with idx1: st.metric("Receitas Base (Impostos + Cota-Parte)",
                                  formar_real(tot_rec_base))
            with idx2: st.metric(f"Esforço Total ({fase_despesa} 15001 + Deduções)",
                                  formar_real(esforco_total))
            with idx3: metric_contabil("Índice de Aplicação (Mín. 25%)", perc_25, 25.0)

            prop_desp = (total_desp_15001 / esforco_total * 100) if esforco_total > 0 else 0
            prop_ded  = (tot_deducoes / esforco_total * 100) if esforco_total > 0 else 0

            fig_meta = go.Figure()

            fig_meta.add_trace(go.Bar(
                x=["Receitas Base"], y=[tot_rec_base],
                name="Receitas Base", marker_color="#003366",
                text=[formar_real(tot_rec_base)],
                textposition='inside', insidetextanchor='middle',
                hovertemplate=(
                    "<span style='color:white;'><b>Receitas Base</b><br>"
                    "Impostos + Cota-Parte<br>"
                    "Valor: <b>" + formar_real(tot_rec_base) + "</b></span><extra></extra>"
                ),
            ))
            fig_meta.add_trace(go.Bar(
                x=["Aplicação Total"], y=[total_desp_15001],
                name=f"Despesa 15001 ({fase_despesa})", marker_color="#860000",
                text=[f"{formar_real(total_desp_15001)}\n({prop_desp:.1f}%)"],
                textposition='inside', insidetextanchor='middle',
                customdata=[[formar_real(total_desp_15001), f"{prop_desp:.1f}%", fase_despesa]],
                hovertemplate=(
                    "<span style='color:white;'><b>Despesa Fonte 15001</b><br>"
                    "Estágio: %{customdata[2]}<br>"
                    "Valor: <b>%{customdata[0]}</b><br>"
                    "% do esforço total: %{customdata[1]}</span><extra></extra>"
                ),
            ))
            fig_meta.add_trace(go.Bar(
                x=["Aplicação Total"], y=[tot_deducoes],
                name="Dedução FUNDEB", marker_color="#f39c12",
                text=[f"{formar_real(tot_deducoes)}\n({prop_ded:.1f}%)"],
                textposition='inside', insidetextanchor='middle',
                customdata=[[formar_real(tot_deducoes), f"{prop_ded:.1f}%"]],
                hovertemplate=(
                    "<span style='color:white;'><b>Dedução FUNDEB</b><br>"
                    "Valor: <b>%{customdata[0]}</b><br>"
                    "% do esforço total: %{customdata[1]}</span><extra></extra>"
                ),
            ))
            fig_meta.add_hline(
                y=tot_rec_base * 0.25, line_dash="dash", line_color="#f39c12",
                annotation_text=f"Meta 25% = {formar_real(tot_rec_base * 0.25)}",
                annotation_position="top left"
            )
            if val_outras_fontes > 0:
                fig_meta.add_annotation(
                    x="Aplicação Total", y=esforco_total * 1.05,
                    text=f"⚠️ Outras fontes (anos ant.): {formar_real(val_outras_fontes)}",
                    showarrow=False, font=dict(color="#aaaaaa", size=11)
                )
            fig_meta.update_layout(
                separators=",.", barmode='stack', hoverlabel=HOVER_STYLE,
                yaxis=dict(showticklabels=False), showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.20,
                            xanchor="center", x=0.5), height=450,
            )
            st.plotly_chart(fig_meta, use_container_width=True, config=CONFIG_PT)

        else:  # MENSAL
            dados_meta_m = []
            for m in meses_disponiveis:
                col_b = m if m in df_r_base.columns else None
                col_d = m if m in df_df_15001.columns else None
                col_e = m if m in df_r_ded.columns else None

                r_m   = df_r_base[col_b].sum() if col_b else 0
                d_m   = df_df_15001[col_d].sum() if col_d else 0
                ded_m = abs(df_r_ded[col_e].sum()) if col_e else 0
                perc_m = ((d_m + ded_m) / r_m * 100) if r_m > 0 else 0

                dados_meta_m.append({
                    "Mês": m, "Tipo": "Receitas Base",
                    "Valor": r_m, "Dedução": 0, "Desp": 0, "Texto": ""
                })
                dados_meta_m.append({
                    "Mês": m, "Tipo": f"Desp. 15001 ({fase_despesa})",
                    "Valor": d_m, "Dedução": ded_m, "Desp": d_m,
                    "Texto": f"{(d_m/(d_m+ded_m)*100):.1f}% desp." if (d_m + ded_m) > 0 else ""
                })
                dados_meta_m.append({
                    "Mês": m, "Tipo": "Dedução FUNDEB",
                    "Valor": ded_m, "Dedução": ded_m, "Desp": d_m,
                    "Texto": f"{(ded_m/(d_m+ded_m)*100):.1f}% ded." if (d_m + ded_m) > 0 else ""
                })

            df_meta_m = pd.DataFrame(dados_meta_m)
            fig_meta = px.bar(
                df_meta_m, x='Mês', y='Valor', color='Tipo', barmode='group',
                text='Texto', custom_data=['Dedução', 'Desp'],
                color_discrete_map={
                    "Receitas Base":                  "#003366",
                    f"Desp. 15001 ({fase_despesa})":  "#860000",
                    "Dedução FUNDEB":                  "#f39c12",
                },
                category_orders={"Mês": ORDEM_MESES}
            )
            fig_meta.update_traces(
                hovertemplate=(
                    "<span style='color:white;'><b>%{x} — %{data.name}</b><br>"
                    "Valor: R$ %{y:,.2f}<br>"
                    "Dedução mês: R$ %{customdata[0]:,.2f}<br>"
                    "Desp. 15001 mês: R$ %{customdata[1]:,.2f}"
                    "</span><extra></extra>"
                ),
                hoverlabel=HOVER_STYLE
            )
            df_linha = df_meta_m[df_meta_m['Tipo'] == 'Receitas Base'].copy()
            df_linha['Meta 25%'] = df_linha['Valor'] * 0.25
            fig_meta.add_trace(go.Scatter(
                x=df_linha['Mês'], y=df_linha['Meta 25%'],
                mode='lines+markers', name='Meta 25% (Mensal)',
                line=dict(color='#f39c12', dash='dash')
            ))
            fig_meta.update_layout(
                separators=",.", yaxis=dict(showticklabels=False), showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25,
                            xanchor="center", x=0.5),
            )
            st.plotly_chart(fig_meta, use_container_width=True, config=CONFIG_PT)


    elif st.session_state.setor == 'Recursos Vinculados':
        st.markdown("<h1 style='text-align: left;'>📖 São Tomás de Aquino - Recursos Vinculados</h1>",
                    unsafe_allow_html=True)

        # ── CONFIGURAÇÃO DE PROGRAMAS E FONTES ───────────────────────────────
        # Fontes confirmadas nas fichas de São Tomás de Aquino:
        #   PNAE  (merenda escolar)          → 1552
        #   PNATE (transporte escolar)       → 1553  (PNATE federal)
        #   PTE   (transporte escolar est.)  → 1576  (segundo programa de transporte)
        #   QESE  (qualidade educação)       → 1550
        # Não há pares 2xxx com valores nos programas padrão.
        mapa_desp = {
            'PNAE':  ['1552'],
            'PNATE': ['1553'],
            'PTE':   ['1576'],
            'QESE':  ['1550'],
        }
        programas = ['PNAE', 'PNATE', 'PTE', 'QESE']

        # Paleta verde/teal/azul — uma cor por programa
        COR_PROG = {
            'PNAE':  '#1a7a4a',   # verde escuro
            'PNATE': '#17a589',   # teal
            'PTE':   '#2980b9',   # azul médio
            'QESE':  '#1565c0',   # azul escuro
        }
        COR_DESP = '#860000'      # vermelho escuro para despesas

        # ── FUNÇÃO AUXILIAR ROBUSTA ───────────────────────────────────────────
        def soma_vinc(df, meses):
            """Soma colunas de meses ignorando case."""
            col_map = {c.strip().lower(): c for c in df.columns}
            cols = [col_map[m.lower()] for m in meses if m.lower() in col_map]
            return df[cols].sum().sum() if cols else 0.0

        # ── BASE DE DADOS RECEITAS ────────────────────────────────────────────
        # Em São Tomás, os programas aparecem na coluna 'Descrição da Receita'
        # com a sigla em maiúsculas (PNAE, PNATE, PTE, QESE).
        # A coluna 'Orçado Receitas' já está limpa pelo load_all_data (header=0).
        # Os meses 'Janeiro' e 'Fevereiro' chegam em maiúsculas.
        df_r_vinc = df_r[
            df_r['Descrição da Receita'].str.upper().str.strip().isin(programas)
        ].copy()

        # ── BOTÃO — MENSAL PRIMEIRO ───────────────────────────────────────────
        tipo_vinc = st.segmented_control(
            "Visualização:", ["Mensal", "Acumulado"], default="Mensal", key="vinc_btn"
        )

        st.markdown("---")

        # ── DETALHAMENTO POR PROGRAMA ─────────────────────────────────────────
        for prog in programas:

            df_prog_r = df_r_vinc[
                df_r_vinc['Descrição da Receita'].str.upper().str.strip() == prog
            ].copy()

            # Previsão orçamentária (Orçado Receitas — coluna já numérica)
            prev_prog    = df_prog_r['Orçado Receitas'].sum()

            # Repasse arrecadado no período (Jan + Fev)
            rep_periodo  = soma_vinc(df_prog_r, meses_disponiveis)

            # Previsão de repasse = mesmo valor do orçado (referência)
            prev_repasse = prev_prog

            # Liquidado no período — fontes do mapa_desp (apenas ano vigente)
            desp_liq = df_df_raw[
                df_df_raw['Fonte'].isin(mapa_desp[prog]) &
                (df_df_raw['Tipo'] == 'Liquidado')
            ][meses_disponiveis].sum().sum()

            # ── CARDS DE DESTAQUE POR PROGRAMA ───────────────────────────────
            st.markdown(
                f"<h4 style='color:{COR_PROG[prog]}; margin-bottom:4px;'>📊 Programa: {prog}</h4>",
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(
                    f"Repasse {meses_disponiveis[0]}–{meses_disponiveis[-1]} (Arrecadado)",
                    formar_real(rep_periodo),
                )
            with c2:
                st.metric(
                    "Previsão de Repasse (Orçado Receitas)",
                    formar_real(prev_repasse),
                )
            with c3:
                st.metric(
                    "Orçamento 2026 (Município)",
                    formar_real(prev_prog),
                )

            # ── GRÁFICO ───────────────────────────────────────────────────────
            if tipo_vinc == "Mensal":
                dados_m = []
                for m in meses_disponiveis:
                    # Meses em maiúsculas em São Tomás — acesso direto
                    col_r  = m if m in df_prog_r.columns else None
                    col_df = m if m in df_df_raw.columns else None

                    rec_m  = df_prog_r[col_r].sum() if col_r else 0.0
                    desp_m = df_df_raw[
                        df_df_raw['Fonte'].isin(mapa_desp[prog]) &
                        (df_df_raw['Tipo'] == 'Liquidado')
                    ][col_df].sum() if col_df else 0.0

                    dados_m.append({"Mês": m, "Tipo": "Receita",             "Valor": rec_m})
                    dados_m.append({"Mês": m, "Tipo": "Despesa (Liquidado)", "Valor": desp_m})

                fig_vinc = px.bar(
                    pd.DataFrame(dados_m), x='Mês', y='Valor', color='Tipo',
                    barmode='group', text_auto='.2s',
                    color_discrete_map={
                        'Receita':             COR_PROG[prog],
                        'Despesa (Liquidado)': COR_DESP,
                    },
                    category_orders={"Mês": ORDEM_MESES},
                )

            else:  # ACUMULADO
                dados_acum = [
                    {"Tipo": "Receita",             "Valor": rep_periodo},
                    {"Tipo": "Despesa (Liquidado)", "Valor": desp_liq},
                ]
                fig_vinc = px.bar(
                    pd.DataFrame(dados_acum),
                    x='Tipo', y='Valor', color='Tipo', barmode='group',
                    text_auto='.2s',
                    color_discrete_map={
                        'Receita':             COR_PROG[prog],
                        'Despesa (Liquidado)': COR_DESP,
                    },
                )

            fig_vinc.update_traces(
                selector=dict(type='bar'),
                textposition='outside',
                hovertemplate=(
                    "<span style='color:white;'>"
                    "<b>%{x}</b><br>"
                    "Programa: " + prog + "<br>"
                    "Tipo: %{data.name}<br>"
                    "Valor: <b>R$ %{y:,.2f}</b>"
                    "</span><extra></extra>"
                ),
                hoverlabel=HOVER_STYLE,
            )
            fig_vinc.update_layout(
                separators=",.",
                yaxis=dict(showticklabels=False, title=None),
                xaxis_title=None,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.30,
                            xanchor="center", x=0.5),
                height=380,
            )
            st.plotly_chart(fig_vinc, use_container_width=True, config=CONFIG_PT)
            st.markdown("---")


    # ── Relatório Geral de Fichas ─────────────────────────────────────────────
    st.markdown("### 📋 Relatório Geral de Fichas")
    df_f_filt = df_f_raw[df_f_raw['Atividade'].str.contains(search_term, na=False, case=False)].copy()
    st.dataframe(df_f_filt, use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar os arquivos CSV. Verifique a pasta 'zEducação'.")