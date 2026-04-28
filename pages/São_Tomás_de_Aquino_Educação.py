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

        # ── Receitas ─────────────────────────────────────────────────────────
        # Após load_all_data com header=0 e limpeza de Repasse + Orçado Receitas,
        # os valores chegam corretamente como float.
        df_r_fundeb = df_r[df_r['Categoria'].str.strip() == 'FUNDEB'].copy()
        df_r_fundeb['Descrição da Receita'] = df_r_fundeb['Descrição da Receita'].str.strip()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)

        # Valores esperados na base (Jan+Fev):
        #   Principal:   537.352,71 + 627.996,62 = 1.165.349,33
        #   Rendimentos:   1.900,89 +   2.941,79 =     4.842,68
        #   VAAR/ETI/VAAT: 0
        tot_prev_municipio = df_r_fundeb[
            df_r_fundeb['Subcategoria'] == 'Principal'
        ]['Orçado Receitas'].sum()                         # R$ 6.650.000,00

        tot_prev_portaria = df_r_fundeb['Repasse'].sum()   # R$ 6.351.300,40

        tot_rec_periodo = soma(df_r_fundeb, meses_disponiveis)  # R$ 1.170.192,01

        tot_eti = soma(
            df_r_fundeb[df_r_fundeb['Subcategoria'] == 'ETI'], meses_disponiveis
        )                                                   # R$ 0,00

        # ── Despesas — apenas fontes do ano vigente (15407 / 15403) ──────────
        # Valores Liquidado:
        #   15407 Jan=454.993,58 Fev=555.073,78 → total 1.010.067,36
        #   15403 Jan= 18.576,50 Fev= 21.822,94 → total    40.399,44
        df_df_fundeb = df_df_raw[
            df_df_raw['Fonte'].isin(['15407', '15403'])
        ].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb['Fonte'].apply(
            lambda x: 'FUNDEB 70%' if x == '15407' else 'FUNDEB 30%'
        )

        base_indice_70 = soma(
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

        tot_desp_vigente = desp_70_vigente + desp_30_vigente  # R$ 1.050.466,80

        perc_70_indice = (desp_70_vigente / base_indice_70 * 100) if base_indice_70 > 0 else 0.0
        # 86,32%

        # ── Cards de previsão ─────────────────────────────────────────────────
        st.markdown("##### Previsões Orçamentárias")
        p1, p2, p3 = st.columns(3)
        with p1: st.metric("Previsão Receitas (Orçamento Município)",
                            formar_real(tot_prev_municipio))
        with p2: st.metric("Previsão de Receitas (Port. Intermin. nº 14/dez 2025)",
                            formar_real(tot_prev_portaria))
        with p3: st.metric("Atualização Quadrimestral", "—")

        st.markdown("---")

        # ── Gráfico 1: Receitas + Despesas ───────────────────────────────────
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

        COR_REC  = {'Principal':'#1a7a4a','VAAR/VAAT':'#2ecc71','ETI':'#17a589','Rendimentos':'#1abc9c'}
        COR_DESP = {'FUNDEB 70% – Vigente':'#660000','FUNDEB 30% – Vigente':'#cc0000'}

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
                    show_leg    = f"rec_{cat}" not in legendas_usadas
                    legendas_usadas.add(f"rec_{cat}")
                    part = f"{(val/tot_rec_m*100):.1f}%" if tot_rec_m > 0 else "—"
                    fig_rd.add_trace(go.Bar(
                        name=cat, x=[[m], ["Receitas"]], y=[val],
                        marker_color=COR_REC.get(cat,'#27ae60'),
                        legendgroup=f"rec_{cat}", showlegend=show_leg,
                        text=formar_real(val) if val > 0 else "",
                        textposition='inside', insidetextanchor='middle',
                        customdata=[[cat,"FUNDEB"," | ".join(desc_list),
                                     formar_real(val),formar_real(tot_rec_m),part,m]],
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

                for fonte_cod, label_desp in [('15407','FUNDEB 70% – Vigente'),
                                              ('15403','FUNDEB 30% – Vigente')]:
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
                        customdata=[[fonte_cod,"Liquidado – Ano Vigente",prop,
                                     formar_real(val),formar_real(tot_desp_m),prop,m]],
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
                    marker_color=COR_REC.get(cat,'#27ae60'),
                    legendgroup=f"rec_{cat}", showlegend=True,
                    text=formar_real(val) if val > 0 else "",
                    textposition='inside', insidetextanchor='middle',
                    customdata=[[cat,"FUNDEB"," | ".join(desc_list),
                                 formar_real(val),formar_real(tot_rec_periodo),part]],
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

            for fonte_cod, label_desp in [('15407','FUNDEB 70% – Vigente'),
                                          ('15403','FUNDEB 30% – Vigente')]:
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
                    customdata=[[fonte_cod,"Liquidado – Ano Vigente",prop,
                                 formar_real(val),formar_real(tot_desp_vigente),prop]],
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

        # ── Gráfico 2: Índice 70% ─────────────────────────────────────────────
        st.subheader("🔹 2. Índice de Aplicação em Pessoal (Mín. 70%)")
        st.info("**Base:** Principal + Rendimentos arrecadados. "
                "**Numerador:** Liquidado fonte 15407.")

        i1, i2, i3 = st.columns(3)
        with i1: st.metric("Base de Cálculo (Principal + Rendimentos)",
                            formar_real(base_indice_70))
        with i2: st.metric("Despesas FUNDEB 70% – Liquidado",
                            formar_real(desp_70_vigente))
        with i3: metric_contabil("Aplicação em Pessoal (Mín. 70%)", perc_70_indice, 70.0)

        cor_barra = "#27ae60" if perc_70_indice >= 70 else "#e74c3c"
        fig_70 = go.Figure()
        fig_70.add_trace(go.Bar(
            x=["Receita Base\n(Principal + Rendimentos)"], y=[base_indice_70],
            name="Receita Base", marker_color="#003366",
            text=[formar_real(base_indice_70)], textposition='inside', insidetextanchor='middle',
            hovertemplate=("<span style='color:white;'><b>Receita Base FUNDEB</b><br>"
                           "Valor: <b>" + formar_real(base_indice_70) + "</b></span><extra></extra>"),
        ))
        fig_70.add_trace(go.Bar(
            x=["Despesas 70%\n(Liquidado)"], y=[desp_70_vigente],
            name=f"Despesas 70% — {perc_70_indice:.2f}%", marker_color=cor_barra,
            text=[f"{formar_real(desp_70_vigente)}\n({perc_70_indice:.2f}%)"],
            textposition='inside', insidetextanchor='middle',
            hovertemplate=("<span style='color:white;'><b>Despesas FUNDEB 70%</b><br>"
                           "Fonte: 15407 | Liquidado<br>"
                           "Valor: <b>" + formar_real(desp_70_vigente) + "</b><br>"
                           "Índice: <b>" + f"{perc_70_indice:.2f}%" + "</b></span><extra></extra>"),
        ))
        fig_70.add_hline(y=base_indice_70*0.70, line_dash="dot", line_color="green",
                         annotation_text=f"Meta 70% = {formar_real(base_indice_70*0.70)}",
                         annotation_position="top left")
        fig_70.update_layout(separators=",.", barmode='group', hoverlabel=HOVER_STYLE,
                             yaxis=dict(showticklabels=False), showlegend=True,
                             legend=dict(orientation="h", yanchor="bottom", y=-0.20,
                                         xanchor="center", x=0.5), height=420)
        st.plotly_chart(fig_70, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

        # ── Gráfico 3: ETI ────────────────────────────────────────────────────
        st.subheader("🔹 3. Percentual Tempo Integral (ETI)")

        meta_eti_perc = 4.0
        val_meta_eti  = base_indice_70 * (meta_eti_perc / 100)
        perc_eti_real = (tot_eti / base_indice_70 * 100) if base_indice_70 > 0 else 0.0

        e1, e2, e3 = st.columns(3)
        with e1: st.metric("Receita ETI Recebida (período)", formar_real(tot_eti))
        with e2: st.metric(f"Valor Equivalente a {meta_eti_perc:.0f}% da Receita Base",
                            formar_real(val_meta_eti))
        with e3: metric_contabil(f"ETI sobre Receita Base (Ref. {meta_eti_perc:.0f}%)",
                                  perc_eti_real, meta_eti_perc)

        cor_eti = "#27ae60" if perc_eti_real >= meta_eti_perc else "#e74c3c"
        fig_eti = go.Figure()
        fig_eti.add_trace(go.Bar(
            x=["Receita Base FUNDEB"], y=[base_indice_70], name="Receita Base",
            marker_color="#003366", text=[formar_real(base_indice_70)],
            textposition='inside', insidetextanchor='middle',
            hovertemplate=("<span style='color:white;'><b>Receita Base FUNDEB</b><br>"
                           "Valor: <b>" + formar_real(base_indice_70) + "</b></span><extra></extra>"),
        ))
        fig_eti.add_trace(go.Bar(
            x=["ETI Recebido (período)"], y=[tot_eti],
            name=f"ETI — {perc_eti_real:.2f}% da base", marker_color=cor_eti,
            text=[f"{formar_real(tot_eti)}\n({perc_eti_real:.2f}%)"],
            textposition='inside', insidetextanchor='middle',
            hovertemplate=("<span style='color:white;'><b>Receita ETI</b><br>"
                           "Valor recebido: <b>" + formar_real(tot_eti) + "</b><br>"
                           "% sobre receita base: <b>" + f"{perc_eti_real:.2f}%" + "</b><br>"
                           "Meta: <b>" + f"{meta_eti_perc:.0f}% = " + formar_real(val_meta_eti) +
                           "</b></span><extra></extra>"),
        ))
        fig_eti.add_hline(y=val_meta_eti, line_dash="dot", line_color="#f39c12",
                          annotation_text=f"Referência {meta_eti_perc:.0f}% = {formar_real(val_meta_eti)}",
                          annotation_position="top left")
        fig_eti.update_layout(separators=",.", barmode='group', hoverlabel=HOVER_STYLE,
                              yaxis=dict(showticklabels=False), showlegend=True,
                              legend=dict(orientation="h", yanchor="bottom", y=-0.20,
                                          xanchor="center", x=0.5), height=400)
        st.plotly_chart(fig_eti, use_container_width=True, config=CONFIG_PT)

    # ── Relatório Geral de Fichas ─────────────────────────────────────────────
    st.markdown("### 📋 Relatório Geral de Fichas")
    df_f_filt = df_f_raw[df_f_raw['Atividade'].str.contains(search_term, na=False, case=False)].copy()
    st.dataframe(df_f_filt, use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar os arquivos CSV. Verifique a pasta 'zEducação'.")