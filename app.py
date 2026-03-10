import streamlit as st
import pandas as pd
import plotly.express as px
import os
import unicodedata


st.set_page_config(page_title="Gestão de Recursos - Bom Jesus", layout="wide")

#Unicodedata
def remover_acentos(texto):
    return "".join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower()

def quebrar_texto(texto, limite=15): # Limite menor para garantir a quebra
    texto = str(texto)
    if len(texto) <= limite: return texto
    palavras = texto.split()
    linhas, linha_atual = [], ""
    for palavra in palavras:
        if len(linha_atual) + len(palavra) <= limite:
            linha_atual += (palavra + " ")
        else:
            linhas.append(linha_atual.strip())
            linha_atual = palavra + " "
    linhas.append(linha_atual.strip())
    # Para o GRÁFICO usamos \n, para a TABELA vamos usar uma lógica diferente
    return "\n".join(linhas)

# --- FUNÇÕES DE LIMPEZA E FORMATAÇÃO ---
def limpar_valor(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "-", "R$ 0,00", "0"]: 
        return 0.0
    s_valor = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try: return float(s_valor)
    except: return 0.0

def formar_real(valor):
    """Transforma 17000.0 em R$ 17.000,00"""
    if valor is None:
        return "R$ 0,00"
    # Formata com padrão americano primeiro: 17,000.00
    a_la_us = f"{valor:,.2f}"
    # Inverte os sinais: virgula vira ponto, ponto vira virgula
    a_la_br = a_la_us.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {a_la_br}"

