import re
import pandas as pd
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer
from time import sleep
from rename import rename

add_printer(1)

def format_betfair(df):
    df = df.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x)
        if not re.match("SUSPENSO", q)
    ]))
    df_teams = df.iloc[:, [6,7]]
    df_odds = df.iloc[:, [3,4,5]]
    df = pd.concat([df_teams, df_odds.reset_index(drop=True)], axis=1)
    df = df[[6, 7, 3, 4, 5]].rename(
        columns={
            6: "betfair_name1",
            7: "betfair_name2",
            3: "betfair_odd1",
            4: "betfair_odd2",
            5: "betfair_odd3"
        }).dropna().assign(
            betfair_odd1=lambda q:q.betfair_odd1.str.replace(",", "."),
            betfair_odd2=lambda q:q.betfair_odd2.str.replace(",", "."),
            betfair_odd3=lambda q:q.betfair_odd3.str.replace(",", ".")).astype({
                "betfair_odd1": "Float64", "betfair_odd2": "Float64", "betfair_odd3": "Float64"
            })
    df["betfair_name1"] = df["betfair_name1"].apply(rename)
    df["betfair_name2"] = df["betfair_name2"].apply(rename)
    print("\nBETFAIR ODDS DATA REQUESTED SUCCESSFULLY!\n")

    return df.sort_values(by=["betfair_name1", "betfair_name2"]).reset_index(drop=True)