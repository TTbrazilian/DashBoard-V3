import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import plotly.graph_objects as go

# ── CONFIGURAÇÃO DA PÁGINA ────────────────────────────────────────────────────
st.set_page_config(page_title="São Tomás de Aquino - Gestão Educação", layout="wide")

st.markdown("""
    <style>
        @keyframes subirBarra {
            from { clip-path: inset(100% 0 0 0); }
            to   { clip-path: inset(0%   0 0 0); }
        }
        .js-plotly-plot .point path {
            animation: subirBarra 1.5s cubic-bezier(0.25,1,0.5,1) forwards;
            animation-delay: 0.3s;
            clip-path: inset(100% 0 0 0);
        }
        @keyframes slideIn {
            from { opacity:0; transform:translateX(20px); }
            to   { opacity:1; transform:translateX(0);    }
        }
        .stButton button {
            width:100%!important; height:45px!important;
            padding:0!important; font-size:10px!important;
            font-weight:700!important; border-radius:4px!important;
            white-space:nowrap!important;
            display:flex!important; align-items:center!important;
            justify-content:center!important;
            animation: slideIn 0.4s ease-out;
        }
        .stButton button:focus { outline:none!important; box-shadow:none!important; }
        [data-testid="column"]  { display:flex; align-items:center; justify-content:center; }

        /* ── FILTRO DE BARRA LATERAL ─────────────────────────────────────────
           Página de EDUCAÇÃO: oculta todos os municípios do setor Saúde.
           O seletor detecta qualquer item da nav que contenha o texto "Saúde".
        ────────────────────────────────────────────────────────────────────── */
        [data-testid="stSidebarNav"] ul li:has(span:contains("Saúde")) {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

pio.templates.default = "plotly_dark"
CONFIG_PT   = {'displaylogo': False, 'showTips': False}
HOVER_STYLE = dict(bgcolor="rgba(0,0,0,0.9)", font_size=13,
                   font_family="Arial", font_color="white")
ORDEM_MESES = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
               'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']

if 'setor' not in st.session_state:
    st.session_state.setor = 'FUNDEB'

# ── PALETA DE CORES GLOBAL ────────────────────────────────────────────────────
# Receitas FUNDEB — verde/azul com alto contraste entre categorias
COR_REC = {
    'Principal':   '#1a7a4a',   # verde floresta escuro
    'Rendimentos': '#0d47a1',   # azul marinho escuro
    'VAAR/VAAT':   '#69f0ae',   # verde neon claro  (bem diferente do escuro)
    'ETI':         '#40c4ff',   # azul céu brilhante (bem diferente do marinho)
}
# Despesas FUNDEB — vermelho, 70% muito escuro / 30% muito claro (bem distintos)
COR_DESP = {
    'FUNDEB 70% – Vigente': '#4a0000',   # vermelho quase preto
    'FUNDEB 30% – Vigente': '#ff1744',   # vermelho vivo/saturado
}

# ── FUNÇÕES UTILITÁRIAS ───────────────────────────────────────────────────────
def limpar_valor(valor):
    if pd.isna(valor) or str(valor).strip() in ["","−","-","R$ 0,00","0"]:
        return 0.0
    s = str(valor).replace('R$','').replace(' ','').replace('.','').replace(',','.')
    try:
        if '(' in s and ')' in s: s = '-' + s.replace('(','').replace(')','')
        return float(s)
    except: return 0.0

def formar_real(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def metric_contabil(label, valor_atual, meta):
    """Card de índice com ícone ✅/⚠️ e delta colorido."""
    delta      = valor_atual - meta
    status_icon = "✅" if valor_atual >= meta else "⚠️"
    return st.metric(label=label,
                     value=f"{status_icon} {valor_atual:.2f}%",
                     delta=f"{delta:.2f}%",
                     delta_color="normal")

def abreviar_extremo(nome):
    if "📊" in nome: return "GERAL"
    n = nome.upper()
    for longo, curto in {
        "IMPOSTO SOBRE A PROPRIEDADE PREDIAL E TERRITORIAL URBANA":"IPTU",
        "IMPOSTO SOBRE TRANSMISSÃO DE BENS IMÓVEIS":"ITBI",
        "IMPOSTO SOBRE SERVIÇOS DE QUALQUER NATUREZA":"ISS",
        "IMPOSTO SOBRE A RENDA":"IR","IMPOSTO TERRITORIAL RURAL":"ITR",
        "DÍVIDA ATIVA":"D.A.","COTA-PARTE":"COTA",
        "CONTRIBUIÇÃO PARA O CUSTEIO DO SERVIÇO DE ILUMINAÇÃO PÚBLICA":"COSIP"
    }.items(): n = n.replace(longo, curto)
    n = n.replace("PRINCIPAL","PRIN.").replace("MULTAS E JUROS","M/J")\
         .replace("OUTRAS RECEITAS","OUTR.")
    if "-" in n:
        p = n.split("-")
        return f"{p[0].strip()[:6]} {p[1].strip()[:5]}"
    return n[:12]

def buscar_arquivo(nome):
    caminhos = [nome, os.path.join("..",nome), os.path.join("pages",nome),
                os.path.join(os.path.dirname(__file__),"..",nome)]
    for p in caminhos:
        if os.path.exists(p): return p
    return None

def soma(df, cols):
    """Soma apenas colunas que existem no df."""
    presentes = [c for c in cols if c in df.columns]
    return df[presentes].sum().sum() if presentes else 0.0

# ── CARGA DE DADOS ────────────────────────────────────────────────────────────
@st.cache_data
def load_all_data():
    path_f  = buscar_arquivo("zEducação/São Tomás de Aquino.csv")
    path_r  = buscar_arquivo("zEducação/São Tomás de Aquino_R.csv")
    path_df = buscar_arquivo("zEducação/São Tomás de Aquino_DF.csv")
    if not path_f or not path_r or not path_df: return None, None, None

    # Fichas (F) — cabeçalho duplo → colunas no formato "Mês_Tipo"
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0,1])
    new_cols = []
    for col in df_f.columns:
        new_cols.append(col[1].strip() if "Unnamed" in col[0]
                        else f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols

    # Receitas (R) — header=0 obrigatório (header=1 destruiria os nomes das colunas)
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8', header=0)
    df_r.columns = [str(c).strip() for c in df_r.columns]

    # Despesas por fonte (DF)
    df_df = pd.read_csv(path_df, sep=None, engine='python', encoding='utf-8')
    df_df.columns = [str(c).strip() for c in df_df.columns]

    # Limpeza numérica — F
    for col in df_f.columns:
        if any(k in col for k in ['Orçado','Saldo','Liquidado','Empenhado','Pago',
                                   'Creditado','Anulado']):
            df_f[col] = df_f[col].apply(limpar_valor)

    # Limpeza numérica — R (inclui Repasse e Orçado Receitas)
    COLS_R = ORDEM_MESES + ['Total','Orçado Receitas','Repasse','2025']
    for col in df_r.columns:
        if col in COLS_R: df_r[col] = df_r[col].apply(limpar_valor)

    # Limpeza numérica — DF
    for col in df_df.columns:
        if col in ORDEM_MESES + ['Total']:
            df_df[col] = df_df[col].apply(limpar_valor)

    # Padronizar coluna Fonte
    for df, colname in [(df_f,'Fonte'),(df_df,'Fonte')]:
        if colname in df.columns:
            df[colname] = df[colname].astype(str).str.replace('.0','',regex=False).str.strip()

    return df_f, df_r, df_df

df_f_raw, df_r, df_df_raw = load_all_data()

# ── MESES DISPONÍVEIS ─────────────────────────────────────────────────────────
meses_disponiveis = ['Janeiro','Fevereiro']

if df_f_raw is not None and df_r is not None:

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    st.sidebar.title("🔍 Filtros de Análise")
    search_term = st.sidebar.text_input("Filtrar Fichas:", "")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Setores")
    for label, key in [("FUNDEB","FUNDEB"),
                        ("Recursos Próprios","Recursos Próprios"),
                        ("Recursos Vinculados","Recursos Vinculados"),
                        ("Visão Macro","Visão Macro"),
                        ("Folha de Pagamento","Folha de Pagamento")]:
        if st.sidebar.button(label, use_container_width=True):
            st.session_state.setor = key

    # =========================================================================
    # SETOR FUNDEB
    # =========================================================================
    if st.session_state.setor == 'FUNDEB':
        st.markdown("<h1 style='text-align:left;'>📖 São Tomás de Aquino — FUNDEB</h1>",
                    unsafe_allow_html=True)

        def cat_receita(desc):
            d = str(desc).upper().strip()
            if 'VAAR' in d or 'VAAT' in d:             return 'VAAR/VAAT'
            if 'ETI'  in d or 'TEMPO INTEGRAL' in d:   return 'ETI'
            if 'APLICAÇÃO' in d or 'RENDIMENTOS' in d: return 'Rendimentos'
            return 'Principal'

        # ── Receitas ─────────────────────────────────────────────────────────
        df_r_fundeb = df_r[df_r['Categoria'].str.strip() == 'FUNDEB'].copy()
        df_r_fundeb['Descrição da Receita'] = df_r_fundeb['Descrição da Receita'].str.strip()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)

        tot_prev_municipio = df_r_fundeb[df_r_fundeb['Subcategoria']=='Principal'
                                         ]['Orçado Receitas'].sum()   # 6.650.000,00
        tot_prev_portaria  = df_r_fundeb['Repasse'].sum()             # 6.351.300,40
        tot_rec_periodo    = soma(df_r_fundeb, meses_disponiveis)     # 1.170.192,01
        tot_eti            = soma(df_r_fundeb[df_r_fundeb['Subcategoria']=='ETI'],
                                  meses_disponiveis)                  # 0,00

        # ── Despesas (somente fontes do ano vigente: 15407 / 15403) ──────────
        df_df_fundeb = df_df_raw[df_df_raw['Fonte'].isin(['15407','15403'])].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb['Fonte'].apply(
            lambda x: 'FUNDEB 70%' if x=='15407' else 'FUNDEB 30%')

        base_indice_70  = soma(df_r_fundeb[df_r_fundeb['Subcategoria'].isin(
                                ['Principal','Rendimentos'])], meses_disponiveis)  # 1.170.192,01
        desp_70_vigente = soma(df_df_fundeb[(df_df_fundeb['Fonte']=='15407') &
                                (df_df_fundeb['Tipo']=='Liquidado')], meses_disponiveis)  # 1.010.067,36
        desp_30_vigente = soma(df_df_fundeb[(df_df_fundeb['Fonte']=='15403') &
                                (df_df_fundeb['Tipo']=='Liquidado')], meses_disponiveis)  # 40.399,44
        tot_desp_vigente = desp_70_vigente + desp_30_vigente         # 1.050.466,80
        perc_70_indice   = (desp_70_vigente/base_indice_70*100) if base_indice_70>0 else 0.0  # 86,32%

        # ── Cards de previsão ─────────────────────────────────────────────────
        st.markdown("##### Previsões Orçamentárias")
        p1, p2, p3 = st.columns(3)
        with p1: st.metric("Previsão Receitas (Orçamento Município)",
                            formar_real(tot_prev_municipio))
        with p2: st.metric("Previsão de Receitas (Port. Intermin. nº 14/dez 2025)",
                            formar_real(tot_prev_portaria))
        with p3: st.metric("Atualização Quadrimestral", "—")
        st.markdown("---")

        # ═════════════════════════════════════════════════════════════════════
        # GRÁFICO 1 — Receitas e Despesas FUNDEB
        # ═════════════════════════════════════════════════════════════════════
        st.subheader("🔹 1. Receitas e Despesas FUNDEB")

        saldo     = tot_rec_periodo - tot_desp_vigente         # 119.725,21
        exec_perc = (tot_desp_vigente/tot_rec_periodo*100) if tot_rec_periodo>0 else 0

        t1, t2, t3 = st.columns(3)
        with t1: st.metric(f"Total Receitas ({meses_disponiveis[0]}–{meses_disponiveis[-1]})",
                            formar_real(tot_rec_periodo))
        with t2: st.metric("Total Despesas Liquidadas – Ano Vigente",
                            formar_real(tot_desp_vigente))
        with t3:
            # Verde se saldo positivo (receitas > despesas), vermelho se negativo
            delta_val   = exec_perc if saldo >= 0 else -exec_perc
            st.metric("Saldo (Receitas − Despesas Vigentes)", formar_real(saldo),
                      delta=f"{delta_val:.1f}% Saldo", delta_color="normal")

        tipo_rd = st.segmented_control("Visualização:", ["Mensal","Acumulado"],
                                       default="Mensal", key="rd_btn_f")

        fig_rd = go.Figure()
        categorias_rec  = list(df_r_fundeb['Subcategoria'].unique())
        legendas_usadas = set()

        if tipo_rd == "Mensal":
            for m in meses_disponiveis:
                tot_rec_m  = soma(df_r_fundeb, [m])
                tot_desp_m = soma(df_df_fundeb[df_df_fundeb['Tipo']=='Liquidado'], [m])
                for cat in categorias_rec:
                    val = soma(df_r_fundeb[df_r_fundeb['Subcategoria']==cat], [m])
                    desc_list = df_r_fundeb[df_r_fundeb['Subcategoria']==cat][
                        'Descrição da Receita'].unique().tolist()
                    show = f"rec_{cat}" not in legendas_usadas
                    legendas_usadas.add(f"rec_{cat}")
                    part = f"{val/tot_rec_m*100:.1f}%" if tot_rec_m>0 else "—"
                    fig_rd.add_trace(go.Bar(
                        name=cat, x=[[m],["Receitas"]], y=[val],
                        marker_color=COR_REC.get(cat,'#27ae60'),
                        legendgroup=f"rec_{cat}", showlegend=show,
                        text=formar_real(val) if val>0 else "",
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
                    val = soma(df_df_fundeb[(df_df_fundeb['Fonte']==fonte_cod) &
                                            (df_df_fundeb['Tipo']=='Liquidado')], [m])
                    show = label_desp not in legendas_usadas
                    legendas_usadas.add(label_desp)
                    prop = f"{val/tot_desp_m*100:.1f}%" if tot_desp_m>0 else "—"
                    fig_rd.add_trace(go.Bar(
                        name=label_desp, x=[[m],["Despesas"]], y=[val],
                        marker_color=COR_DESP[label_desp],
                        legendgroup=label_desp, showlegend=show,
                        text=formar_real(val) if val>0 else "",
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
        else:  # Acumulado
            for cat in categorias_rec:
                val = soma(df_r_fundeb[df_r_fundeb['Subcategoria']==cat], meses_disponiveis)
                desc_list = df_r_fundeb[df_r_fundeb['Subcategoria']==cat][
                    'Descrição da Receita'].unique().tolist()
                part = f"{val/tot_rec_periodo*100:.1f}%" if tot_rec_periodo>0 else "—"
                fig_rd.add_trace(go.Bar(
                    name=cat, x=[["Acumulado"],["Receitas"]], y=[val],
                    marker_color=COR_REC.get(cat,'#27ae60'),
                    legendgroup=f"rec_{cat}", showlegend=True,
                    text=formar_real(val) if val>0 else "",
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
                val = soma(df_df_fundeb[(df_df_fundeb['Fonte']==fonte_cod) &
                                        (df_df_fundeb['Tipo']=='Liquidado')], meses_disponiveis)
                prop = f"{val/tot_desp_vigente*100:.1f}%" if tot_desp_vigente>0 else "—"
                fig_rd.add_trace(go.Bar(
                    name=label_desp, x=[["Acumulado"],["Despesas"]], y=[val],
                    marker_color=COR_DESP[label_desp],
                    legendgroup=label_desp, showlegend=True,
                    text=formar_real(val) if val>0 else "",
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

        # ═════════════════════════════════════════════════════════════════════
        # GRÁFICO 2 — Índice de Aplicação em Pessoal (Mín. 70%)
        # metric_contabil exibido APENAS na visão Acumulado
        # Legenda posicionada para não cobrir o eixo X
        # ═════════════════════════════════════════════════════════════════════
        st.subheader("🔹 2. Índice de Aplicação em Pessoal (Mín. 70%)")
        tipo_70 = st.segmented_control("Visualização:", ["Mensal","Acumulado"],
                                       default="Mensal", key="tipo_70_btn")

        if tipo_70 == "Acumulado":
            a1, a2 = st.columns(2)
            with a1: st.metric("Base de Cálculo (Principal + Rendimentos)",
                                formar_real(base_indice_70))
            with a2: st.metric("Despesas FUNDEB 70% – Liquidado",
                                formar_real(desp_70_vigente))
            metric_contabil("Aplicação em Pessoal (Mín. 70%)", perc_70_indice, 70.0)

            cor_barra = "#27ae60" if perc_70_indice>=70 else "#e74c3c"
            fig_70 = go.Figure()
            fig_70.add_trace(go.Bar(
                x=["Receita Base\n(Principal + Rendimentos)"], y=[base_indice_70],
                name="Receita Base", marker_color="#003366",
                text=[formar_real(base_indice_70)],
                textposition='inside', insidetextanchor='middle',
                hovertemplate=("<span style='color:white;'><b>Receita Base FUNDEB</b><br>"
                               "Valor: <b>"+formar_real(base_indice_70)+"</b></span><extra></extra>"),
            ))
            fig_70.add_trace(go.Bar(
                x=["Despesas 70%\n(Liquidado)"], y=[desp_70_vigente],
                name=f"Despesas 70% — {perc_70_indice:.2f}%", marker_color=COR_DESP['FUNDEB 70% – Vigente'],
                text=[f"{formar_real(desp_70_vigente)}\n({perc_70_indice:.2f}%)"],
                textposition='inside', insidetextanchor='middle',
                hovertemplate=("<span style='color:white;'><b>Despesas FUNDEB 70%</b><br>"
                               "Fonte: 15407 | Liquidado<br>"
                               "Valor: <b>"+formar_real(desp_70_vigente)+"</b><br>"
                               "Índice: <b>"+f"{perc_70_indice:.2f}%"+"</b></span><extra></extra>"),
            ))
            fig_70.add_hline(y=base_indice_70*0.70, line_dash="dot", line_color="green",
                             annotation_text=f"Meta 70% = {formar_real(base_indice_70*0.70)}",
                             annotation_position="top left")
            fig_70.update_layout(
                separators=",.", barmode='group', hoverlabel=HOVER_STYLE,
                yaxis=dict(showticklabels=False),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                height=440, margin=dict(b=80),
            )

        else:  # Mensal — sem metric_contabil
            dados_70_m = []
            for m in meses_disponiveis:
                base_m   = soma(df_r_fundeb[df_r_fundeb['Subcategoria'].isin(
                                    ['Principal','Rendimentos'])], [m])
                liq_70_m = soma(df_df_fundeb[(df_df_fundeb['Fonte']=='15407') &
                                             (df_df_fundeb['Tipo']=='Liquidado')], [m])
                liq_30_m = soma(df_df_fundeb[(df_df_fundeb['Fonte']=='15403') &
                                             (df_df_fundeb['Tipo']=='Liquidado')], [m])
                perc_m   = (liq_70_m/base_m*100) if base_m>0 else 0.0
                dados_70_m += [
                    {"Mês":m,"Tipo":"Receita Base","Valor":base_m,"Texto":""},
                    {"Mês":m,"Tipo":"FUNDEB 70% (Liquidado)","Valor":liq_70_m,"Texto":f"{perc_m:.1f}%"},
                    {"Mês":m,"Tipo":"FUNDEB 30% (Liquidado)","Valor":liq_30_m,"Texto":""},
                ]
            fig_70 = px.bar(
                pd.DataFrame(dados_70_m), x='Mês', y='Valor', color='Tipo',
                barmode='group', text='Texto',
                color_discrete_map={
                    "Receita Base":           "#003366",
                    "FUNDEB 70% (Liquidado)": COR_DESP['FUNDEB 70% – Vigente'],
                    "FUNDEB 30% (Liquidado)": COR_DESP['FUNDEB 30% – Vigente'],
                },
                category_orders={"Mês":ORDEM_MESES}
            )
            df_meta_70 = pd.DataFrame([
                {"Mês":m, "Meta 70%": soma(df_r_fundeb[df_r_fundeb['Subcategoria'].isin(
                    ['Principal','Rendimentos'])],[m])*0.70}
                for m in meses_disponiveis
            ])
            fig_70.add_trace(go.Scatter(
                x=df_meta_70['Mês'], y=df_meta_70['Meta 70%'],
                mode='lines+markers', name='Meta 70% (Mensal)',
                line=dict(color='green', dash='dot')
            ))
            fig_70.update_traces(
                selector=dict(type='bar'), textposition='outside', hoverlabel=HOVER_STYLE,
                hovertemplate=("<span style='color:white;'><b>%{x} — %{data.name}</b><br>"
                               "Valor: <b>R$ %{y:,.2f}</b></span><extra></extra>")
            )
            fig_70.update_layout(
                separators=",.", yaxis=dict(showticklabels=False),
                xaxis_title=None,   # remove "Mês" do eixo para não sobrepor à legenda
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                height=460, margin=dict(b=90),
            )

        st.plotly_chart(fig_70, use_container_width=True, config=CONFIG_PT)
        st.markdown("---")

        # ═════════════════════════════════════════════════════════════════════
        # GRÁFICO 3 — Percentual Tempo Integral
        # Uma única barra (Receita Base FUNDEB) + linha de referência 4%
        # ═════════════════════════════════════════════════════════════════════
        st.subheader("🔹 3. Percentual Tempo Integral")

        meta_eti_perc = 4.0
        val_meta_eti  = base_indice_70 * (meta_eti_perc/100)   # 46.807,68

        e1, e2 = st.columns(2)
        with e1: st.metric("Total Receitas FUNDEB (período)", formar_real(tot_rec_periodo))
        with e2: st.metric(f"Equivalente a {meta_eti_perc:.0f}% da Receita Base",
                            formar_real(val_meta_eti))

        fig_eti = go.Figure()
        fig_eti.add_trace(go.Bar(
            x=["Receita Base FUNDEB"], y=[base_indice_70],
            name="Receita Base", marker_color="#003366",
            text=[formar_real(base_indice_70)],
            textposition='inside', insidetextanchor='middle',
            hovertemplate=("<span style='color:white;'><b>Receita Base FUNDEB</b><br>"
                           "Principal + Rendimentos<br>"
                           "Valor: <b>"+formar_real(base_indice_70)+"</b></span><extra></extra>"),
        ))
        fig_eti.add_hline(
            y=val_meta_eti, line_dash="dot", line_color="#f39c12", line_width=2,
            annotation_text=f"Referência ETI {meta_eti_perc:.0f}% = {formar_real(val_meta_eti)}",
            annotation_position="top left"
        )
        fig_eti.update_layout(
            separators=",.", hoverlabel=HOVER_STYLE,
            yaxis=dict(showticklabels=False), showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.20, xanchor="center", x=0.5),
            height=380,
        )
        st.plotly_chart(fig_eti, use_container_width=True, config=CONFIG_PT)

    # =========================================================================
    # SETOR RECURSOS PRÓPRIOS
    # =========================================================================
    elif st.session_state.setor == 'Recursos Próprios':
        st.markdown("<h1 style='text-align:left;'>📖 São Tomás de Aquino — Recursos Próprios (25%)</h1>",
                    unsafe_allow_html=True)

        def obter_soma_rp(df, meses):
            col_map = {c.strip().lower():c for c in df.columns}
            cols = [col_map[m.lower()] for m in meses if m.lower() in col_map]
            return df[cols].sum().sum() if cols else 0.0

        # Mapeamento: nome longo → sigla do grupo principal
        ABREV_IMPOSTO = {
            'PROPRIEDADE PREDIAL E TERRITORIAL URBANA':'IPTU',
            'TRANSMISSÃO "INTER VIVOS"':'ITBI','TRANSMISSÃO INTER VIVOS':'ITBI',
            'RENDA - RETIDO NA FONTE':'IR','RENDA – RETIDO NA FONTE':'IR',
            'SERVIÇOS DE QUALQUER NATUREZA':'ISS',
            'FUNDO DE PARTICIPAÇÃO DOS MUNICÍPIOS':'FPM',
            'FUNDO DE PARTICIPAÇÃO DO MUNICÍPIOS':'FPM',
            'PROPRIEDADE TERRITORIAL RURAL':'ITR',
            'ICMS':'ICMS','IPVA':'IPVA','IPI':'IPI','INSS':'INSS',
        }

        def abrev_imposto(desc):
            """Retorna a sigla completa (ex: IPTU – D.A.) para uso interno.
            Normaliza aspas tipográficas (\u201c\u201d) para aspas retas antes de comparar."""
            du = str(desc).upper()
            # Normaliza aspas curvas/tipográficas → aspas retas (ex: "Inter Vivos" → "Inter Vivos")
            du = du.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")
            for longo, curto in ABREV_IMPOSTO.items():
                if longo in du:
                    if 'DÍVIDA ATIVA' in du and 'MULTAS' in du: return f"{curto} – D.A. M/J"
                    if 'DÍVIDA ATIVA' in du:                     return f"{curto} – D.A."
                    if 'MULTAS' in du:                           return f"{curto} – M/J"
                    if 'OUTROS RENDIMENTOS' in du:               return f"{curto} – Outros"
                    if 'DEZEMBRO' in du:                         return f"{curto} – Dez"
                    if 'JULHO' in du or 'SETEMBRO' in du:        return f"{curto} – Jul/Set"
                    return curto
            return desc.strip()[:20]

        def grupo_imposto(abrev):
            """Extrai apenas o nome do grupo, sem subcategoria (D.A., M/J etc.)."""
            return abrev.split(' –')[0].strip()

        PALETA_RP = ['#1a7a4a','#27ae60','#17a589','#1abc9c',
                     '#2980b9','#1565c0','#0288d1','#00838f',
                     '#00acc1','#26c6da','#43a047','#66bb6a',
                     '#80cbc4','#4dd0e1']

        # Base: Impostos + Cota-Parte
        df_r_base = df_r[df_r['Categoria'].str.strip().isin(['Impostos','Cota-Parte'])].copy()
        df_r_base['Descrição da Receita'] = df_r_base['Descrição da Receita'].str.strip()
        df_r_base['Abrev'] = df_r_base['Descrição da Receita'].apply(abrev_imposto)
        df_r_base['Grupo'] = df_r_base['Abrev'].apply(grupo_imposto)

        # Agrupamento por grupo (soma IPTU + IPTU D.A. + IPTU M/J → IPTU único)
        df_r_grupo = df_r_base.groupby('Grupo')[meses_disponiveis].sum().reset_index()
        grupos_unicos = list(df_r_grupo['Grupo'].unique())
        mapa_cores_grupos = {g: PALETA_RP[i%len(PALETA_RP)] for i,g in enumerate(grupos_unicos)}

        # Dedução FUNDEB
        df_r_ded = df_r[df_r['Categoria'].str.strip().str.startswith('Dedução',na=False)].copy()

        prev_impostos = df_r[df_r['Categoria'].str.strip()=='Impostos']['Orçado Receitas'].sum()
        tot_rec_base  = obter_soma_rp(df_r_base, meses_disponiveis)
        tot_deducoes  = abs(obter_soma_rp(df_r_ded, meses_disponiveis))
        meta_25_valor = tot_rec_base * 0.25

        fase_despesa = st.segmented_control(
            " (Impacta Indicadores Superiores):",
            ["Empenhado","Liquidado","Pago"], default="Liquidado", key="fase_desp_rp")
        df_df_15001 = df_df_raw[(df_df_raw['Fonte']=='15001') &
                                 (df_df_raw['Tipo']==fase_despesa)].copy()

        total_desp_15001 = df_df_15001[meses_disponiveis].sum().sum()
        esforco_total    = total_desp_15001 + tot_deducoes
        perc_25          = (esforco_total/tot_rec_base*100) if tot_rec_base>0 else 0.0
        saldo_nec_25     = max(0.0, meta_25_valor - esforco_total)

        df_15000_outras = df_df_raw[
            df_df_raw['Fonte'].str.match(r'^150\d*$',na=False) &
            (df_df_raw['Fonte']!='15001') & (df_df_raw['Tipo']=='Liquidado')].copy()
        val_outras_fontes = df_15000_outras[meses_disponiveis].sum().sum()

        # Cards superiores
        st.markdown("##### Previsões e Arrecadação")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Previsão Orçamentária — Impostos", formar_real(prev_impostos))
        with c2: st.metric(f"Receitas Arrecadadas ({meses_disponiveis[0]}–{meses_disponiveis[-1]})",
                            formar_real(tot_rec_base))
        # Saldo vs meta: positivo = meta atingida (verde ↑), negativo = abaixo da meta (vermelho ↓)
        # Mesmo padrão do FUNDEB Gráfico 1
        perc_vs_meta = ((esforco_total - meta_25_valor) / meta_25_valor * 100) if meta_25_valor > 0 else 0
        with c3: st.metric("Meta 25% (sobre o arrecadado)", formar_real(meta_25_valor),
                            delta=f"{perc_vs_meta:.1f}% Saldo", delta_color="normal")
        st.markdown("---")

        # ── Gráfico Receitas por Imposto (AGRUPADO) ───────────────────────────
        # M/J, D.A. e D.A. M/J são somados com o principal de cada imposto
        st.subheader("🔹 Receitas Recursos Próprios (Impostos e Cota-Parte)")
        view_rp = st.segmented_control("Visualização Receitas:", ["Mensal","Acumulado"],
                                       default="Mensal", key="view_rp")

        # Navegação — botões mostram apenas o grupo (IPTU, ITBI, FPM…)
        lista_completa = ["📊 Acumulado Geral"] + grupos_unicos
        if 'idx_nav_rp' not in st.session_state: st.session_state.idx_nav_rp = 0

        grid = st.columns([0.5,1.2,1.2,1.2,1.2,1.2,0.5])
        with grid[0]:
            if st.button("◀", key="rp_left"):
                st.session_state.idx_nav_rp = max(0, st.session_state.idx_nav_rp-5)
                st.rerun()
        fim_idx = min(st.session_state.idx_nav_rp+5, len(lista_completa))
        fatia   = lista_completa[st.session_state.idx_nav_rp:fim_idx]
        for i, item in enumerate(fatia):
            with grid[i+1]:
                label = item.replace("📊 ","") if "📊" in item else item
                if st.button(label, key=f"rp_btn_{item}", help=item, use_container_width=True):
                    st.session_state['ativo_rp'] = item.replace("📊 ","")
                    st.rerun()
        with grid[6]:
            if st.button("▶", key="rp_right"):
                if st.session_state.idx_nav_rp+5 < len(lista_completa):
                    st.session_state.idx_nav_rp += 5
                    st.rerun()

        ativo = st.session_state.get('ativo_rp', "Acumulado Geral")
        st.markdown(f"#### 📈 {ativo}")

        if view_rp == "Acumulado":
            if ativo == "Acumulado Geral":
                # Soma Jan+Fev por grupo e ordena do maior para o menor
                df_acum = df_r_grupo.copy()
                df_acum['Valor'] = df_acum[meses_disponiveis].sum(axis=1)
                df_acum = df_acum.sort_values('Valor', ascending=False)
                fig_rp = px.bar(df_acum, x='Grupo', y='Valor', color='Grupo',
                                text_auto='.3s', color_discrete_map=mapa_cores_grupos)
            else:
                row = df_r_grupo[df_r_grupo['Grupo']==ativo]
                val = row[meses_disponiveis].sum().sum() if len(row)>0 else 0
                fig_rp = px.bar(x=[ativo], y=[val], text_auto='.3s',
                                color_discrete_sequence=[mapa_cores_grupos.get(ativo,'#003366')])
        else:  # Mensal
            if ativo == "Acumulado Geral":
                dados_m = []
                for m in meses_disponiveis:
                    for _, row in df_r_grupo.iterrows():
                        dados_m.append({"Mês":m,"Imposto":row['Grupo'],"Valor":row[m]})
                fig_rp = px.bar(pd.DataFrame(dados_m), x='Mês', y='Valor', color='Imposto',
                                barmode='stack', text_auto='.2s',
                                color_discrete_map=mapa_cores_grupos,
                                category_orders={"Mês":ORDEM_MESES})
            else:
                row = df_r_grupo[df_r_grupo['Grupo']==ativo]
                dados_m = [{"Mês":m,"Valor":row[m].sum() if len(row)>0 else 0}
                           for m in meses_disponiveis]
                fig_rp = px.bar(pd.DataFrame(dados_m), x='Mês', y='Valor', text_auto='.2s',
                                color_discrete_sequence=[mapa_cores_grupos.get(ativo,'#003366')],
                                category_orders={"Mês":ORDEM_MESES})

        # Hover — no Acumulado Geral %{data.name} traz o nome do grupo (trace nomeado);
        # nos botões individuais (FPM, ICMS…) o trace não tem nome, então injeta o ativo diretamente
        nome_hover = "%{data.name}" if ativo == "Acumulado Geral" else ativo
        fig_rp.update_traces(
            hovertemplate=(
                "<span style='color:white;'>"
                "<b>%{x}</b><br>"
                f"Imposto: {nome_hover}<br>"
                "Setor: Recursos Próprios<br>"
                "Valor: <b>R$ %{y:,.2f}</b>"
                "</span><extra></extra>"
            ),
            hoverlabel=HOVER_STYLE
        )
        fig_rp.update_layout(separators=",.", yaxis=dict(showticklabels=False))
        st.plotly_chart(fig_rp, use_container_width=True, config=CONFIG_PT)
        st.markdown("---")

        # ── Despesas Fonte 15001 ──────────────────────────────────────────────
        st.subheader("🔹 Despesas Fonte 15001")
        st.markdown("Detalhamento por Estágio (Empenhado, Liquidado, Pago)")
        view_desp = st.segmented_control("Visualização Despesas:", ["Mensal","Acumulado"],
                                         default="Mensal", key="view_desp")
        df_15001_todas = df_df_raw[(df_df_raw['Fonte']=='15001') &
                                    (df_df_raw['Tipo'].isin(['Empenhado','Liquidado','Pago']))].copy()

        if view_desp == "Acumulado":
            total_rp_acum = df_15001_todas[meses_disponiveis].sum().sum()
            df_desp_plot  = []
            for fase in ["Empenhado","Liquidado","Pago"]:
                val  = df_15001_todas[df_15001_todas['Tipo']==fase][meses_disponiveis].sum().sum()
                prop = (val/total_rp_acum*100) if total_rp_acum>0 else 0
                df_desp_plot.append({"Fase":fase,"Valor":val,
                                     "Proporção":f"{prop:.2f}%","Dedução":tot_deducoes,"Despesa":val})
            df_desp_plot = pd.DataFrame(df_desp_plot)
            df_desp_plot['Fase'] = pd.Categorical(df_desp_plot['Fase'],
                                                   ["Empenhado","Liquidado","Pago"])
            fig_d = px.bar(df_desp_plot, x='Fase', y='Valor', color='Fase', text_auto='.3s',
                           custom_data=['Proporção','Dedução','Despesa'],
                           color_discrete_map={'Empenhado':'#fa3d3d','Liquidado':'#860000','Pago':'#470000'})
        else:
            dados_d_m = []
            for m in meses_disponiveis:
                col_d   = m if m in df_15001_todas.columns else None
                col_ded = m if m in df_r_ded.columns else None
                total_m = df_15001_todas[col_d].sum() if col_d else 0
                ded_m   = abs(df_r_ded[col_ded].sum()) if col_ded else 0
                for fase in ['Empenhado','Liquidado','Pago']:
                    val  = df_15001_todas[df_15001_todas['Tipo']==fase][col_d].sum() if col_d else 0
                    prop = (val/total_m*100) if total_m>0 else 0
                    dados_d_m.append({"Mês":m,"Fase":fase,"Valor":val,
                                      "Proporção":f"{prop:.2f}%","Dedução":ded_m,"Despesa":val})
            df_dados_d_m = pd.DataFrame(dados_d_m)
            df_dados_d_m['Fase'] = pd.Categorical(df_dados_d_m['Fase'],["Empenhado","Liquidado","Pago"])
            fig_d = px.bar(df_dados_d_m, x='Mês', y='Valor', color='Fase', barmode='group',
                           text_auto='.2s', custom_data=['Proporção','Dedução','Despesa'],
                           color_discrete_map={'Empenhado':'#fa3d3d','Liquidado':'#860000','Pago':'#470000'},
                           category_orders={"Mês":ORDEM_MESES,"Fase":["Empenhado","Liquidado","Pago"]})

        fig_d.update_traces(
            hovertemplate=("<span style='color:white;'><b>%{x}</b><br>"
                           "Estágio: %{fullData.name}<br>"
                           "Valor (15001): R$ %{customdata[2]:,.2f}<br>"
                           "Dedução FUNDEB: R$ %{customdata[1]:,.2f}<br>"
                           "Proporção: %{customdata[0]}</span><extra></extra>"),
            hoverlabel=HOVER_STYLE)
        fig_d.update_layout(separators=",.", yaxis=dict(showticklabels=False))
        st.plotly_chart(fig_d, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

        # ── Análise Comparativa e Meta (25%) ─────────────────────────────────
        st.subheader("🔹 Análise Comparativa e Meta (Mínimo 25%)")
        view_meta     = st.segmented_control("Visualização Meta:", ["Mensal","Acumulado"],
                                             default="Mensal", key="view_meta")
        cor_aplicacao = "#27ae60" if perc_25>=25 else "#e74c3c"

        if view_meta == "Acumulado":
            idx1, idx2, idx3 = st.columns(3)
            with idx1: st.metric("Receitas Base (Impostos + Cota-Parte)", formar_real(tot_rec_base))
            with idx2: st.metric(f"Esforço Total ({fase_despesa} 15001 + Deduções)", formar_real(esforco_total))
            with idx3: metric_contabil("Índice de Aplicação (Mín. 25%)", perc_25, 25.0)

            prop_desp = (total_desp_15001/esforco_total*100) if esforco_total>0 else 0
            prop_ded  = (tot_deducoes/esforco_total*100)    if esforco_total>0 else 0
            fig_meta  = go.Figure()
            fig_meta.add_trace(go.Bar(
                x=["Receitas Base"], y=[tot_rec_base], name="Receitas Base",
                marker_color="#003366", text=[formar_real(tot_rec_base)],
                textposition='inside', insidetextanchor='middle',
                hovertemplate=("<span style='color:white;'><b>Receitas Base</b><br>"
                               "Impostos + Cota-Parte<br>Valor: <b>"+formar_real(tot_rec_base)+"</b></span><extra></extra>"),
            ))
            fig_meta.add_trace(go.Bar(
                x=["Aplicação Total"], y=[total_desp_15001],
                name=f"Despesa 15001 ({fase_despesa})", marker_color="#860000",
                text=[f"{formar_real(total_desp_15001)}\n({prop_desp:.1f}%)"],
                textposition='inside', insidetextanchor='middle',
                customdata=[[formar_real(total_desp_15001),f"{prop_desp:.1f}%",fase_despesa]],
                hovertemplate=("<span style='color:white;'><b>Despesa Fonte 15001</b><br>"
                               "Estágio: %{customdata[2]}<br>Valor: <b>%{customdata[0]}</b><br>"
                               "% do esforço: %{customdata[1]}</span><extra></extra>"),
            ))
            fig_meta.add_trace(go.Bar(
                x=["Aplicação Total"], y=[tot_deducoes],
                name="Dedução FUNDEB", marker_color="#f39c12",
                text=[f"{formar_real(tot_deducoes)}\n({prop_ded:.1f}%)"],
                textposition='inside', insidetextanchor='middle',
                customdata=[[formar_real(tot_deducoes),f"{prop_ded:.1f}%"]],
                hovertemplate=("<span style='color:white;'><b>Dedução FUNDEB</b><br>"
                               "Valor: <b>%{customdata[0]}</b><br>"
                               "% do esforço: %{customdata[1]}</span><extra></extra>"),
            ))
            fig_meta.add_hline(y=tot_rec_base*0.25, line_dash="dash", line_color="#f39c12",
                               annotation_text=f"Meta 25% = {formar_real(tot_rec_base*0.25)}",
                               annotation_position="top left")
            if val_outras_fontes>0:
                fig_meta.add_annotation(x="Aplicação Total", y=esforco_total*1.05,
                    text=f"⚠️ Outras fontes (anos ant.): {formar_real(val_outras_fontes)}",
                    showarrow=False, font=dict(color="#aaaaaa",size=11))
            fig_meta.update_layout(separators=",.", barmode='stack', hoverlabel=HOVER_STYLE,
                                   yaxis=dict(showticklabels=False), showlegend=True,
                                   legend=dict(orientation="h",yanchor="bottom",y=-0.20,
                                               xanchor="center",x=0.5), height=450)
        else:
            dados_meta_m = []
            for m in meses_disponiveis:
                col_b = m if m in df_r_base.columns else None
                col_d = m if m in df_df_15001.columns else None
                col_e = m if m in df_r_ded.columns else None
                r_m   = df_r_base[col_b].sum() if col_b else 0
                d_m   = df_df_15001[col_d].sum() if col_d else 0
                ded_m = abs(df_r_ded[col_e].sum()) if col_e else 0
                dados_meta_m += [
                    {"Mês":m,"Tipo":"Receitas Base","Valor":r_m,"Dedução":0,"Desp":0,"Texto":""},
                    {"Mês":m,"Tipo":f"Desp. 15001 ({fase_despesa})","Valor":d_m,
                     "Dedução":ded_m,"Desp":d_m,
                     "Texto":f"{d_m/(d_m+ded_m)*100:.1f}% desp." if (d_m+ded_m)>0 else ""},
                    {"Mês":m,"Tipo":"Dedução FUNDEB","Valor":ded_m,
                     "Dedução":ded_m,"Desp":d_m,
                     "Texto":f"{ded_m/(d_m+ded_m)*100:.1f}% ded." if (d_m+ded_m)>0 else ""},
                ]
            df_meta_m = pd.DataFrame(dados_meta_m)
            fig_meta  = px.bar(df_meta_m, x='Mês', y='Valor', color='Tipo', barmode='group',
                               text='Texto', custom_data=['Dedução','Desp'],
                               color_discrete_map={
                                   "Receitas Base":"#003366",
                                   f"Desp. 15001 ({fase_despesa})":"#860000",
                                   "Dedução FUNDEB":"#f39c12"},
                               category_orders={"Mês":ORDEM_MESES})
            fig_meta.update_traces(
                hovertemplate=("<span style='color:white;'><b>%{x} — %{data.name}</b><br>"
                               "Valor: R$ %{y:,.2f}<br>"
                               "Dedução mês: R$ %{customdata[0]:,.2f}<br>"
                               "Desp. 15001 mês: R$ %{customdata[1]:,.2f}</span><extra></extra>"),
                hoverlabel=HOVER_STYLE)
            df_linha = df_meta_m[df_meta_m['Tipo']=='Receitas Base'].copy()
            df_linha['Meta 25%'] = df_linha['Valor']*0.25
            fig_meta.add_trace(go.Scatter(x=df_linha['Mês'], y=df_linha['Meta 25%'],
                mode='lines+markers', name='Meta 25% (Mensal)',
                line=dict(color='#f39c12',dash='dash')))
            fig_meta.update_layout(separators=",.", yaxis=dict(showticklabels=False),
                                   showlegend=True,
                                   legend=dict(orientation="h",yanchor="bottom",y=-0.25,
                                               xanchor="center",x=0.5))

        st.plotly_chart(fig_meta, use_container_width=True, config=CONFIG_PT)

    # =========================================================================
    # SETOR RECURSOS VINCULADOS
    # =========================================================================
    elif st.session_state.setor == 'Recursos Vinculados':
        st.markdown("<h1 style='text-align:left;'>📖 São Tomás de Aquino — Recursos Vinculados</h1>",
                    unsafe_allow_html=True)

        # Fontes confirmadas nas fichas de São Tomás (sem pares 2xxx)
        mapa_desp = {'PNAE':['1552'],'PNATE':['1553'],'PTE':['1576'],'QESE':['1550']}
        programas = ['PNAE','PNATE','PTE','QESE']
        COR_PROG  = {'PNAE':'#1a7a4a','PNATE':'#17a589','PTE':'#2980b9','QESE':'#1565c0'}
        COR_DESP_V = '#860000'

        def soma_vinc(df, meses):
            col_map = {c.strip().lower():c for c in df.columns}
            cols = [col_map[m.lower()] for m in meses if m.lower() in col_map]
            return df[cols].sum().sum() if cols else 0.0

        df_r_vinc = df_r[df_r['Descrição da Receita'].str.upper().str.strip().isin(programas)].copy()
        tipo_vinc = st.segmented_control("Visualização:", ["Mensal","Acumulado"],
                                         default="Mensal", key="vinc_btn")
        st.markdown("---")

        for prog in programas:
            df_prog_r = df_r_vinc[df_r_vinc['Descrição da Receita'].str.upper().str.strip()==prog].copy()
            prev_prog   = df_prog_r['Orçado Receitas'].sum()
            rep_periodo = soma_vinc(df_prog_r, meses_disponiveis)
            desp_liq    = df_df_raw[df_df_raw['Fonte'].isin(mapa_desp[prog]) &
                                     (df_df_raw['Tipo']=='Liquidado')][meses_disponiveis].sum().sum()

            st.markdown(f"<h4 style='color:{COR_PROG[prog]};margin-bottom:4px;'>"
                        f"📊 Programa: {prog}</h4>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: st.metric(f"Repasse {meses_disponiveis[0]}–{meses_disponiveis[-1]} (Arrecadado)",
                                formar_real(rep_periodo))
            with c2: st.metric("Previsão de Repasse (Orçado Receitas)", formar_real(prev_prog))
            with c3: st.metric("Orçamento 2026 (Município)", formar_real(prev_prog))

            if tipo_vinc == "Mensal":
                dados_m = []
                for m in meses_disponiveis:
                    col_r  = m if m in df_prog_r.columns else None
                    col_df = m if m in df_df_raw.columns else None
                    rec_m  = df_prog_r[col_r].sum() if col_r else 0.0
                    desp_m = df_df_raw[df_df_raw['Fonte'].isin(mapa_desp[prog]) &
                                        (df_df_raw['Tipo']=='Liquidado')][col_df].sum() if col_df else 0.0
                    dados_m += [{"Mês":m,"Tipo":"Receita","Valor":rec_m},
                                 {"Mês":m,"Tipo":"Despesa (Liquidado)","Valor":desp_m}]
                fig_vinc = px.bar(pd.DataFrame(dados_m), x='Mês', y='Valor', color='Tipo',
                                  barmode='group', text_auto='.2s',
                                  color_discrete_map={'Receita':COR_PROG[prog],'Despesa (Liquidado)':COR_DESP_V},
                                  category_orders={"Mês":ORDEM_MESES})
            else:
                fig_vinc = px.bar(pd.DataFrame([{"Tipo":"Receita","Valor":rep_periodo},
                                                 {"Tipo":"Despesa (Liquidado)","Valor":desp_liq}]),
                                  x='Tipo', y='Valor', color='Tipo', barmode='group', text_auto='.2s',
                                  color_discrete_map={'Receita':COR_PROG[prog],'Despesa (Liquidado)':COR_DESP_V})

            fig_vinc.update_traces(selector=dict(type='bar'), textposition='outside',
                hovertemplate=("<span style='color:white;'><b>%{x}</b><br>"
                               "Programa: "+prog+"<br>Tipo: %{data.name}<br>"
                               "Valor: <b>R$ %{y:,.2f}</b></span><extra></extra>"),
                hoverlabel=HOVER_STYLE)
            fig_vinc.update_layout(separators=",.", yaxis=dict(showticklabels=False,title=None),
                                   xaxis_title=None, showlegend=True,
                                   legend=dict(orientation="h",yanchor="bottom",y=-0.30,
                                               xanchor="center",x=0.5), height=380)
            st.plotly_chart(fig_vinc, use_container_width=True, config=CONFIG_PT)
            st.markdown("---")

    # =========================================================================
    # SETOR VISÃO MACRO DA EDUCAÇÃO
    # ─── Seção em desenvolvimento — adicionar arquivo de dados quando disponível
    # =========================================================================
    elif st.session_state.setor == 'Visão Macro':
        st.markdown("<h1 style='text-align:left;'>📖 São Tomás de Aquino — Visão Macro da Educação</h1>",
                    unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("""
        > 📌 **Seção em desenvolvimento.** 
        """)

    # =========================================================================
    # SETOR FOLHA DE PAGAMENTO
    # ─── Seção em desenvolvimento — adicionar arquivo de dados quando disponível
    # =========================================================================
    elif st.session_state.setor == 'Folha de Pagamento':
        st.markdown("<h1 style='text-align:left;'>📖 São Tomás de Aquino — Folha de Pagamento</h1>",
                    unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("""
        > 📌 **Seção em desenvolvimento.** 
        """)

    # ── Relatório Geral de Fichas (todos os setores) ──────────────────────────
    st.markdown("### 📋 Relatório Geral de Fichas")
    df_f_filt = df_f_raw[df_f_raw['Atividade'].str.contains(
        search_term, na=False, case=False)].copy()
    st.dataframe(df_f_filt, use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar os arquivos CSV. Verifique a pasta 'zEducação'.")