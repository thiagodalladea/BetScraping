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
from get_data import get_data
from urls import get_urls

add_printer(1)

event = threading.Event()

col_team1 = "bet365_name1"
col_team2 = "bet365_name2"

urls = get_urls()

def open_site(name, url, query="*"):
    drivers[name].get(url)
    df = get_data(drivers[name], name, query)
    results.append(df)
    drivers[name].quit()
    event.set()

names = [
    "betano",
    "sportingbet",
    "bet365",
    "betfair"
]

for url1 in urls:
    drivers = {}

    querys = [
        "div.vue-recycle-scroller__item-view",
        "ms-event",
        ["div.rcl-ParticipantFixtureDetails_TeamNames", "span.sgl-ParticipantOddsOnly80_Odds"],
        "li.com-coupon-line-new-layout",
    ]

    for name in names:
        drivers[name] = Driver(uc=True)

    threads = []
    results = []
    start = time()

    for name, url, query in zip(names, url1, querys):
        try:
            thread = threading.Thread(target=open_site, args=(name, url, query))
            thread.start()
            threads.append(thread)
        except Exception as e:
            print(e)
            continue

    for thread in threads:
        thread.join()

    event.wait()

    end = time()

    print(results)

    df_betano = pd.DataFrame()
    df_sportingbet = pd.DataFrame()
    df_bet365 = pd.DataFrame()
    df_betfair = pd.DataFrame()

    for result in results:
        if result.columns[0] == "betano_name1":
            df_betano = result
        elif result.columns[0] == "sportingbet_name1":
            df_sportingbet = result
        elif result.columns[0] == "bet365_name1":
            df_bet365 = result
        elif result.columns[0] == "betfair_name1":
            df_betfair = result

    merged_df = pd.DataFrame()

    merged_df = pd.merge(df_betano, df_sportingbet, left_on=["betano_name1", "betano_name2"],
        right_on=["sportingbet_name1", "sportingbet_name2"], how="outer")
    merged_df = pd.merge(merged_df, df_bet365, left_on=["betano_name1", "betano_name2"],
        right_on=["bet365_name1", "bet365_name2"], how="outer")
    merged_df = pd.merge(merged_df, df_betfair, left_on=["betano_name1", "betano_name2"],
        right_on=["betfair_name1", "betfair_name2"], how="outer")
    merged_df = merged_df.dropna().reset_index(drop=True)

    print("\n\nMERGED------------")
    print(merged_df)

    bet_value = 100

    columns = np.array(
        [
            ["betano_odd1", "betano_odd2", "betano_odd3"],
            ["sportingbet_odd1", "sportingbet_odd2", "sportingbet_odd3"],
            ["bet365_odd1", "bet365_odd2", "bet365_odd3"],
            ["betfair_odd1", "betfair_odd2", "betfair_odd3"],
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
        print("THERE ARE NO ARBITRAGE BETTING AT THIS TIME")

    # print("REQUEST TIME:  " + str(end - start) + " SECONDS")