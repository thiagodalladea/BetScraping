import re
import pandas as pd
import numpy as np
import itertools
import numexpr
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer

add_printer(1)

from betano import get_betano
from sporting_bet import get_sporting_bet
#from bet365 import get_bet365
from pinnacle import get_pinnacle
from draw import draw

col_team1 = "betano_name1"
col_team2 = "betano_name2"

draw()
print("----- Seja bem-vindo!!! ----- \n\n")
print("-- É importante que você não feche nenhuma janela do Chrome até que todas as requisições tenhas sidos feitas por completo.\n\n")
print("-- O processo pode demorar um pouco.\n\n")
print("-- Carregando as informações...\n\n")

df_betano = pd.DataFrame()
df_sportingbet = pd.DataFrame()
#df_bet365 = pd.DataFrame()
df_pinnacle = pd.DataFrame()

df_betano = get_betano()
df_sportingbet = get_sporting_bet()
#df_bet365 = get_bet365()
df_pinnacle = get_pinnacle()

# data_betano = {
#     'betano_name1': ['Philadelphia 76ers', 'Orlando Magic', 'Dallas Mavericks', 'Denver Nuggets'],
#     'betano_name2': ['New York Knicks', 'Cleveland Cavaliers', 'Los Angeles Clippers', 'Minnesota Timberwolves'],
#     'betano_odd1': [2.52, 1.57, 1.31, 1.55],
#     'betano_odd2': [2.5, 2.5, 3.65, 2.52]
# }

# data_pinnacle = {
#     'pinnacle_name1': ['Philadelphia 76ers', 'Orlando Magic', 'Dallas Mavericks', 'Denver Nuggets'],
#     'pinnacle_name2': ['New York Knicks', 'Cleveland Cavaliers', 'Los Angeles Clippers', 'Minnesota Timberwolves'],
#     'pinnacle_odd1': [1.645, 1.588, 1.3, 5.564],
#     'pinnacle_odd2': [2.38, 2.53, 3.83, 2.58],
# }

# df_betano = pd.DataFrame(data_betano)
# df_pinnacle = pd.DataFrame(data_pinnacle)

df_betano = df_betano.sort_values(by="betano_name1")
df_pinnacle = df_pinnacle.sort_values(by="pinnacle_name1")
df_sportingbet = df_sportingbet.sort_values(by="sportingbet_name1")

# if any(df.empty for df in [df_betano, df_sportingbet, df_bet365, df_pinnacle]):
#     print("A requisição de dados não aconteceu corretamente.")

print("\n\nBETANO------------")
print(df_betano)
print("\n\nPINNACLE------------")
print(df_pinnacle)
print("\n\nSPORTING BET------------")
print(df_sportingbet)
# print("\n\nBET 365------------")
# print(df_bet365)

merged_df = pd.DataFrame()

merged_df = pd.merge(df_betano, df_pinnacle, left_on=['betano_name1', 'betano_name2'], right_on=['pinnacle_name1', 'pinnacle_name2'], how='outer')
merged_df = pd.merge(merged_df, df_sportingbet, left_on=["betano_name1", "betano_name2"], right_on=["sportingbet_name1", "sportingbet_name2"], how="outer")
#merged_df = pd.merge(merged_df, df_bet365, left_on=["betano_name1", "betano_name2"], right_on=["bet365_name1", "bet365_name2"], how="outer")
merged_df = merged_df.dropna().reset_index(drop=True)

print(merged_df)

bet_value = 100

columns = np.array(
    [
        ["betano_odd1", "betano_odd2"],
        ["pinnacle_odd1", "pinnacle_odd2"],
        ["sportingbet_odd1", "sportingbet_odd2"]
    ]
)

divcols = []
suffixo = "_div1"
for d in columns.flatten():
    new_column = f"{d}{suffixo}"
    merged_df[new_column] = (1 / merged_df[d]).astype(np.float64)
    divcols.append(new_column)

compare_columns = np.array(divcols).reshape(columns.shape)
itercols = itertools.product(*compare_columns.T)

table = pd.concat(
    [merged_df[col] for col in map(list, itercols)], ignore_index=True, copy=False
).fillna(0)

more_than_1 = numexpr.evaluate(
    "sum(table, 1)",
    global_dict={},
    local_dict={"table": table},
)

less_than_1 = numexpr.evaluate(
    "more_than_1<1", global_dict={}, local_dict={"more_than_1": more_than_1}
)

good_results = table[less_than_1]

table_columns = pd.DataFrame(
    np.tile(table.columns, ((len(good_results)), 1))
)

not_zero = numexpr.evaluate(
    "good_results != 0",
    global_dict={},
    local_dict={"good_results": good_results},
)

good_ind = np.where(not_zero)

good_results_np_array = np.array(
    [good_results.iat[*h] for h in zip(*good_ind)]
).reshape((-1, 2))

good_results_np_array_col = np.array(
    [table_columns.iat[*h] for h in zip(*good_ind)]
).reshape((-1, 2))

allresults = []

for col, number in zip(good_results_np_array_col, good_results_np_array):
    original = [x[: -len(suffixo)] for x in col]

    win = merged_df.loc[
        (merged_df[col[0]] == number[0])
        & (merged_df[col[1]] == number[1])
    ][list((col_team1, col_team2, *col, *original))]
    if not win.empty:
        win.columns = [
            "team1",
            "team2",
            "odd0",
            "odd1",
            "odd_casa0",
            "odd_casa1"
        ]
    else:
        print("vazio")
    win["porcentagem"] = win[["odd0", "odd1"]].sum(axis=1)
    for i in range(len(col)):
        win[f"casa{i}"] = col[i]
        win[f"div{i}"] = win[f"odd{i}"] / win[f"porcentagem"]
        win[f"aposta{i}"] = bet_value * win[f"div{i}"]
        win[f"lucro{i}"] = win[f"aposta{i}"] * win[f"odd_casa{i}"] - 100
    allresults.append(win)
try:
    df_final = (
        pd.concat(allresults).sort_values(by=f"porcentagem").reset_index(drop=True)
    )
    print("ARBITRAGEM------------")
    unique = df_final[["team1", "team2", "casa0", "casa1", "odd_casa0", "odd_casa1", "aposta0", "aposta1", "lucro0", ]]
    print(unique)
except Exception:
    df_final = pd.DataFrame()
    print("NÃO HÁ ARBITRAGENS POSSÍVEIS NO MOMENTO")