import re
import pandas as pd
import numpy as np
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer
from time import sleep
from rename import rename

add_printer(1)

def format_bet365_teams(df):
    df = df.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x)
        if not re.match(r"\d{2}:\d{2}\b", q)]))[[0, 1]].rename(columns={
            0: "bet365_name1",
            1: "bet365_name2",
        }).dropna()
    df["bet365_name1"] = df["bet365_name1"].apply(rename)
    df["bet365_name2"] = df["bet365_name2"].apply(rename)
    print("\nBET 365 TEAMS DATA REQUESTED SUCCESSFULLY!\n")

    return df.reset_index(drop=True)

def format_bet365_odds(df):
    df = df.dropna(subset="aa_innerText")
    df = df[["aa_innerText"]]
    df_parts_odds = np.array_split(df, 3)
    df_part_1 = df_parts_odds[0]
    df_part_2 = df_parts_odds[1]
    df_part_3 = df_parts_odds[2]
    df_part_1 = df_part_1.rename(columns={"aa_innerText": "bet365_odd1"})
    df_part_2 = df_part_2.rename(columns={"aa_innerText": "bet365_odd2"})
    df_part_3 = df_part_3.rename(columns={"aa_innerText": "bet365_odd3"})
    df_odds = pd.concat([df_part_1, df_part_2.reset_index(drop=True)], axis=1)
    df_odds = pd.concat([df_odds, df_part_3.reset_index(drop=True)], axis=1)
    print("\nBET365 ODDS DATA REQUESTED SUCCESSFULLY!\n")

    return df_odds.reset_index(drop=True)