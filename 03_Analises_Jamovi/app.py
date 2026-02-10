import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from scipy import integrate

# --- Configuração Inicial da Página ---
st.set_page_config(page_title="Dashboard PIBIC-EM", layout="wide", page_icon="📊")

# --- Função de Carregamento de Dados ---
@st.cache_data
def load_data():
    try:
        # Obtém o diretório do script atual
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Caminho do arquivo CSV
        csv_path = os.path.join(script_dir, '2025_12_18_participacao_PIBIC-EM_categoria_adm_corrigida_v5.csv')
        # Carregando dados
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("Erro: O arquivo CSV não foi encontrado.")
    st.stop()

# --- Barra Lateral (Sidebar) de Filtros ---
st.sidebar.title("Filtros de Pesquisa")

# Filtro 1: Região
todas_regioes = df['regiao_corrigida'].unique()
regioes_selecionadas = st.sidebar.multiselect("Região Geográfica:", options=todas_regioes, default=todas_regioes)

# Filtro 2: Categoria Administrativa
todas_cats = df['categoria_adm_corrigida'].unique()
cats_selecionadas = st.sidebar.multiselect("Categoria Administrativa:", options=todas_cats, default=todas_cats)

# Filtro 3: Grande Área
todas_areas = df['grande_area - area_macro_CAPES'].unique()
areas_selecionadas = st.sidebar.multiselect("Grande Área:", options=todas_areas, default=todas_areas)

# Aplicar Filtros
df_filtered = df[
    (df['regiao_corrigida'].isin(regioes_selecionadas)) &
    (df['categoria_adm_corrigida'].isin(cats_selecionadas)) &
    (df['grande_area - area_macro_CAPES'].isin(areas_selecionadas))
]

# --- Título Principal ---
st.title(" Adesão dos pesquisadores ao PIBIC-EM") # como diminuir o tamanho da fonte do título?
st.subheader("Análise da participação e recorrência dos pesquisadores no Programa de Iniciação Científica no Ensino Médio do CNPq.")
st.markdown(f"**Amostra:** {df_filtered.shape[0]} pesquisadores selecionados.")
st.markdown(f"**Período Analisado:** 2014-2024")
st.markdown("Este dashboard apresenta uma análise detalhada da participação dos pesquisadores no programa PIBIC-EM, explorando aspectos geopolíticos, de mérito, recorrência e desigualdade. Use os filtros na barra lateral para personalizar a visualização dos dados.")
# Supondo que 'df_filtrado' seja o seu DataFrame com os dados
# Converta o DataFrame para CSV em memória
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(df_filtered)

# Crie o botão de download
st.download_button(
   label="Clique aqui para fazer o download dos dados",
   data=csv,
   file_name='dados_filtrados.csv',
   mime='text/csv',
)
st.markdown("---")

# --- Abas ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Geopolítica & Acesso", 
    "2. Produtividade & Mérito", 
    "3. Recorrência & Permanência",
    "4. Fluxo de Sobrevivência",
    "5. A Anatomia da Desigualdade"
])

# ==============================================================================
# ABA 1: GEOPOLÍTICA (Mantida)
# ==============================================================================
with tab1:
    st.header("Distribuição Espacial e Institucional")

    st.subheader("Mapa de Calor: Pesquisadores por Estado")
    df_estado = df_filtered['uf'].value_counts().reset_index()
    df_estado.columns = ['UF', 'Total']
    fig_map = px.choropleth(
        df_estado,
        geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        locations='UF', featureidkey="properties.sigla",
        color='Total', color_continuous_scale="Viridis", hover_name="UF"
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)


    st.subheader("Por Categoria Administrativa")
    fig_pie = px.pie(df_filtered, names='categoria_adm_corrigida', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_pie, use_container_width=True)
st.markdown("### Detalhamento por Instituição")
top_inst = df_filtered['inst_padronizada'].value_counts().head(15).reset_index()
top_inst.columns = ['Instituição', 'Pesquisadores']
fig_bar = px.bar(top_inst, x='Pesquisadores', y='Instituição', orientation='h', text='Pesquisadores', color='Pesquisadores', color_continuous_scale='Blues')
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_bar, use_container_width=True)

