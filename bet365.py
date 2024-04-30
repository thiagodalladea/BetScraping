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

add_printer(1)

def get_dataframe_teams(query="*", selector="*"):
    df = pd.DataFrame()
    while df.empty:
        df = get_df(
            driver,
            By,
            WebDriverWait,
            expected_conditions,
            queryselector = query,
            with_methods = True,
        )
    df = df.loc[df.aa_className == selector]
    return df.reset_index(drop=True)

def get_dataframe_odds(query="*"):
    df = pd.DataFrame()
    while df.empty:
        df = get_df(
            driver,
            By,
            WebDriverWait,
            expected_conditions,
            queryselector = query,
            with_methods = True,
        )
    return df.reset_index(drop=True)

try:
    driver = Driver(uc=True)
    driver.get(
        "https://www.bet365.com/#/AC/B1/C1/D1002/E88369731/G40/"
    )
    df_teams = get_dataframe_teams(selector="rcl-ParticipantFixtureDetails_TeamNames")
    df_teams = df_teams.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x) if not re.match(r"\d{2}:\d{2}\b", q) if not re.match(r"^\d+$", q)]))[[0, 1]].rename( columns={0: "team1_name", 1: "team2_name"}).dropna()
    sleep(2.23)
    df_odds = get_dataframe_odds()
    df_odds = df_odds.loc[df_odds.aa_className == "sgl-ParticipantOddsOnly80_Odds"]
    df_odds = df_odds[["aa_innerText"]]
    df_parts_odds = np.array_split(df_odds, 3)
    df_part_1 = df_parts_odds[0]
    df_part_2 = df_parts_odds[1]
    df_part_3 = df_parts_odds[2]
    df_part_1 = df_part_1.rename(columns={"aa_innerText": "team1_odds"})
    df_part_2 = df_part_2.rename(columns={"aa_innerText": "draw_odds"})
    df_part_3 = df_part_3.rename(columns={"aa_innerText": "team2_odds"})
    df = df_teams
    df = pd.concat([df, df_part_1.reset_index(drop=True)], axis=1)
    df = pd.concat([df, df_part_2.reset_index(drop=True)], axis=1)
    df = pd.concat([df, df_part_3.reset_index(drop=True)], axis=1)

except Exception as exception:
    print("Ocorreu algum erro durante a requisição de dados :(\n\n")
    print("Mais informações:\n", exception)