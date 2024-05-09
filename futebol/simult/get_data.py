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
from betano import format_betano
from sporting_bet import format_sportingbet
from bet365 import format_bet365_teams, format_bet365_odds

def get_data(driver, name, query):
    if name == "betano":
        sleep(3)
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
        df = format_betano(df)
        return df
    elif name == "sportingbet":
        sleep(3)
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
        df = format_sportingbet(df)
        return df
    elif name == "bet365":
        sleep(3)
        dfs = []
        for part_query in query:
            df = pd.DataFrame()
            while df.empty:
                df = get_df(
                    driver,
                    By,
                    WebDriverWait,
                    expected_conditions,
                    queryselector = part_query,
                    with_methods = True,
                )
            dfs.append(df)
        df_teams = format_bet365_teams(dfs[0])
        df_odds = format_bet365_odds(dfs[1])
        df = pd.concat([df_teams, df_odds.reset_index(drop=True)], axis=1)
        df = df.sort_values(by=["bet365_name1", "bet365_name2"])
        return df