# ==============================================================================
# ABA 2: MÉRITO & PRODUTIVIDADE (Mantida)
# ==============================================================================
with tab2:
    st.header("Análise de Capital Científico (Produtividade)")
    st.info(" **Insight:** Dados estatísticos indicam que o *H-index* não é um preditor determinante para a recorrência no programa, sugerindo que o PIBIC-EM é permeável a diferentes perfis produtivos, embora geograficamente concentrado.")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("Distribuição do H-Index por Região")
        fig_box = px.box(df_filtered, x='regiao_corrigida', y='h_index', color='regiao_corrigida', points="all", title="Dispersão do Índice H por Região")
        st.plotly_chart(fig_box, use_container_width=True)
    with col_m2:
        st.subheader("Produtividade vs. Volume de Produção")
        fig_scatter = px.scatter(df_filtered, x='works_count', y='h_index', color='grande_area - area_macro_CAPES', size='num_chamadas_participou', hover_data=['pesquisador_padronizado', 'inst_padronizada'], title="Relação: Nº de Trabalhos x Índice H (Cor = Área)")
        st.plotly_chart(fig_scatter, use_container_width=True)

# ==============================================================================
# ABA 3: RECORRÊNCIA (Restaurada conforme seu código)
# ==============================================================================
with tab3:
    st.header("Dinâmica de Recorrência nas Chamadas Públicas do PIBIC-EM")
    col_r1, col_r2 = st.columns([1, 2])
    with col_r1:
        st.subheader("Frequência de Retenção")
        fig_hist = px.histogram(df_filtered, x='num_chamadas_participou', nbins=10, text_auto=True, title="Distribuição Geral de Aprovações", labels={'num_chamadas_participou': 'Nº de Chamadas Aprovadas'})
        fig_hist.update_layout(bargap=0.1)
        st.plotly_chart(fig_hist, use_container_width=True)
    with col_r2:
        st.subheader("Taxa de recorrência por Gênero")
        df_gender = df_filtered.groupby(['num_chamadas_participou', 'genero']).size().reset_index(name='count')
        total_por_nivel = df_gender.groupby('num_chamadas_participou')['count'].transform('sum')
        df_gender['percent'] = (df_gender['count'] / total_por_nivel) * 100
        fig_gender = px.bar(df_gender, x='num_chamadas_participou', y='percent', color='genero', title="Distribuição de Gênero por Nível de Recorrência (%)", labels={'num_chamadas_participou': 'Nº de Chamadas Aprovadas', 'percent': 'Proporção (%)'}, text_auto='.1f', barmode='group')
        st.plotly_chart(fig_gender, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Selecione o Nível de Recorrência para Análise Detalhada")
    min_aprovacoes = st.slider("Filtrar pesquisadores com **NO MÍNIMO X** aprovações:", min_value=1, max_value=int(df['num_chamadas_participou'].max()), value=4, step=1)
    top_recorrentes = df_filtered[df_filtered['num_chamadas_participou'] >= min_aprovacoes].copy()
    st.dataframe(top_recorrentes[['pesquisador_padronizado', 'inst_padronizada', 'regiao_corrigida', 'num_chamadas_participou', 'h_index']].sort_values(by='num_chamadas_participou', ascending=False), column_config={"pesquisador_padronizado": "Pesquisador", "inst_padronizada": "Instituição", "regiao_corrigida": "Região", "num_chamadas_participou": st.column_config.NumberColumn("Aprovações", format="%d"), "h_index": "H-Index"}, use_container_width=True, hide_index=True)
    
    st.markdown(f"### Características dos pesquisadores com {min_aprovacoes} ou mais aprovações")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        fig_pie_rec = px.pie(top_recorrentes, names='categoria_adm_corrigida', title=f"Vínculo Administrativo", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie_rec, use_container_width=True)
    with col_p2:
        df_igc = top_recorrentes.dropna(subset=['igc_categoria'])
        if not df_igc.empty:
            fig_bar_igc = px.histogram(df_igc, x='igc_categoria', color='igc_categoria', title=f"Qualidade Institucional (IGC)", text_auto=True)
            fig_bar_igc.update_layout(showlegend=False)
            st.plotly_chart(fig_bar_igc, use_container_width=True)
        else:
            st.warning("Dados de IGC indisponíveis para este grupo.")
    st.markdown("IGC: Índice Geral de Cursos - indicador de qualidade das instituições de ensino superior, variando de 1 a 5. Valores mais altos indicam melhor avaliação institucional pelo MEC. Para mais informações, consulte (https://emec.mec.gov.br/).")
    
    

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        df_reg_rec = top_recorrentes['regiao_corrigida'].value_counts().reset_index()
        df_reg_rec.columns = ['Região', 'Total']
        fig_reg_rec = px.bar(df_reg_rec, x='Região', y='Total', color='Região', title=f"Concentração Regional (>{min_aprovacoes} aprovações)", text_auto=True)
        st.plotly_chart(fig_reg_rec, use_container_width=True)
    with col_g2:
        df_uf_rec = top_recorrentes['uf'].value_counts().reset_index()
        df_uf_rec.columns = ['UF', 'Total']
        fig_uf_rec = px.bar(df_uf_rec, x='Total', y='UF', orientation='h', color='Total', color_continuous_scale='Viridis', title=f"Ranking por Estado (>{min_aprovacoes} aprovações)", text_auto=True)
        fig_uf_rec.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_uf_rec, use_container_width=True)

