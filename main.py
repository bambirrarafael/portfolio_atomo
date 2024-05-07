from utils.leitor_infomacoes import load_portfolio_data, load_previsao_precos_data
from objetos.portfolio import Portfolio
import utils.plotter as plt

compras_df, vendas_df = load_portfolio_data('D:/Programas/asotech/atomo/pythonProject/dados/portfolio.xlsx')
previsao_precos = load_previsao_precos_data('D:/Programas/asotech/atomo/pythonProject/dados/previsao_precos.xlsx')

p = Portfolio(compras_df, vendas_df)
p.calc_receita(cenario=previsao_precos)
p.calc_valor_presente(0.01)     # 1% ao mês, equivalente à 12.6% ao ano

plt.plotar_balanco_energia(p)
plt.plotar_receitas_no_tempo(p)
plt.plotar_volume_financeiro(p)
