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
        
        # 1. FUNÇÕES DE SUPORTE
        def cat_receita(desc):
            desc = str(desc).upper().strip()
            if 'VAAR' in desc: return 'VAAR'
            if 'ETI' in desc or 'TEMPO INTEGRAL' in desc: return 'ETI'
            if 'APLICAÇÃO' in desc or 'RENDIMENTOS' in desc: return 'Aplicação'
            return 'Principal'

        def obter_soma_mensal_robusta(df, meses):
            colunas_map = {c.strip().lower(): c for c in df.columns}
            cols_encontradas = [colunas_map[m.strip().lower()] for m in meses if m.strip().lower() in colunas_map]
            return df[cols_encontradas].sum().sum() if cols_encontradas else 0

        # 2. RECEITAS
        df_r_fundeb = df_r[df_r['Categoria'].str.strip() == 'FUNDEB'].copy()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)
        
        df_principal = df_r_fundeb[df_r_fundeb['Subcategoria'] == 'Principal']
        tot_prev_2026   = df_principal['Orçado Receitas'].sum()
        tot_rec_periodo = obter_soma_mensal_robusta(df_r_fundeb, meses_disponiveis)

        # 3. DESPESAS
        df_df_fundeb = df_df_raw[df_df_raw['Fonte'].str.contains('1540', na=False)].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb['Fonte'].apply(
            lambda x: 'FUNDEB 70%' if '15407' in str(x) else 'FUNDEB 30%'
        )
        
        desp_70_val = obter_soma_mensal_robusta(
            df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & (df_df_fundeb['Tipo'] == 'Liquidado')],
            meses_disponiveis
        )
        tot_desp_periodo = obter_soma_mensal_robusta(
            df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado'],
            meses_disponiveis
        )
        perc_70_indice = (desp_70_val / tot_rec_periodo * 100) if tot_rec_periodo > 0 else 0

        # 4. MÉTRICAS
        m1, m3 = st.columns(3)
        with m1: st.metric("Previsão Orçamentária 2026", formar_real(tot_prev_2026))
        with m3: metric_contabil("Aplicação em Pessoal (Mín. 70%)", perc_70_indice, 70.0)

        st.markdown("---")

        # ── GRÁFICO UNIFICADO: RECEITAS + DESPESAS LADO A LADO ───────────────
        st.subheader("🔹 1. Receitas e Despesas FUNDEB")

        # Totalizadores abaixo do título
        t1, t2, t3 = st.columns(3)
        with t1: st.metric("Total Receitas FUNDEB", formar_real(tot_rec_periodo))
        with t2: st.metric("Total Despesas FUNDEB (Liquidado)", formar_real(tot_desp_periodo))
        with t3:
            saldo = tot_rec_periodo - tot_desp_periodo
            st.metric("Saldo (Receitas − Despesas)", formar_real(saldo),
                      delta=f"{(tot_desp_periodo/tot_rec_periodo*100):.1f}% executado" if tot_rec_periodo > 0 else "—",
                      delta_color="inverse")

        tipo_rd = st.segmented_control(
            "Visualização:", ["Acumulado", "Mensal"], default="Mensal", key="rd_btn_f"
        )

        if tipo_rd == "Acumulado":
            # ── Receitas por subcategoria ──
            dados_rec = []
            for cat in df_r_fundeb['Subcategoria'].unique():
                val = obter_soma_mensal_robusta(df_r_fundeb[df_r_fundeb['Subcategoria'] == cat], meses_disponiveis)
                desc_list = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat]['Descrição da Receita'].unique().tolist()
                dados_rec.append({
                    "Painel": "Receitas",
                    "Legenda": cat,
                    "Eixo_X": cat,
                    "Valor": val,
                    "Tipo_Painel": "Receita",
                    "Fonte": "FUNDEB",
                    "Descrição": " | ".join(desc_list),
                    "Total_Painel": tot_rec_periodo,
                })

            # ── Despesas por fonte (70% / 30%) ──
            dados_desp = []
            for fonte in ['FUNDEB 70%', 'FUNDEB 30%']:
                val = obter_soma_mensal_robusta(
                    df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & (df_df_fundeb['Tipo'] == 'Liquidado')],
                    meses_disponiveis
                )
                prop = (val / tot_desp_periodo * 100) if tot_desp_periodo > 0 else 0
                dados_desp.append({
                    "Painel": "Despesas",
                    "Legenda": fonte,
                    "Eixo_X": fonte,
                    "Valor": val,
                    "Tipo_Painel": "Despesa",
                    "Fonte": fonte,
                    "Descrição": f"Liquidado — {prop:.1f}% do total de despesas",
                    "Total_Painel": tot_desp_periodo,
                })

            from plotly.subplots import make_subplots

            fig_rd = make_subplots(
                rows=1, cols=2,
                subplot_titles=["Receitas FUNDEB", "Despesas FUNDEB (Liquidado)"],
                horizontal_spacing=0.08
            )

            COR_REC  = {'Principal':'#002147', 'VAAR':'#003366', 'ETI':'#00509d', 'Aplicação':'#6699cc'}
            COR_DESP = {'FUNDEB 70%':'#660000', 'FUNDEB 30%':'#cc0000'}

            # Receitas — uma trace por subcategoria (para legenda colorida)
            for item in dados_rec:
                fig_rd.add_trace(
                    go.Bar(
                        name=item['Legenda'],
                        x=[item['Eixo_X']],
                        y=[item['Valor']],
                        marker_color=COR_REC.get(item['Legenda'], '#336699'),
                        text=f"R$ {item['Valor']:,.0f}".replace(",","X").replace(".",",").replace("X","."),
                        textposition='outside',
                        legendgroup=item['Legenda'],
                        customdata=[[
                            item['Legenda'],
                            "FUNDEB",
                            item['Descrição'],
                            formar_real(item['Valor']),
                            formar_real(item['Total_Painel']),
                            f"{(item['Valor']/item['Total_Painel']*100):.1f}%" if item['Total_Painel'] > 0 else "—",
                        ]],
                        hovertemplate=(
                            "<span style='color:white;'>"
                            "<b>📥 RECEITA — %{customdata[0]}</b><br>"
                            "Categoria: %{customdata[0]}<br>"
                            "Fundo: %{customdata[1]}<br>"
                            "Rubricas: %{customdata[2]}<br>"
                            "──────────────────<br>"
                            "Valor: <b>%{customdata[3]}</b><br>"
                            "Total Receitas: %{customdata[4]}<br>"
                            "Participação: %{customdata[5]}"
                            "</span><extra></extra>"
                        ),
                    ),
                    row=1, col=1
                )

            # Despesas — uma trace por fonte
            for item in dados_desp:
                fig_rd.add_trace(
                    go.Bar(
                        name=item['Legenda'],
                        x=[item['Eixo_X']],
                        y=[item['Valor']],
                        marker_color=COR_DESP.get(item['Legenda'], '#990000'),
                        text=f"R$ {item['Valor']:,.0f}".replace(",","X").replace(".",",").replace("X","."),
                        textposition='outside',
                        legendgroup=item['Legenda'],
                        customdata=[[
                            item['Fonte'],
                            "Liquidado",
                            item['Descrição'],
                            formar_real(item['Valor']),
                            formar_real(item['Total_Painel']),
                            f"{(item['Valor']/item['Total_Painel']*100):.1f}%" if item['Total_Painel'] > 0 else "—",
                        ]],
                        hovertemplate=(
                            "<span style='color:white;'>"
                            "<b>📤 DESPESA — %{customdata[0]}</b><br>"
                            "Fonte: %{customdata[0]}<br>"
                            "Estágio: %{customdata[1]}<br>"
                            "Detalhe: %{customdata[2]}<br>"
                            "──────────────────<br>"
                            "Valor: <b>%{customdata[3]}</b><br>"
                            "Total Despesas: %{customdata[4]}<br>"
                            "Participação: %{customdata[5]}"
                            "</span><extra></extra>"
                        ),
                    ),
                    row=1, col=2
                )

            fig_rd.update_layout(
                separators=",.",
                barmode='stack',
                hoverlabel=HOVER_STYLE,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                height=480,
            )
            fig_rd.update_yaxes(showticklabels=False)

        else:  # MENSAL
            from plotly.subplots import make_subplots

            fig_rd = make_subplots(
                rows=1, cols=2,
                subplot_titles=["Receitas FUNDEB por Mês", "Despesas FUNDEB por Mês (Liquidado)"],
                horizontal_spacing=0.08
            )

            COR_REC  = {'Principal':'#002147', 'VAAR':'#003366', 'ETI':'#00509d', 'Aplicação':'#6699cc'}
            COR_DESP = {'FUNDEB 70%':'#660000', 'FUNDEB 30%':'#cc0000'}

            categorias_rec  = list(df_r_fundeb['Subcategoria'].unique())
            fontes_desp     = ['FUNDEB 70%', 'FUNDEB 30%']
            legendas_usadas = set()

            for m in meses_disponiveis:
                tot_rec_m  = obter_soma_mensal_robusta(df_r_fundeb, [m])
                tot_desp_m = obter_soma_mensal_robusta(df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado'], [m])

                for cat in categorias_rec:
                    val = obter_soma_mensal_robusta(df_r_fundeb[df_r_fundeb['Subcategoria'] == cat], [m])
                    desc_list = df_r_fundeb[df_r_fundeb['Subcategoria'] == cat]['Descrição da Receita'].unique().tolist()
                    show_leg  = cat not in legendas_usadas
                    legendas_usadas.add(cat)
                    part = f"{(val/tot_rec_m*100):.1f}%" if tot_rec_m > 0 else "—"
                    fig_rd.add_trace(
                        go.Bar(
                            name=cat,
                            x=[m],
                            y=[val],
                            marker_color=COR_REC.get(cat, '#336699'),
                            legendgroup=cat,
                            showlegend=show_leg,
                            customdata=[[
                                cat, "FUNDEB", " | ".join(desc_list),
                                formar_real(val), formar_real(tot_rec_m), part, m,
                            ]],
                            hovertemplate=(
                                "<span style='color:white;'>"
                                "<b>📥 %{customdata[6]} — %{customdata[0]}</b><br>"
                                "Categoria: %{customdata[0]}<br>"
                                "Fundo: %{customdata[1]}<br>"
                                "Rubricas: %{customdata[2]}<br>"
                                "──────────────────<br>"
                                "Valor: <b>%{customdata[3]}</b><br>"
                                "Total Rec. mês: %{customdata[4]}<br>"
                                "Participação: %{customdata[5]}"
                                "</span><extra></extra>"
                            ),
                        ),
                        row=1, col=1
                    )

                for fonte in fontes_desp:
                    val = obter_soma_mensal_robusta(
                        df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & (df_df_fundeb['Tipo'] == 'Liquidado')], [m]
                    )
                    show_leg = fonte not in legendas_usadas
                    legendas_usadas.add(fonte)
                    prop = f"{(val/tot_desp_m*100):.1f}%" if tot_desp_m > 0 else "—"
                    fig_rd.add_trace(
                        go.Bar(
                            name=fonte,
                            x=[m],
                            y=[val],
                            marker_color=COR_DESP.get(fonte, '#990000'),
                            legendgroup=fonte,
                            showlegend=show_leg,
                            customdata=[[
                                fonte, "Liquidado",
                                f"{prop} do total de despesas do mês",
                                formar_real(val), formar_real(tot_desp_m), prop, m,
                            ]],
                            hovertemplate=(
                                "<span style='color:white;'>"
                                "<b>📤 %{customdata[6]} — %{customdata[0]}</b><br>"
                                "Fonte: %{customdata[0]}<br>"
                                "Estágio: %{customdata[1]}<br>"
                                "Detalhe: %{customdata[2]}<br>"
                                "──────────────────<br>"
                                "Valor: <b>%{customdata[3]}</b><br>"
                                "Total Desp. mês: %{customdata[4]}<br>"
                                "Participação: %{customdata[5]}"
                                "</span><extra></extra>"
                            ),
                        ),
                        row=1, col=2
                    )

            fig_rd.update_layout(
                separators=",.",
                barmode='stack',
                hoverlabel=HOVER_STYLE,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                height=480,
            )
            fig_rd.update_yaxes(showticklabels=False)

        st.plotly_chart(fig_rd, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

        # ── GRÁFICO 2 — COMPARATIVO ÍNDICE 70% ───────────────────────────────
        st.subheader("🔹 2. Comparativo de Aplicação (Índice 70%)")
        tipo_comp = st.segmented_control(
            "Visualização Comparativo:", ["Total Acumulado", "Mensal"],
            default="Mensal", key="comp_btn_f"
        )
        
        if tipo_comp == "Total Acumulado":
            df_c = pd.DataFrame({
                "Tipo":  ["Receita Total", "Despesas (70%)"],
                "Valor": [tot_rec_periodo, desp_70_val],
                "Texto": ["", f"{perc_70_indice:.2f}%"]
            })
            fig_comp = px.bar(df_c, x='Tipo', y='Valor', color='Tipo', text='Texto',
                              color_discrete_map={"Receita Total": "#003366", "Despesas (70%)": "#660000"})
            fig_comp.add_hline(y=tot_rec_periodo * 0.7, line_dash="dot", line_color="green",
                               annotation_text="Meta 70%")
        else:
            dados_c = []
            for m in meses_disponiveis:
                r_m = obter_soma_mensal_robusta(df_r_fundeb, [m])
                d_m = obter_soma_mensal_robusta(
                    df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & (df_df_fundeb['Tipo'] == 'Liquidado')], [m]
                )
                p_m = (d_m / r_m * 100) if r_m > 0 else 0
                dados_c.append({"Mês": m, "Tipo": "Receita Total",  "Valor": r_m, "Texto": ""})
                dados_c.append({"Mês": m, "Tipo": "Despesas (70%)", "Valor": d_m, "Texto": f"{p_m:.2f}%"})
            
            fig_comp = px.bar(pd.DataFrame(dados_c), x='Mês', y='Valor', color='Tipo',
                              barmode='group', text='Texto',
                              color_discrete_map={"Receita Total": "#003366", "Despesas (70%)": "#660000"},
                              category_orders={"Mês": ORDEM_MESES})
            
            df_l = pd.DataFrame([
                {"Mês": m, "Meta": obter_soma_mensal_robusta(df_r_fundeb, [m]) * 0.7}
                for m in meses_disponiveis
            ])
            fig_comp.add_trace(go.Scatter(
                x=df_l['Mês'], y=df_l['Meta'],
                mode='lines+markers', name='Meta 70%',
                line=dict(color='green', dash='dot')
            ))

        fig_comp.update_traces(
            selector=dict(type='bar'),
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}"
        )
        fig_comp.update_layout(
            separators=",.",
            yaxis_title="Valor (R$)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_comp, use_container_width=True, config=CONFIG_PT)
        
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