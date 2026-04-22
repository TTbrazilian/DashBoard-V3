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

# Tema padrão 'plotly_dark'
pio.templates.default = "plotly_dark"
CONFIG_PT = {'displaylogo': False, 'showTips': False}
HOVER_STYLE = dict(bgcolor="rgba(0,0,0,0.9)", font_size=13, font_family="Arial", font_color="white")

# ORDEM CRONOLÓGICA DOS MESES
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
    # AJUSTADO PARA OS ARQUIVOS DE SÃO ROQUE DE MINAS
    arquivo_f = "zEducação/São Roque de Minas.csv"
    arquivo_r = "zEducação/São Roque de Minas_R.csv"
    arquivo_df = "zEducação/São Roque de Minas_DF.csv"
    
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
        st.markdown("<h1 style='text-align: left;'>📖 São Roque de Minas - FUNDEB</h1>", unsafe_allow_html=True)
        
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

        # 2. PROCESSAMENTO DE DADOS (RECEITAS)
        df_r_fundeb = df_r[df_r['Categoria'].str.strip() == 'FUNDEB'].copy()
        df_r_fundeb['Subcategoria'] = df_r_fundeb['Descrição da Receita'].apply(cat_receita)
        
        # Filtra apenas a linha do Principal para pegar o valor orçado correto
        df_principal = df_r_fundeb[df_r_fundeb['Subcategoria'] == 'Principal']
        tot_prev_2026 = df_principal['Orçamento Receitas'].sum()
        
        tot_rec_periodo = obter_soma_mensal_robusta(df_r_fundeb, meses_disponiveis)

        # 3. PROCESSAMENTO DE DADOS (DESPESAS)
        # Ajustado para São Roque de Minas: Filtrando pela nomenclatura FUNDEB no arquivo DF
        df_df_fundeb = df_df_raw[df_df_raw['Nomenclatura'].str.contains('FUNDEB', na=False)].copy()
        df_df_fundeb['Fonte_Nome'] = df_df_fundeb['Nomenclatura'].str.strip()
        
        desp_70_val = obter_soma_mensal_robusta(
            df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & (df_df_fundeb['Tipo'] == 'Liquidado')],
            meses_disponiveis
        )
        
        perc_70_indice = (desp_70_val / tot_rec_periodo * 100) if tot_rec_periodo > 0 else 0

        # 4. MÉTRICAS (CARDS)
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Previsão Orçamentária 2026", formar_real(tot_prev_2026))
        with m2: st.metric(f"Total Arrecadado ({meses_disponiveis[0]}-{meses_disponiveis[-1]})", formar_real(tot_rec_periodo))
        with m3:
            metric_contabil("Aplicação em Pessoal (Mín. 70%)", perc_70_indice, 70.0)

        st.markdown("---")

        # 5. GRÁFICO DE RECEITAS
        st.subheader("🔹 1. Receitas FUNDEB")
        tipo_r = st.segmented_control("Visualização Receita:", ["Acumulado", "Mensal"], default="Mensal", key="r_btn_f")
        
        if tipo_r == "Acumulado":
            df_r_plot = df_r_fundeb.groupby('Subcategoria').apply(lambda x: obter_soma_mensal_robusta(x, meses_disponiveis)).reset_index()
            df_r_plot.columns = ['Categoria', 'Valor']
            fig_r = px.bar(df_r_plot, x='Categoria', y='Valor', color='Categoria', text_auto='.2s',
                          color_discrete_map={'Principal':'#002147', 'VAAR':'#003366', 'ETI':'#00509d', 'Aplicação':'#6699cc'})
        else:
            dados_m_r = []
            for m in meses_disponiveis:
                for cat in df_r_fundeb['Subcategoria'].unique():
                    val = obter_soma_mensal_robusta(df_r_fundeb[df_r_fundeb['Subcategoria'] == cat], [m])
                    dados_m_r.append({"Mês": m, "Categoria": cat, "Valor": val})
            fig_r = px.bar(pd.DataFrame(dados_m_r), x='Mês', y='Valor', color='Categoria', text_auto='.2s', barmode='stack',
                          color_discrete_map={'Principal':'#002147', 'VAAR':'#003366', 'ETI':'#00509d', 'Aplicação':'#6699cc'},
                          category_orders={"Mês": ORDEM_MESES})
        
        fig_r.update_layout(separators=",.", yaxis_title="Valor (R$)")
        fig_r.update_traces(hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>", hoverlabel=HOVER_STYLE)
        st.plotly_chart(fig_r, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

        # 6. GRÁFICO DE DESPESAS
        st.subheader("🔹 2. Despesas FUNDEB")
        tipo_f = st.segmented_control("Visualização Despesa:", ["Acumulado", "Mensal"], default="Mensal", key="f_btn_f")
        
        if tipo_f == "Acumulado":
            total_desp_acum = obter_soma_mensal_robusta(df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado'], meses_disponiveis)
            df_f_plot = []
            for fonte in ['FUNDEB 70%', 'FUNDEB 30%']:
                val = obter_soma_mensal_robusta(df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & (df_df_fundeb['Tipo'] == 'Liquidado')], meses_disponiveis)
                prop = (val / total_desp_acum * 100) if total_desp_acum > 0 else 0
                df_f_plot.append({"Fonte": fonte, "Valor": val, "Proporção": f"{prop:.2f}%"})
            fig_f = px.bar(pd.DataFrame(df_f_plot), x='Fonte', y='Valor', color='Fonte', text_auto='.2s',
                          custom_data=['Proporção'], color_discrete_map={'FUNDEB 70%':'#660000', 'FUNDEB 30%':'#cc0000'})
        else:
            dados_m_f = []
            for m in meses_disponiveis:
                total_mes = obter_soma_mensal_robusta(df_df_fundeb[df_df_fundeb['Tipo'] == 'Liquidado'], [m])
                for fonte in ['FUNDEB 70%', 'FUNDEB 30%']:
                    val = obter_soma_mensal_robusta(df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == fonte) & (df_df_fundeb['Tipo'] == 'Liquidado')], [m])
                    prop = (val / total_mes * 100) if total_mes > 0 else 0
                    dados_m_f.append({"Mês": m, "Fonte": fonte, "Valor": val, "Proporção": f"{prop:.2f}%"})
            fig_f = px.bar(pd.DataFrame(dados_m_f), x='Mês', y='Valor', color='Fonte', text_auto='.2s', barmode='stack',
                          custom_data=['Proporção'], color_discrete_map={'FUNDEB 70%':'#660000', 'FUNDEB 30%':'#cc0000'},
                          category_orders={"Mês": ORDEM_MESES})
        
        fig_f.update_layout(separators=",.", yaxis_title="Valor (R$)")
        fig_f.update_traces(hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<br>Prop: %{customdata[0]}<extra></extra>", hoverlabel=HOVER_STYLE)
        st.plotly_chart(fig_f, use_container_width=True, config=CONFIG_PT)

        st.markdown("---")

        # 7. COMPARATIVO (ÍNDICE 70%)
        st.subheader("🔹 3. Comparativo de Aplicação (Índice 70%)")
        tipo_comp = st.segmented_control("Visualização Comparativo:", ["Total Acumulado", "Mensal"], default="Mensal", key="comp_btn_f")
        
        if tipo_comp == "Total Acumulado":
            df_c = pd.DataFrame({
                "Tipo": ["Receita Total", "Despesas (70%)"], 
                "Valor": [tot_rec_periodo, desp_70_val],
                "Texto": ["", f"{perc_70_indice:.2f}%"]
            })
            fig_comp = px.bar(df_c, x='Tipo', y='Valor', color='Tipo', text='Texto',
                              color_discrete_map={"Receita Total": "#003366", "Despesas (70%)": "#660000"})
            fig_comp.add_hline(y=tot_rec_periodo * 0.7, line_dash="dot", line_color="green", annotation_text="Meta 70%")
        else:
            dados_c = []
            for m in meses_disponiveis:
                r_m = obter_soma_mensal_robusta(df_r_fundeb, [m])
                d_m = obter_soma_mensal_robusta(df_df_fundeb[(df_df_fundeb['Fonte_Nome'] == 'FUNDEB 70%') & (df_df_fundeb['Tipo'] == 'Liquidado')], [m])
                p_m = (d_m / r_m * 100) if r_m > 0 else 0
                dados_c.append({"Mês": m, "Tipo": "Receita Total", "Valor": r_m, "Texto": ""})
                dados_c.append({"Mês": m, "Tipo": "Despesas (70%)", "Valor": d_m, "Texto": f"{p_m:.2f}%"})
            
            fig_comp = px.bar(pd.DataFrame(dados_c), x='Mês', y='Valor', color='Tipo', barmode='group', text='Texto',
                              color_discrete_map={"Receita Total": "#003366", "Despesas (70%)": "#660000"},
                              category_orders={"Mês": ORDEM_MESES})
            
            df_l = pd.DataFrame([{"Mês": m, "Meta": obter_soma_mensal_robusta(df_r_fundeb, [m])*0.7} for m in meses_disponiveis])
            fig_comp.add_trace(go.Scatter(x=df_l['Mês'], y=df_l['Meta'], mode='lines+markers', name='Meta 70%', line=dict(color='green', dash='dot')))

        fig_comp.update_traces(selector=dict(type='bar'), textposition='outside', hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}")
        fig_comp.update_layout(separators=",.", yaxis_title="Valor (R$)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_comp, use_container_width=True, config=CONFIG_PT)
