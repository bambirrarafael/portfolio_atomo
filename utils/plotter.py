import plotly.graph_objects as go
import plotly.express as px


def plotar_balanco_energia(portfolio):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=portfolio.recursos_df.index, y=portfolio.recursos_df['volume'], mode='lines', name='Recursos'))
    fig.add_trace(go.Scatter(x=portfolio.requisitos_df.index, y=portfolio.requisitos_df['volume'], mode='lines', name='Requisitos'))
    fig.add_trace(go.Bar(x=portfolio.exposicao_df.index, y=portfolio.exposicao_df['volume'], name='Exposição'))
    fig.update_layout(title='Balanço de energia',
                      xaxis_title='Data',
                      yaxis_title='Volume')
    fig.show()


def plotar_receitas_no_tempo(portfolio):
    fig = px.line(portfolio.receita.cumsum())
    fig.update_layout(title='Evolução patrimonial',
                      xaxis_title='Data',
                      yaxis_title='Valor')
    fig.show()


def plotar_volume_financeiro(portfolio):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=portfolio.recursos_df.index, y=-portfolio.recursos_df['resultado_financeiro'], mode='lines', name='-1 * Recursos'))
    fig.add_trace(go.Scatter(x=portfolio.requisitos_df.index, y=portfolio.requisitos_df['resultado_financeiro'], mode='lines', name='Requisitos'))
    fig.add_trace(go.Scatter(x=portfolio.exposicao_df.index, y=portfolio.exposicao_df['resultado_financeiro'], mode='lines', name='Exposição'))
    fig.update_layout(title='Volume financeiro',
                      xaxis_title='Data',
                      yaxis_title='Valor')
    fig.show()
