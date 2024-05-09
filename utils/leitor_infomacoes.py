import pandas as pd
import os

def load_portfolio_data(filepath):
    # Use a dictionary to read both sheets into separate DataFrames
    data = pd.read_excel(filepath, sheet_name=["compras", "vendas"])

    compras_df = data["compras"]
    vendas_df = data["vendas"]

    return compras_df, vendas_df


def load_previsao_precos_data(filepath):
    dfs = pd.read_excel(filepath)
    dfs = dfs.set_index('mes')
    return dfs
