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

def get_dataframe_teams(driver, query="*"):
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
    df = df.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x)
        if not re.match(r"\d{2}:\d{2}\b", q)]))[[0, 1]].rename(columns={
            0: "bet365_name1",
            1: "bet365_name2",
        }).dropna()

    return df.reset_index(drop=True)

def get_dataframe_odds(driver, query="*"):
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
    df = df.dropna(subset="aa_innerText")
    df = df[["aa_innerText"]]

    return df.reset_index(drop=True)

def get_bet365():
    try:
        driver = Driver(uc=True)
        sleep(2.3)
        driver.get(
            "https://www.bet365.com/#/AC/B1/C1/D1002/E88369731/G40/"
        )
        df_teams = get_dataframe_teams(driver, query="div.rcl-ParticipantFixtureDetails_LhsContainer")
        df_odds = get_dataframe_odds(driver, query="span.sgl-ParticipantOddsOnly80_Odds")
        driver.quit()
        df_parts_odds = np.array_split(df_odds, 3)
        df_part_1 = df_parts_odds[0]
        df_part_2 = df_parts_odds[1]
        df_part_3 = df_parts_odds[2]
        df_part_1 = df_part_1.rename(columns={"aa_innerText": "bet365_odd1"})
        df_part_2 = df_part_2.rename(columns={"aa_innerText": "bet365_odd2"})
        df_part_3 = df_part_3.rename(columns={"aa_innerText": "bet365_odd3"})
        df = df_teams
        df = pd.concat([df, df_part_1.reset_index(drop=True)], axis=1)
        df = pd.concat([df, df_part_2.reset_index(drop=True)], axis=1)
        df = pd.concat([df, df_part_3.reset_index(drop=True)], axis=1)
        print("\nRequisição de dados da BET365 concluída com sucesso!\n")
        df["bet365_name1"] = df["bet365_name1"].apply(rename)
        df["bet365_name2"] = df["bet365_name2"].apply(rename)

        return df.sort_values(by=["bet365_name1", "bet365_name2"]).reset_index(drop=True)
    except Exception as exception:
        print("Ocorreu algum erro durante a requisição de dados da BET365\n\n")
        print("Mais informações:\n", exception)
        driver.quit()