import pandas as pd
import numpy as np
from objetos.portfolio import expand_df, weighted_mean


class Alternativa:

    def __init__(self, df_alternativa):
        self.df_alternativa = df_alternativa
        self.nome = df_alternativa['empresa'].iloc[0]
        self.min_date = df_alternativa['inicio'].index.min()
        self.max_date = df_alternativa['fim'].index.max()
        self.informacoes = self.calc_alternativa()

    def calc_alternativa(self):
        expanded_df = pd.concat([expand_df(row) for index, row in self.df_alternativa.iterrows()])
        expanded_df['horas_no_mes'] = expanded_df['dias_no_mes'] * 24
        monthly_data = expanded_df.groupby('data').agg(
            volume=pd.NamedAgg(column='volume', aggfunc='sum'),
            preco_medio=pd.NamedAgg(column='preco', aggfunc=lambda x: weighted_mean(expanded_df.loc[x.index])),
            horas_no_mes=pd.NamedAgg(column='horas_no_mes', aggfunc='max')
        )
        monthly_data['preco_medio'] = -monthly_data['preco_medio']
        monthly_data['resultado_financeiro'] = monthly_data['volume'] * monthly_data['preco_medio'] * monthly_data[
            'horas_no_mes']
        self.informacoes = monthly_data
        return self.informacoes



