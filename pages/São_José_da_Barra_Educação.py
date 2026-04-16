import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="São José da Barra - Gestão Educação", layout="wide")

# --- ESTILIZAÇÃO E GRADE PADRONIZADA ---
st.markdown(
    """
    <style>
        /* Ocultar outras cidades na navegação */
        [data-testid="stSidebarNav"] ul li:has(span:contains("Ibiraci")),
        [data-testid="stSidebarNav"] ul li:has(span:contains("Cássia")),
        [data-testid="stSidebarNav"] ul li:has(span:contains("Bom Jesus")),
        [data-testid="stSidebarNav"] ul li:has(span:contains("Penha")) {
            display: none !important;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(20px); }
            to { opacity: 1; transform: translateX(0); }
        }

        .stButton button {
            width: 100% !important;
            height: 45px !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            border-radius: 4px !important;
            animation: slideIn 0.4s ease-out;
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
    mapeamento = {"IMPOSTO": "IMP.", "PROPRIEDADE": "PROP.", "CONTRIBUIÇÃO": "CONTRIB.", "COTA-PARTE": "COTA"}
    for longo, curto in mapeamento.items(): n = n.replace(longo, curto)
    return n[:15]

def buscar_arquivo(nome):
    caminhos = [nome, os.path.join("zEducação", nome), os.path.join("..", nome)]
    for p in caminhos:
        if os.path.exists(p): return p
    return None

@st.cache_data
def load_all_data():
    arquivo_f = "São José da Barra.csv"
    arquivo_r = "São José da Barra_R.csv"
    arquivo_df = "São José da Barra_DF.csv"
    
    path_f, path_r, path_df = buscar_arquivo(arquivo_f), buscar_arquivo(arquivo_r), buscar_arquivo(arquivo_df)
    if not path_f or not path_r or not path_df: return None, None, None
    
    # Fichas (Multilevel Header)
    df_f = pd.read_csv(path_f, sep=None, engine='python', encoding='utf-8', header=[0, 1])
    new_cols = []
    for col in df_f.columns:
        if "Unnamed" in col[0]: new_cols.append(col[1].strip())
        else: new_cols.append(f"{col[1].strip()}_{col[0].strip()}")
    df_f.columns = new_cols
    
    # Receitas e Despesas Consolidadas
    df_r = pd.read_csv(path_r, sep=None, engine='python', encoding='utf-8')
    df_df = pd.read_csv(path_df, sep=None, engine='python', encoding='utf-8')
    
    meses_limpeza = ORDEM_MESES + [m.lower() for m in ORDEM_MESES] + ['Total', 'TOTAL', 'Orçado', 'Orçado Receitas']
    
    for df in [df_f, df_r, df_df]:
        df.columns = [str(c).strip() for c in df.columns]
        for col in df.columns:
            if any(k in col for k in meses_limpeza + ['Saldo', 'Liquidado', 'Empenhado', 'Pago']):
                df[col] = df[col].apply(limpar_valor)
                
    return df_f, df_r, df_df

df_f_raw, df_r, df_df_raw = load_all_data()
meses_disponiveis = ['Janeiro', 'Fevereiro'] # Ajustável conforme novos dados entrarem

if df_f_raw is not None:
    # --- SIDEBAR ---
    st.sidebar.title("🔍 São José da Barra")
    search_term = st.sidebar.text_input("Filtrar Fichas:", "")
    st.sidebar.markdown("---")
    if st.sidebar.button("FUNDEB", use_container_width=True): st.session_state.setor = 'FUNDEB'
    if st.sidebar.button("Recursos Próprios (25%)", use_container_width=True): st.session_state.setor = 'Recursos Próprios'
    if st.sidebar.button("Recursos Vinculados", use_container_width=True): st.session_state.setor = 'Recursos Vinculados'

    # --- LÓGICA DE SETORES ---
    if st.session_state.setor == 'FUNDEB':
        st.header("📖 FUNDEB - São José da Barra")
        
        df_r_fundeb = df_r[df_r['Categoria'].str.contains('FUNDEB', na=False)].copy()
        tot_prev = df_r_fundeb['Orçado Receitas'].sum()
        tot_rec = df_r_fundeb[meses_disponiveis].sum().sum()
        
        # Filtro de despesa para SJB: Fonte 1540
        df_df_fundeb = df_df_raw[df_df_raw['Fonte'].astype(str).str.contains('1540', na=False)].copy()
        desp_70 = df_df_fundeb[(df_df_raw['Nomenclatura'].str.contains('70%', na=False)) & (df_df_raw['Tipo'] == 'Liquidado')][meses_disponiveis].sum().sum()
        
        perc_70 = (desp_70 / tot_rec * 100) if tot_rec > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Previsão Orçamentária", formar_real(tot_prev))
        m2.metric("Total Arrecadado", formar_real(tot_rec))
        m3.metric("Índice 70% (Pessoal)", f"{perc_70:.2f}%", delta=f"{perc_70-70:.2f}%")

        # Gráfico FUNDEB
        dados_r = []
        for m in meses_disponiveis:
            for cat in ['Principal', 'VAAR', 'ETI']:
                val = df_r_fundeb[df_r_fundeb['Descrição da Receita'].str.contains(cat, case=False, na=False)][m].sum()
                dados_r.append({"Mês": m, "Categoria": cat, "Valor": val})
        
        fig = px.bar(pd.DataFrame(dados_r), x='Mês', y='Valor', color='Categoria', barmode='stack', text_auto='.2s',
                     color_discrete_map={'Principal':'#002147', 'VAAR':'#00509d', 'ETI':'#6699cc'})
        st.plotly_chart(fig, use_container_width=True, config=CONFIG_PT)

    elif st.session_state.setor == 'Recursos Próprios':
        st.header("📖 Recursos Próprios (25%)")
        
        df_r_base = df_r[df_r['Categoria'].str.strip().isin(['Impostos', 'Cota-Parte'])].copy()
        df_r_ded = df_r[df_r['Categoria'].str.contains('Dedução', case=False, na=False)].copy()
        df_df_25 = df_df_raw[(df_df_raw['Fonte'].astype(str).str.contains('1500', na=False)) & (df_df_raw['Tipo'] == 'Liquidado')].copy()

        total_base = df_r_base[meses_disponiveis].sum().sum()
        total_desp = df_df_25[meses_disponiveis].sum().sum()
        total_ded = abs(df_r_ded[meses_disponiveis].sum().sum())
        
        indice = ((total_desp + total_ded) / total_base * 100) if total_base > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Receita Base (Impostos)", formar_real(total_base))
        m2.metric("Deduções FUNDEB", formar_real(total_ded))
        m3.metric("Índice de Aplicação", f"{indice:.2f}%", delta=f"{indice-25:.2f}%")
        
        fig_rp = px.bar(x=['Receita Base', 'Aplicação (Desp + Ded)'], y=[total_base, total_desp + total_ded], 
                        color=['Receita', 'Aplicação'], color_discrete_map={'Receita':'#003366', 'Aplicação':'#27ae60'})
        st.plotly_chart(fig_rp, use_container_width=True)

    elif st.session_state.setor == 'Recursos Vinculados':
        st.header("📖 Recursos Vinculados")
        # Mapeamento de fontes comum para SJB
        vinc_map = {'PNAE': '1552', 'PNATE': '1553', 'PTE': '1576', 'QESE': '1550'}
        
        for nome, fonte in vinc_map.items():
            with st.expander(f"📊 Detalhes: {nome} (Fonte {fonte})"):
                rec = df_r[df_r['Descrição da Receita'].str.contains(nome, case=False, na=False)][meses_disponiveis].sum().sum()
                desp = df_df_raw[(df_df_raw['Fonte'].astype(str).str.contains(fonte)) & (df_df_raw['Tipo'] == 'Liquidado')][meses_disponiveis].sum().sum()
                
                c1, c2 = st.columns(2)
                c1.metric("Arrecadado", formar_real(rec))
                c2.metric("Liquidado", formar_real(desp))
                
                fig_v = px.area(x=meses_disponiveis, y=[rec, desp], title=f"Fluxo {nome}")
                st.plotly_chart(fig_v, use_container_width=True)

    # --- TABELA DE FICHAS ---
    st.markdown("---")
    st.subheader("📋 Relatório de Fichas - Detalhado")
    df_f_filt = df_f_raw[df_f_raw['Atividade'].str.contains(search_term, na=False, case=False)].copy()
    st.dataframe(df_f_filt, use_container_width=True, hide_index=True)

else:
    st.error("Erro: Arquivos de São José da Barra não encontrados na pasta zEducação.")