import numpy as np
import pandas as pd

from utils.leitor_infomacoes import load_portfolio_data, load_previsao_precos_data
from objetos.portfolio import Portfolio
from objetos.alternativa import Alternativa
from decision_models import xf_models
import utils.plotter as plt
import copy

pd.options.display.float_format = '{:.2f}'.format

compras_df, vendas_df = load_portfolio_data('D:/Programas/asotech/portfolio_atomo/dados/portfolio.xlsx')
previsao_precos = load_previsao_precos_data('D:/Programas/asotech/portfolio_atomo/dados/previsao_precos.xlsx')

dict_alternativa_1 = {
    'empresa': ["Compra_jun"],
    'volume': [0.5],
    'preco': [140],
    'inicio': pd.to_datetime(['2024-06-01']),
    'fim': pd.to_datetime(['2024-12-31']),
    'ponta': ["C"]
}
dict_alternativa_2 = {
    'empresa': ["Compra_ago"],
    'volume': [1],
    'preco': [140],
    'inicio': pd.to_datetime(['2024-08-01']),
    'fim': pd.to_datetime(['2024-12-31']),
    'ponta': ["C"]
}
dict_alternativa_3 = {
    'empresa': ["Compra_out"],
    'volume': [1],
    'preco': [140],
    'inicio': pd.to_datetime(['2024-10-01']),
    'fim': pd.to_datetime(['2024-12-31']),
    'ponta': ["C"]
}
dict_alternativa_4 = {
    'empresa': ["Venda_set"],
    'volume': [-1],
    'preco': [150],
    'inicio': pd.to_datetime(['2024-09-01']),
    'fim': pd.to_datetime(['2024-12-31']),
    'ponta': ["V"]
}
dict_alternativa_5 = {
    'empresa': ["Venda_jul"],
    'volume': [-0.6],
    'preco': [140],
    'inicio': pd.to_datetime(['2024-07-01']),
    'fim': pd.to_datetime(['2024-12-31']),
    'ponta': ["V"]
}
df_alternativa_1 = pd.DataFrame(dict_alternativa_1)
df_alternativa_2 = pd.DataFrame(dict_alternativa_2)
df_alternativa_3 = pd.DataFrame(dict_alternativa_3)
df_alternativa_4 = pd.DataFrame(dict_alternativa_4)
df_alternativa_5 = pd.DataFrame(dict_alternativa_5)

dict_df_alternativas = {
    'posicao_atual': None,
    "Compra_jun": df_alternativa_1,
    "Compra_ago": df_alternativa_2,
    "Compra_out": df_alternativa_3,
    'Venda_set': df_alternativa_4,
    'Venda_jul': df_alternativa_5
}

payoff_objetos = []
payoff = []
for cenario in previsao_precos:
    list_portfolios = []
    list_npv = []
    for nome, df_alt in dict_df_alternativas.items():
        p = Portfolio(previsao_precos[cenario], compras_df, vendas_df, df_alt)
        p = copy.deepcopy(p)
        list_portfolios.append(p)
        list_npv.append(p.valor_presente)
    payoff_objetos.append(list_portfolios)
    payoff.append(list_npv)
matrix_payoff = np.array(payoff).T

plt.plotar_previsao_precos(previsao_precos)
plt.plotar_balanco_energia(payoff_objetos[0][0])
plt.plotar_receitas_no_tempo(payoff_objetos[0][0])
plt.plotar_volume_financeiro(payoff_objetos[0][0])

payoff_objetos[0][0].print_info()

matrix_regret = xf_models.build_regret_matrix(-matrix_payoff)
matrix_cc = xf_models.build_choice_criteria_matrix(-matrix_payoff)
matrix_ncc = xf_models.build_normalized_choice_criteria_matrix(matrix_cc)


list_alternativas = [df_alternativa_1, df_alternativa_2, df_alternativa_3, df_alternativa_4, df_alternativa_5]
list_objetos_alterativas = []
for alternativa in list_alternativas:
    a = Alternativa(alternativa)
    list_objetos_alterativas.append(a)
plt.plotar_volume_alternativas(list_objetos_alterativas)

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
