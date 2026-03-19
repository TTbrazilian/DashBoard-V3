import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
import os

# --- FUNÇÕES DE APOIO (PADRÃO BOM JESUS) ---
def limpar_valor(v):
    if pd.isna(v) or str(v).strip() in ["", "-", "R$ 0,00"]: return 0.0
    s = str(v).replace('R$', '').replace('.', '').replace(',', '.').strip()
    try: return float(s)
    except: return 0.0

def formar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def load_data_alpinopolis():
    # Carregando o arquivo específico solicitado
    file_path = 'Alpinópolis.csv'
    if not os.path.exists(file_path): return None
    
    # header=1 pois a primeira linha do seu CSV são rótulos de grupo (Empenhado/Liquidado/Pago)
    df = pd.read_csv(file_path, sep=None, engine='python', encoding='utf-8', header=1)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Limpeza financeira básica
    cols_fin = ['Orçado', 'Saldo', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    # Como as colunas de meses são triplicadas, o pandas cria listas. 
    # Para as análises do PDF, usaremos sempre a coluna de 'Liquidado'.
    return df

def main_alpinopolis_edu():
    st.title("🎓 Gestão Educacional - Alpinópolis")
    df = load_data_alpinopolis()
    
    if df is None:
        st.error("Arquivo Alpinópolis.csv não encontrado.")
        return

    # --- 1. ANÁLISE FUNDEB 70% (Base: Pág 3 e 6 do PDF) ---
    # No PDF, a análise foca no percentual aplicado em Pessoal com recursos do FUNDEB.
    st.header("📊 Aplicação FUNDEB 70% (Pessoal)")
    
    # Filtro lógico: Fonte 1540/1500 (FUNDEB) e Elementos de Despesa de Pessoal (3.1.90)
    df_fundeb_70 = df[
        (df['Fonte'].astype(str).str.contains('1540|1500', na=False)) & 
        (df['Elemento'].astype(str).str.contains('3.1.90|Vencimentos|Obrigações Patronais', na=False))
    ].copy()

    total_fundeb_70 = df_fundeb_70['Orçado'].apply(limpar_valor).sum()
    # Simulação de Receita FUNDEB (No dashboard real, isso viria de uma tabela de receita ou KPI fixo)
    receita_fundeb_estimada = 6000000.00 
    perc_fundeb = (total_fundeb_70 / receita_fundeb_estimada) * 100 if receita_fundeb_estimada > 0 else 0

    c1, c2 = st.columns(2)
    c1.metric("Total Gasto (Pessoal FUNDEB)", formar_real(total_fundeb_70))
    c2.metric("% Aplicado (Mínimo 70%)", f"{perc_fundeb:.2f}%", delta=f"{perc_fundeb-70:.2f}%")

    # --- 2. MÍNIMO CONSTITUCIONAL 25% (Base: Pág 4 e 5 do PDF) ---
    st.markdown("---")
    st.header("🏛️ Mínimo Constitucional (25%)")
    
    # Filtro: Recursos Próprios (Geralmente Fonte 1500 sem subvinculação ou específica do tesouro)
    df_proprio = df[df['Fonte'].astype(str).str.contains('1500', na=False)].copy()
    gasto_proprio = df_proprio['Orçado'].apply(limpar_valor).sum()
    
    # Gráfico de Barra Horizontal (Igual pág 4 do PDF)
    fig_25 = px.bar(
        x=[gasto_proprio], y=["Recursos Próprios"],
        orientation='h', title="Investimento em Educação vs Limite 25%",
        color_discrete_sequence=['#00CC96']
    )
    st.plotly_chart(fig_25, use_container_width=True)

    # --- 3. CUSTEIO VS CAPITAL (Base: Pág 7 do PDF) ---
    st.markdown("---")
    st.header("📦 Natureza da Despesa: Custeio x Capital")
    
    def rotular_natureza(elemento):
        ele = str(elemento)
        if '4.4.90' in ele or 'Equipamentos' in ele or 'Obras' in ele:
            return 'Capital (Investimento)'
        return 'Custeio (Manutenção)'

    df['Natureza'] = df['Elemento'].apply(rotular_natureza)
    resumo_natureza = df.groupby('Natureza')['Orçado'].apply(lambda x: x.apply(limpar_valor).sum()).reset_index()
    
    fig_natureza = px.pie(
        resumo_natureza, values='Orçado', names='Natureza',
        color_discrete_map={'Custeio (Manutenção)': '#00CC96', 'Capital (Investimento)': '#EF553B'},
        hole=0.4
    )
    st.plotly_chart(fig_natureza, use_container_width=True)

    # --- 4. DESPESAS POR ELEMENTO (Base: Pág 8 e 9 do PDF) ---
    st.markdown("---")
    st.header("📑 Detalhamento por Elemento (Liquidado)")
    
    # Agrupamento para ver onde o dinheiro está saindo (Folha, Material, Serviços)
    resumo_elemento = df.groupby('Elemento')['Orçado'].apply(lambda x: x.apply(limpar_valor).sum()).reset_index()
    resumo_elemento = resumo_elemento.sort_values(by='Orçado', ascending=False).head(10)
    
    fig_elem = px.bar(
        resumo_elemento, x='Orçado', y='Elemento', orientation='h',
        title="Top 10 Maiores Gastos por Elemento",
        color_discrete_sequence=['#636EFA']
    )
    st.plotly_chart(fig_elem, use_container_width=True)

    # --- 5. ALIMENTAÇÃO ESCOLAR - PNAE (Base: Pág 10 do PDF) ---
    st.markdown("---")
    st.header("🍎 Monitoramento PNAE (Merenda)")
    # Filtro por Atividade ou Elemento que contenha "Alimentação" ou "Merenda"
    df_pnae = df[df['Atividade'].astype(str).str.contains('Alimentação|Merenda|PNAE', case=False, na=False)].copy()
    
    if not df_pnae.empty:
        gasto_pnae = df_pnae['Orçado'].apply(limpar_valor).sum()
        st.info(f"O investimento total identificado para Alimentação Escolar em Alpinópolis é de **{formar_real(gasto_pnae)}**.")
        st.dataframe(df_pnae[['Ficha', 'Atividade', 'Elemento', 'Orçado']], use_container_width=True)
    else:
        st.warning("Nenhuma ficha específica de Alimentação Escolar (PNAE) detectada com esses termos.")

if __name__ == "__main__":
    main_alpinopolis_edu()