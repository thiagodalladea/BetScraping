import pandas as pd
import threading
import numpy as np
import itertools
import numexpr
from selenium.webdriver.support import expected_conditions
from seleniumbase import Driver
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from selenium.webdriver.common.by import By
from PrettyColorPrinter import add_printer
from time import sleep, time
from betano import get_betano
from sporting_bet import get_sporting_bet
from bet365 import get_bet365_teams, get_bet365_odds
from pinnacle import get_pinnacle

add_printer(1)

drivers = {}

def open_site(name, url, query="*"):
    def get_data():
        sleep(2)
        return get_df(
            drivers[name],
            By,
            WebDriverWait,
            expected_conditions,
            queryselector = query,
            with_methods = True,
        )
    drivers[name].get(url)
    df=pd.DataFrame()
    while df.empty:
        sleep(2)
        df = get_data()
    if name == "betano":
        df = get_betano(df)
    elif name == "sporting_bet":
        df = get_sporting_bet(df)
    elif name == "bet365_teams":
        df = get_bet365_teams(df)
    elif name == "bet365_odds":
        df = get_bet365_odds(df)
    elif name == "pinnacle":
        df = get_pinnacle(df)
    results.append(df)
    drivers[name].quit()

names = [
    "betano",
    "sporting_bet",
    "bet365_teams",
    "bet365_odds",
    "pinnacle",
]

urls = [
    "https://br.betano.com/sport/futebol/brasil/brasileirao-serie-a-betano/10016/",
    "https://sports.sportingbet.com/pt-br/sports/futebol-4/aposta/brasil-33/brasileir%C3%A3o-a-102838",
    "https://www.bet365.com/#/AC/B1/C1/D1002/E88369731/G40/",
    "https://www.bet365.com/#/AC/B1/C1/D1002/E88369731/G40/",
    "https://pinnacle.com/pt/soccer/brazil-serie-a/matchups/#all",
]

querys = [
    "div.vue-recycle-scroller__item-view",
    "ms-event",
    "div.rcl-ParticipantFixtureDetails_TeamNames",
    "span.sgl-ParticipantOddsOnly80_Odds",
    "div.style_row__12oAB",
]

for name in names:
    drivers[name] = Driver(uc=True)

threads = []
results = []
# start = time()
for name, url, query in zip(names, urls, querys):
    try:
        thread = threading.Thread(target=open_site, args=(name, url, query))
        thread.start()
        threads.append(thread)
    except Exception as e:
        print(e)
        continue

for thread in threads:
    thread.join()

# end = time()

rm_ind = []
for i, df in enumerate(results):
    cols = df.shape[1]
    if cols == 2 or cols == 3:
        rm_ind.append(i)
        if cols == 2:
            df1 = df
        elif cols == 3:
            df2 = df
for index in sorted(rm_ind, reverse=True):
    del results[index]

df_bet_365 = pd.concat([df1, df2.reset_index(drop=True)], axis=1)
df_bet_365.sort_values(by=["bet365_name1", "bet365_name2"])
results.append(df_bet_365)
print(results)

for result in results:
    if result.columns[0] == "betano_name1":
        df_betano = result
    elif result.columns[0] == "sportingbet_name1":
        df_sportingbet = result
    elif result.columns[0] == "bet365_name1":
        df_bet365 = result
    elif result.columns[0] == "pinnacle_name1":
        df_pinnacle = result

merged_df = pd.DataFrame()

merged_df = pd.merge(df_betano, df_sportingbet, left_on=["betano_name1", "betano_name2"],
    right_on=["sportingbet_name1", "sportingbet_name2"], how="outer")
merged_df = pd.merge(merged_df, df_bet365, left_on=["betano_name1", "betano_name2"],
    right_on=["bet365_name1", "bet365_name2"], how="outer")
merged_df = pd.merge(merged_df, df_pinnacle, left_on=["betano_name1", "betano_name2"],
    right_on=["pinnacle_name1", "pinnacle_name2"], how="outer")
merged_df = merged_df.dropna().reset_index(drop=True)

print("\n\nMERGED------------")
print(merged_df)

bet_value = 100

columns = np.array(
    [
        ["betano_odd1", "betano_odd2", "betano_odd3"],
        ["sportingbet_odd1", "sportingbet_odd2", "sportingbet_odd3"],
        ["bet365_odd1", "bet365_odd2", "bet365_odd3"],
        ["pinnacle_odd1", "pinnacle_odd2", "pinnacle_odd3"],
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
).reshape((-1, 3))

good_results_np_array_col = np.array(
    [table_columns.iat[*h] for h in zip(*good_ind)]
).reshape((-1, 3))

allresults = []

for col, number in zip(good_results_np_array_col, good_results_np_array):
    original = [x[: -len(suffixo)] for x in col]

    win = merged_df.loc[
        (merged_df[col[0]] == number[0])
        & (merged_df[col[1]] == number[1])
        & (merged_df[col[2]] == number[2])
    ][list((col_team1, col_team2, *col, *original))]
    if not win.empty:
        win.columns = [
            "team1",
            "team2",
            "odd0",
            "odd1",
            "odd2",
            "odd_casa0",
            "odd_casa1",
            "odd_casa2"
        ]
    else:
        print("vazio")
    win["porcentagem"] = win[["odd0", "odd1", "odd2"]].sum(axis=1)
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
    unique = df_final[["team1", "team2", "casa0", "casa1", "casa2", "odd_casa0", "odd_casa1", "odd_casa2", "aposta0", "aposta1", "aposta2", "lucro0", ]]
    print(unique)
except Exception:
    df_final = pd.DataFrame()
    print("NÃO HÁ ARBITRAGENS NO MOMENTO")

# print("REQUEST TIME:  " + str(end - start) + " SECONDS")