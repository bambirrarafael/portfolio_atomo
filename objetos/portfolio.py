import pandas as pd
import numpy as np
import numpy_financial as npf


class Portfolio:

    def __init__(self, cenario, compras_df, vendas_df, alternativas_df=None):
        self.cenario = cenario
        self.min_date = cenario.index.min()
        self.max_date = cenario.index.max()
        self.compras_df, self.vendas_df = self.considerar_alternativa(compras_df, vendas_df, alternativas_df)
        self.recursos_df = self.calc_recursos()
        self.requisitos_df = self.calc_requisitos()
        self.exposicao_df = self.calc_exposicao()
        #
        self.receita = self.calc_receita()
        self.valor_presente = self.calc_valor_presente(0.01)  # 1% ao mês, equivalente à 12.6% ao ano

    def print_info(self):
        print("\n ------- Relatório do portfólio \n")
        print(f'Cenário: {self.cenario.name} \n')
        print("Informações de Compras:")
        print(self.compras_df)
        print("\n")
        print("Informações de Vendas:")
        print(self.vendas_df)
        print("\n")
        if self.receita is not None:
            print(f'Horizonte de análise: \n {self.receita.index[0]} --- {self.receita.index[-1]} \n')
        else:
            print(f'Horizonte ainda não avaliado')
        if self.valor_presente is not None:
            print(f"Valor Presente do Portfólio: R$ {self.valor_presente:.2f}")
        else:
            print("Valor Presente do Portfólio: Não calculado")

    @staticmethod
    def considerar_alternativa(compras_df, vendas_df, alternativas_df):
        if alternativas_df is not None:
            for index, row in alternativas_df.iterrows():
                if row['ponta'] == 'C':
                    compras_df.loc[len(compras_df)] = row[:-1]
                elif row['ponta'] == 'V':
                    vendas_df.loc[len(vendas_df)] = row[:-1]
                else:
                    print("Erro al declarar a ponta da alternativa")
        return compras_df, vendas_df

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
        self.recursos_df = monthly_data.loc[self.min_date:self.max_date]
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
        self.requisitos_df = monthly_data.loc[self.min_date:self.max_date]
        return self.requisitos_df

    def calc_exposicao(self):
        new_index = pd.date_range(start=self.min_date, end=self.max_date, freq='MS')
        self.recursos_df = self.recursos_df.reindex(new_index, fill_value=0)
        self.requisitos_df = self.requisitos_df.reindex(new_index, fill_value=0)
        self.exposicao_df = pd.DataFrame(self.recursos_df['volume'] - self.requisitos_df['volume'])
        self.exposicao_df['horas_no_mes'] = self.exposicao_df.index.days_in_month * 24
        return self.exposicao_df

    def calc_receita(self):
        new_index = pd.date_range(start=self.min_date, end=self.max_date, freq='MS')
        self.recursos_df = self.recursos_df.reindex(new_index, fill_value=0)
        self.requisitos_df = self.requisitos_df.reindex(new_index, fill_value=0)
        self.exposicao_df = self.exposicao_df.reindex(new_index, fill_value=0)
        self.exposicao_df['resultado_financeiro'] = self.exposicao_df['volume'] * self.exposicao_df['horas_no_mes'] * self.cenario
        self.receita = self.recursos_df['resultado_financeiro'] + self.requisitos_df['resultado_financeiro'] + self.exposicao_df['resultado_financeiro']
        return self.receita

    def calc_valor_presente(self, taxa):
        self.valor_presente = npf.npv(taxa, self.receita)
        return self.valor_presente


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