# ==============================================================================
# ABA 4: SANKEY DIAGRAM (Refinado e Corrigido) + NOVOS GRÁFICOS
# ==============================================================================
with tab4:
    st.header(" Fluxo de Sobrevivência e Renovação (2014-2027)")
    st.markdown("Análise da trajetória dos pesquisadores: **Permanência** (Verde), **Evasão** (Vermelho) e **Renovação** (Azul).")

    # --- 1. Preparação dos Dados ---
    ciclos = {
        'ch_2014': '2014-2016',
        'ch_2016': '2016-2018',
        'ch_2018': '2018-2020',
        'ch_2020': '2020-2021',
        'ch_2022': '2022-2024',
        'ch_2024': '2024-2027'
    }
    colunas_ordenadas = list(ciclos.keys())
    labels_cronologicos = list(ciclos.values())
    
    # Binarizar
    df_sankey = df_filtered[colunas_ordenadas].fillna(0).applymap(lambda x: 1 if x > 0 else 0)

    # --- 2. Construção do Sankey (Versão 11.1 - Sem Erro de Fonte) ---
    COLOR_STAY = "rgba(89, 161, 79, 0.5)"   # Verde
    COLOR_EXIT = "rgba(225, 87, 89, 0.5)"   # Vermelho
    COLOR_NEW  = "rgba(78, 121, 167, 0.5)"  # Azul
    COLOR_NODE = "#495057"                  # Cinza Escuro
    
    labels_sankey = []
    source = []
    target = []
    value = []
    color_link = []
    x_pos = []
    y_pos = []
    layout_annotations = []
    
    # Listas para o Gráfico de Taxas (Parte 2 desta aba)
    stats_years = []
    stats_retention = []
    stats_exit = []
    stats_new = []

    num_steps = len(colunas_ordenadas)
    
    # Nós Principais
    for i, col in enumerate(colunas_ordenadas):
        total_ativos = df_sankey[col].sum()
        labels_sankey.append(f"{total_ativos}") 
        x = 0.05 + i * (0.9 / (num_steps - 1))
        y = 0.5
        x_pos.append(x)
        y_pos.append(y)
        
        layout_annotations.append(dict(x=x, y=-0.1, text=f"<b>{labels_cronologicos[i]}</b>", showarrow=False, font=dict(size=14, color="#333333", family="Arial"), xanchor="center", yanchor="top"))
        layout_annotations.append(dict(x=x, y=0.5, text=f"<b>{total_ativos}</b>", showarrow=False, font=dict(size=12, color="white", family="Arial"), xanchor="center", yanchor="middle"))

    node_idx_counter = len(colunas_ordenadas)

    # Links e Cálculo de Taxas
    for i in range(len(colunas_ordenadas) - 1):
        col_atual = colunas_ordenadas[i]
        col_prox = colunas_ordenadas[i+1]
        
        total_anterior = df_sankey[col_atual].sum()
        total_atual = df_sankey[col_prox].sum()
        
        ficou = df_sankey[(df_sankey[col_atual] == 1) & (df_sankey[col_prox] == 1)].shape[0]
        saiu = df_sankey[(df_sankey[col_atual] == 1) & (df_sankey[col_prox] == 0)].shape[0]
        entrou = df_sankey[(df_sankey[col_atual] == 0) & (df_sankey[col_prox] == 1)].shape[0]
        
        # Guardar estatísticas para o gráfico de linhas
        # Taxas em relação ao ciclo de destino (composição) ou origem (evasão)?
        # Padronização: % Novos (sobre total atual), % Retidos (sobre total atual), % Saída (sobre total anterior)
        stats_years.append(labels_cronologicos[i+1])
        stats_retention.append((ficou / total_atual * 100) if total_atual > 0 else 0)
        stats_new.append((entrou / total_atual * 100) if total_atual > 0 else 0)
        stats_exit.append((saiu / total_anterior * 100) if total_anterior > 0 else 0)

        # Construção Visual do Sankey
        x_start = x_pos[i]
        x_end = x_pos[i+1]
        x_mid = (x_start + x_end) / 2

        if ficou > 0:
            source.append(i)
            target.append(i+1)
            value.append(ficou)
            color_link.append(COLOR_STAY)
            layout_annotations.append(dict(x=x_mid, y=0.5, text=f"<b>{ficou}</b>", showarrow=False, font=dict(size=10, color="green"), bgcolor="rgba(255,255,255,0.7)"))

        if saiu > 0:
            labels_sankey.append("") 
            x_pos.append(x_mid)
            y_pos.append(0.85)
            idx_saida = node_idx_counter
            node_idx_counter += 1
            source.append(i)
            target.append(idx_saida)
            value.append(saiu)
            color_link.append(COLOR_EXIT)
            layout_annotations.append(dict(x=x_mid, y=0.92, text=f"Saída: <b>-{saiu}</b>", showarrow=False, font=dict(size=11, color="#B03030")))

        if entrou > 0:
            labels_sankey.append("") 
            x_pos.append(x_mid)
            y_pos.append(0.15)
            idx_entrada = node_idx_counter
            node_idx_counter += 1
            source.append(idx_entrada)
            target.append(i+1)
            value.append(entrou)
            color_link.append(COLOR_NEW)
            layout_annotations.append(dict(x=x_mid, y=0.08, text=f"Novos: <b>+{entrou}</b>", showarrow=False, font=dict(size=11, color="#2C5F8A")))

    fig_sankey = go.Figure(data=[go.Sankey(
        arrangement = "snap",
        node = dict(
            pad = 20, thickness = 20, line = dict(color = "white", width = 0.5),
            label = labels_sankey,
            color = [COLOR_NODE if l != "" else "rgba(0,0,0,0)" for l in labels_sankey],
            x = x_pos, y = y_pos, hoverinfo = "all"
        ),
        link = dict(source = source, target = target, value = value, color = color_link)
    )])

    fig_sankey.update_layout(title_text="Dinâmica Longitudinal do PIBIC-EM", font=dict(size=12, family="Arial"), height=600, margin=dict(l=20, r=20, t=40, b=100), annotations=layout_annotations, plot_bgcolor='white')
    st.plotly_chart(fig_sankey, use_container_width=True)

