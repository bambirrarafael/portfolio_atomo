import pandas as pd
import numpy as np
import numpy_financial as npf


class Portfolio:

    def __init__(self, compras_df, vendas_df):
        self.compras_df = compras_df
        self.vendas_df = vendas_df
        self.recursos_df = self.calc_recursos()
        self.requisitos_df = self.calc_requisitos()
        self.exposicao_df = self.calc_exposicao()
        #
        self.receita = None
        self.valor_presente = None

    def calc_recursos(self):
        expanded_df = pd.concat([expand_df(row) for index, row in self.compras_df.iterrows()])
        expanded_df['horas_no_mes'] = expanded_df['dias_no_mes'] * 24
        monthly_data = expanded_df.groupby('data').agg(
            volume=pd.NamedAgg(column='volume', aggfunc='sum'),
            preco_medio=pd.NamedAgg(column='preco', aggfunc=lambda x: weighted_mean(expanded_df.loc[x.index])),
            horas_no_mes=pd.NamedAgg(column='horas_no_mes', aggfunc='max')
        )
        monthly_data['preco_medio'] = -monthly_data['preco_medio']
        monthly_data['resultado_financeiro'] = monthly_data['volume'] * monthly_data['preco_medio'] * monthly_data['horas_no_mes']
        self.recursos_df = monthly_data
        return self.recursos_df

    def calc_requisitos(self):
        expanded_df = pd.concat([expand_df(row) for index, row in self.vendas_df.iterrows()])
        expanded_df['horas_no_mes'] = expanded_df['dias_no_mes'] * 24
        monthly_data = expanded_df.groupby('data').agg(
            volume=pd.NamedAgg(column='volume', aggfunc='sum'),
            preco_medio=pd.NamedAgg(column='preco', aggfunc=lambda x: weighted_mean(expanded_df.loc[x.index])),
            horas_no_mes=pd.NamedAgg(column='horas_no_mes', aggfunc='max')
        )
        monthly_data['resultado_financeiro'] = monthly_data['volume'] * monthly_data['preco_medio'] * monthly_data['horas_no_mes']
        self.requisitos_df = monthly_data
        return self.requisitos_df

    def calc_exposicao(self):
        min_date = min(self.recursos_df.index.min(), self.requisitos_df.index.min())
        max_date = max(self.recursos_df.index.max(), self.requisitos_df.index.max())
        new_index = pd.date_range(start=min_date, end=max_date, freq='MS')
        self.recursos_df = self.recursos_df.reindex(new_index, fill_value=0)
        self.requisitos_df = self.requisitos_df.reindex(new_index, fill_value=0)
        self.exposicao_df = pd.DataFrame(self.recursos_df['volume'] - self.requisitos_df['volume'])
        self.exposicao_df['horas_no_mes'] = self.exposicao_df.index.days_in_month * 24
        return self.exposicao_df

    def calc_receita(self, cenario):
        cenario.set_index('mes', inplace=True)
        min_date = min(self.recursos_df.index.min(), self.requisitos_df.index.min(), cenario.index. min())
        max_date = max(self.recursos_df.index.max(), self.requisitos_df.index.max(), cenario.index. max())
        new_index = pd.date_range(start=min_date, end=max_date, freq='MS')
        self.recursos_df = self.recursos_df.reindex(new_index, fill_value=0)
        self.requisitos_df = self.requisitos_df.reindex(new_index, fill_value=0)
        self.exposicao_df = self.exposicao_df.reindex(new_index, fill_value=0)
        cenario = cenario.reindex(new_index, fill_value=0)
        self.exposicao_df['resultado_financeiro'] = self.exposicao_df['volume'] * self.exposicao_df['horas_no_mes'] * cenario['valor']
        self.receita = self.recursos_df['resultado_financeiro'] + self.requisitos_df['resultado_financeiro'] + self.exposicao_df['resultado_financeiro']

    def calc_valor_presente(self, taxa):
        self.valor_presente = npf.npv(taxa, self.receita)


def expand_df(row):
    start = row['inicio']
    end = row['fim']
    r = pd.date_range(start=start, end=end, freq='MS')
    days_in_month = [((min(end, pd.Timestamp(year=d.year, month=d.month, day=d.days_in_month)) -
                       max(start, pd.Timestamp(year=d.year, month=d.month, day=1))).days + 1)
                     for d in r]
    return pd.DataFrame({
        'empresa': row['empresa'],
        'volume': row['volume'],
        'preco': row['preco'],
        'data': r,
        'dias_no_mes': days_in_month
    })


def weighted_mean(x):
    return np.average(x['preco'], weights=x['volume'])