@st.cache_data
def load_data():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(diretorio_atual, 'fichas.csv')
    if not os.path.exists(caminho): return None

    # Lendo o CSV (Cabeçalho na linha 1 conforme o padrão da sua planilha)
    df = pd.read_csv(caminho, sep=None, engine='python', encoding='utf-8', header=1)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Limpar colunas financeiras (Orçado, Saldo e meses)
    cols_para_limpar = ['Orçado', 'Saldo', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho']
    for col in df.columns:
        if any(k in col for k in cols_para_limpar):
            df[col] = df[col].apply(limpar_valor)
    return df

# --- INTERFACE ---
st.title("📊Bom Jesus da Penha - Saúde")
st.markdown("---")

df_raw = load_data()

df_raw = load_data()

if df_raw is not None:
    # DEFINIMOS O DF_PLOT AQUI PARA ELE EXISTIR NO CÓDIGO TODO
    df_plot = df_raw.copy() 
    
    # ... (aqui continua seu código de filtros, sidebar, etc)

if df_raw is not None:
    # Sidebar
    st.sidebar.header("🔍 Filtros")
    busca = st.sidebar.text_input("Filtrar Fichas/Categorias:")
    df = df_raw.copy()
    if busca:
        mask = df.astype(str).apply(lambda x: x.str.contains(busca, case=False)).any(axis=1)
        df = df[mask]

    # --- KPIs NO TOPO ---
    orcado_total = df['Orçado'].sum()
    saldo_total = df['Saldo'].sum()
    executado = orcado_total - saldo_total
    perc_exec = (executado / orcado_total * 100) if orcado_total > 0 else 0

    # KPIs
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Previsão (Orçado)", formar_real(orcado_total))
    
    with c2:
        st.metric("Saldo Disponível", formar_real(saldo_total))
        
    with c3:
        st.metric("Executado (Liquidado)", formar_real(executado))

    with c4:
        st.metric("% de Execução", f"{perc_exec:.2f}%".replace('.', ','))

    # --- ANÁLISE 2: EVOLUÇÃO MENSAL (Foco da Apresentação) ---
    st.subheader("📈 Evolução Mensal da Execução")
    
    # Vamos somar os meses (considerando que sua planilha tem colunas Janeiro, Fevereiro...)
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho']
    mensal_dados = []
    for mes in meses:
        if mes in df.columns:
            # Pegamos o valor da coluna 'Liquidado' do mês se existir, ou a soma da coluna do mês
            valor_mes = df[mes].sum()
            mensal_dados.append({"Mês": mes, "Valor": valor_mes})
    
    df_mensal = pd.DataFrame(mensal_dados)
    fig_evolucao = px.line(df_mensal, x='Mês', y='Valor', markers=True, 
                           title="Gastos Totais por Mês (R$)",
                           line_shape="spline", color_discrete_sequence=["#00CC96"])
    fig_evolucao.update_layout(yaxis_tickprefix='R$ ', yaxis_tickformat=',.2f')
    st.plotly_chart(fig_evolucao, use_container_width=True)

# --- ANÁLISE 3: NAVEGAÇÃO POR ELEMENTOS (BOTÕES) ---
    st.markdown("---")
    st.subheader("📦 Detalhamento por Elemento")

    # --- CSS HACK PARA ANIMAÇÃO BARRA POR BARRA (ESTILO LOVABLE) ---
    st.markdown("""
        <style>
        @keyframes barraSobe {
            from { opacity: 0; transform: scaleY(0); transform-origin: bottom; }
            to { opacity: 1; transform: scaleY(1); transform-origin: bottom; }
        }
        /* Seleciona as barras do Plotly e aplica animação sequencial */
        .js-plotly-plot .point path {
            animation: barraSobe 0.8s cubic-bezier(0.45, 0.05, 0.55, 0.95) forwards;
            opacity: 0;
        }
        /* Delays para as primeiras 10 barras (efeito cascata) */
        .js-plotly-plot .point path:nth-child(1) { animation-delay: 0.1s; }
        .js-plotly-plot .point path:nth-child(2) { animation-delay: 0.2s; }
        .js-plotly-plot .point path:nth-child(3) { animation-delay: 0.3s; }
        .js-plotly-plot .point path:nth-child(4) { animation-delay: 0.4s; }
        .js-plotly-plot .point path:nth-child(5) { animation-delay: 0.5s; }
        .js-plotly-plot .point path:nth-child(6) { animation-delay: 0.6s; }
        .js-plotly-plot .point path:nth-child(7) { animation-delay: 0.7s; }
        .js-plotly-plot .point path:nth-child(8) { animation-delay: 0.8s; }
        </style>
    """, unsafe_allow_html=True)

    df_busca = df_raw.copy()
    if busca:
        busca_limpa = remover_acentos(busca)
        mask = df_busca.apply(lambda row: busca_limpa in remover_acentos(row.values), axis=1)
        df_busca = df_busca[mask]

    elementos_disponiveis = sorted([str(x) for x in df_busca['Elemento'].dropna().unique()])

    if elementos_disponiveis:
        st.write("Selecione um elemento para visualizar o detalhamento:")
        cols_botoes = st.columns(4) 
        
        for i, elemento in enumerate(elementos_disponiveis):
            with cols_botoes[i % 4]:
                if st.button(elemento, use_container_width=True, key=f"btn_{i}"):
                    st.session_state['elemento_ativo'] = elemento

        if 'elemento_ativo' in st.session_state:
            ele = st.session_state['elemento_ativo']
            df_detalhe = df_busca[df_busca['Elemento'] == ele].sort_values('Orçado', ascending=False)
            
            # Título limpo
            st.subheader(f"📊 Detalhamento de Fichas: {ele}")
            
            fig_detalhe = px.bar(
                df_detalhe,
                x='Ficha',
                y='Orçado',
                text='Orçado',
                color_discrete_sequence=["#00CC96"],
                hover_name='Elemento'
            )

            # Mantendo seu design da foto
            fig_detalhe.update_traces(
                hovertemplate="<b>%{hovertext}</b><extra></extra>",
                texttemplate='R$ %{text:,.2f}', 
                textposition='outside',
                cliponaxis=False,
                marker_line_width=0,
                width=0.8 if len(df_detalhe) < 12 else 0.5
            )

            fig_detalhe.update_layout(
                xaxis_type='category',
                yaxis_title="Valor Orçado (R$)",
                xaxis_title="Número da Ficha",
                height=550,
                yaxis=dict(range=[0, df_detalhe['Orçado'].max() * 1.25]),
                margin=dict(t=50, b=50, l=50, r=50),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )

            # Renderiza o gráfico. O CSS acima vai cuidar de animar as barras uma a uma.
            st.plotly_chart(fig_detalhe, use_container_width=True, theme=None)
            
            if st.button("⬅️ Voltar para Visão Geral"):
                del st.session_state['elemento_ativo']
                st.rerun()
    else:
        st.info("Nenhum elemento encontrado.")
    # --- ANÁLISE 4: TABELA DETALHADA ---
    st.subheader("📋 Detalhamento das Fichas (Estilo Relatório)")
    df_tab = df[['Categoria', 'Ficha', 'Elemento', 'Fonte', 'Orçado', 'Saldo']].copy()
    df_tab['Orçado'] = df_tab['Orçado'].apply(formar_real)
    df_tab['Saldo'] = df_tab['Saldo'].apply(formar_real)
    st.dataframe(df_tab, use_container_width=True, hide_index=True)

else:
    st.error("Arquivo 'fichas.csv' não encontrado!")

# --- ANÁLISE 5: RELATÓRIO TÉCNICO DE FICHAS ---
    st.markdown("---")
    st.subheader("📋 Relatório Detalhado (Estilo Relatório)")

    df_relatorio = df_plot.copy()
    
    # 1. Limpamos qualquer tentativa de HTML que possa bugar o editor
    df_relatorio['Elemento'] = df_relatorio['Elemento'].astype(str)

    # 2. Formatamos os valores (sem mexer na estrutura do texto)
    if 'Orçado' in df_relatorio.columns:
        df_relatorio['Orçado'] = df_relatorio['Orçado'].apply(formar_real)
    if 'Saldo' in df_relatorio.columns:
        df_relatorio['Saldo'] = df_relatorio['Saldo'].apply(formar_real)

    # 3. O PULO DO GATO: Usar o data_editor com Wrap de texto ativado
    # Nota: O Streamlit lançou recentemente o suporte a wrap em TextColumn!
    st.data_editor(
        df_relatorio[['Categoria', 'Ficha', 'Elemento', 'Fonte', 'Orçado', 'Saldo']],
        use_container_width=True,
        hide_index=True,
        disabled=True,
        column_config={
            "Elemento": st.column_config.TextColumn(
                "Elemento",
                width="large",  # Deixa a coluna bem larga
                help="Nome completo do elemento"
            ),
            "Categoria": st.column_config.TextColumn("Categoria", width="medium"),
            "Ficha": st.column_config.NumberColumn("Ficha", format="%d"),
        },
    )
    st.info("💡 **Dica:** Você pode esticar a largura das colunas clicando e arrastando na divisória do cabeçalho.")
    # --- ANÁLISE 6: RAIO-X DE MAIORES GASTOS (TOP 10) ---
    st.markdown("---")
    st.subheader("🔍 Raio-X: Maiores Investimentos")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        df_top10 = df_plot.groupby('Elemento')['Orçado'].sum().nlargest(10).reset_index()
        
        # Aplicamos a quebra com \n para o eixo do gráfico
        df_top10['Elemento_Q'] = df_top10['Elemento'].apply(lambda x: quebrar_texto(x, 15))
        
        fig_top = px.bar(
            df_top10, 
            x='Orçado', 
            y='Elemento_Q', 
            orientation='h', 
            color_discrete_sequence=["#EF553B"],
            text_auto='.2s' # Adiciona o valor resumido dentro da barra para ajudar
        )
        
        fig_top.update_layout(
            xaxis_tickprefix='R$ ', 
            xaxis_tickformat=',.2f',
            separators=',.', 
            yaxis_title="", 
            xaxis_title="Valor Acumulado",
            margin=dict(l=200, r=50, t=50, b=50),
            # Truque para o Plotly aceitar o \n:
            yaxis={'type': 'category', 'automargin': True} 
        )
        
        fig_top.update_yaxes(autorange="reversed") 
        st.plotly_chart(fig_top, use_container_width=True)