# --- GRÁFICO: EVOLUÇÃO DAS TAXAS ---
    st.divider()
    st.subheader("Evolução das Taxas de Renovação e Evasão")
    st.markdown("Acompanhamento percentual da composição dos grupos a cada novo edital.")

    # Criar DataFrame para o gráfico de linhas
    df_stats = pd.DataFrame({
        'Edital': stats_years,
        'Taxa de Novos (%)': stats_new,
        'Taxa de Retenção (%)': stats_retention,
        'Taxa de Evasão (%)': stats_exit
    })

    fig_lines = go.Figure()
    
    # Linha 1: Novos (Mantém desde o início)
    fig_lines.add_trace(go.Scatter(
        x=df_stats['Edital'], 
        y=df_stats['Taxa de Novos (%)'], 
        mode='lines+markers', 
        name='Novos Pesquisadores', 
        line=dict(color='#4c78a8', width=3)
    ))
    
    # Linha 2: Retenção (Mantém desde o início)
    fig_lines.add_trace(go.Scatter(
        x=df_stats['Edital'], 
        y=df_stats['Taxa de Retenção (%)'], 
        mode='lines+markers', 
        name='Retenção (Permanência)', 
        line=dict(color='#59a14f', width=3)
    ))
    
    # Linha 3: Evasão (ALTERADA: Começa a partir do 2º registro)
    # O slicing [1:] pula o primeiro dado (2016-2018) e começa em 2018-2020
    fig_lines.add_trace(go.Scatter(
        x=df_stats['Edital'][1:],  # <--- ALTERADO AQUI
        y=df_stats['Taxa de Evasão (%)'][1:], # <--- ALTERADO AQUI
        mode='lines+markers', 
        name='Evasão (Do edital anterior)', 
        line=dict(color='#e15759', width=3, dash='dot')
    ))

    fig_lines.update_layout(
        title="Indicadores de Fluxo por Edital",
        xaxis_title="Ciclo do PIBIC-EM",
        yaxis_title="Percentual (%)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_lines, use_container_width=True)
# ==============================================================================
# ABA 5: DESIGUALDADE (Layout Vertical)
# ==============================================================================
with tab5:
    st.header("A Anatomia da Desigualdade e Dinâmica da Recompensa")
    st.markdown("Esta seção sintetiza os resultados dos testes estatísticos de associação ($X^2$ e Kruskal-Wallis).")
    
    # 1. Matriz de Calor (Sem colunas, ocupando largura total)
    st.subheader("Estrutura de Oportunidades: Região x Tipo de IES")
    heatmap_data = pd.crosstab(df_filtered['regiao_corrigida'], df_filtered['categoria_adm_corrigida'])
    fig_heat = px.imshow(heatmap_data, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r", title="Matriz de Concentração: Região vs. Categoria Adm.")
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.divider()

    # 2. Curva de Lorenz (Logo abaixo)
    st.subheader("Concentração de Recursos (Curva de Lorenz)")
    lorenz_data = df_filtered.sort_values(by='num_chamadas_participou')
    n_pesquisadores = len(lorenz_data)
    if n_pesquisadores > 0:
        total_chamadas = lorenz_data['num_chamadas_participou'].sum()
        lorenz_x = np.arange(1, n_pesquisadores + 1) / n_pesquisadores
        lorenz_y = lorenz_data['num_chamadas_participou'].cumsum() / total_chamadas
        lorenz_x = np.insert(lorenz_x, 0, 0)
        lorenz_y = np.insert(lorenz_y, 0, 0)
        
        # Cálculo Gini
        area_sob_lorenz = integrate.trapezoid(lorenz_y, lorenz_x)
        gini = (0.5 - area_sob_lorenz) / 0.5
        
        fig_lorenz = go.Figure()
        fig_lorenz.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Igualdade Perfeita', line=dict(dash='dash', color='gray')))
        fig_lorenz.add_trace(go.Scatter(x=lorenz_x, y=lorenz_y, mode='lines', name='Distribuição Real', line=dict(color='blue')))
        fig_lorenz.update_layout(title=f"Curva de Lorenz (Gini Estimado: {gini:.3f})", xaxis_title="% Acumulado de Pesquisadores", yaxis_title="% Acumulado de Aprovações")
        st.plotly_chart(fig_lorenz, use_container_width=True)
    else:
        st.warning("Dados insuficientes.")
    st.markdown("**Interpretação:** O Gini estimado indica o grau de desigualdade na distribuição de aprovações. Quanto mais próximo de 1, maior a concentração em poucos pesquisadores.")
    st.markdown("Ao aplicarmos a Curva de Lorenz e o Índice de Gini para analisar a concentração de aprovações por pesquisador, encontramos um coeficiente de aproximadamente **0,265**. Este valor indica uma desigualdade moderada na distribuição individual das oportunidades.") 
    st.markdown("Contudo, esta 'igualdade aparente' deve ser lida com cautela crítica: ela não ocorre porque todos têm sucesso contínuo, mas sim porque a rotatividade é alta. Como o **leaky pipeline** (vazamento) é intenso, poucos pesquisadores conseguem acumular capital suficiente para se tornarem 'super-recorrentes', o que achata a curva.")
    st.markdown("O Gini baixo, neste caso, pode ser um sintoma da **dificuldade generalizada de permanência no programa**, e não de uma democratização plena do acesso.")
    st.divider()
    
    # 3. Análises Adicionais (Lado a Lado para finalizar)
    col_d3, col_d4 = st.columns(2)
    with col_d3:
        st.markdown("**Disparidade Regional na Permanência**")
        fig_box_rec = px.box(df_filtered, x='regiao_corrigida', y='num_chamadas_participou', color='regiao_corrigida', title="Distribuição da Recorrência por Região")
        st.plotly_chart(fig_box_rec, use_container_width=True)
    with col_d4:
        st.markdown("**O Paradoxo da Produtividade**")
        st.warning("⚠️ **Achado Contra-Intuitivo:** A 'elite produtiva' (alto H-index) não domina necessariamente a recorrência.")

# Rodapé
st.markdown("---")
st.caption("Desenvolvido por Tiago Ribeiro dos Anjos. Em caso de dúvidas ou sugestões, entre em contato: tiago.anjos@mail.utoronto.ca \ tiago.anjos@estudante.ufscar.br")