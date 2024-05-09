import numpy as np
import pandas as pd

from utils.leitor_infomacoes import load_portfolio_data, load_previsao_precos_data
from objetos.portfolio import Portfolio
from decision_models import xf_models
import utils.plotter as plt

pd.options.display.float_format = '{:.2f}'.format

compras_df, vendas_df = load_portfolio_data('D:/Programas/asotech/portfolio_atomo/dados/portfolio.xlsx')
previsao_precos = load_previsao_precos_data('D:/Programas/asotech/portfolio_atomo/dados/previsao_precos.xlsx')

dict_alternativa_1 = {
    'empresa': ["Compra_A"],
    'volume': [1],
    'preco': [140],
    'inicio': pd.to_datetime(['2024-05-01']),
    'fim': pd.to_datetime(['2024-12-31']),
    'ponta': ["C"]
}
df_alternativa_1 = pd.DataFrame(dict_alternativa_1)

dict_df_alternativas = {
    'posicao_atual': None,
    "Compra_A": df_alternativa_1
}

payoff_objetos = []
payoff = []
for cenario in previsao_precos:
    list_portfolios = []
    list_npv = []
    for nome, df_alt in dict_df_alternativas.items():
        p = Portfolio(previsao_precos[cenario], compras_df, vendas_df, df_alt)
        list_portfolios.append(p)
        list_npv.append(p.valor_presente)
    payoff_objetos.append(list_portfolios)
    payoff.append(list_npv)
matrix_payoff = np.array(payoff)

plt.plotar_previsao_precos(previsao_precos)
plt.plotar_balanco_energia(payoff_objetos[0][0])
plt.plotar_receitas_no_tempo(payoff_objetos[0][0])
plt.plotar_volume_financeiro(payoff_objetos[0][0])

payoff_objetos[0][0].print_info()

matrix_regret = xf_models.build_regret_matrix(-matrix_payoff)
matrix_cc = xf_models.build_choice_criteria_matrix(-matrix_payoff)
matrix_ncc = xf_models.build_normalized_choice_criteria_matrix(matrix_cc)

print(f'\n\n ------ Resultado do modelos de decisão: \n')
index = list(dict_df_alternativas.keys())
columns = ['W', 'S', 'L', 'H']
df = pd.DataFrame(matrix_ncc, index=index, columns=columns)
print(df)
print(f'\n Matrizes avaliadas: \n')
print(f' Objetivo: valor_presente')
df = pd.DataFrame(matrix_payoff, index=index, columns=previsao_precos.columns)
print(df)
print(f'\n ')
print(f'Fim da análise -----')
