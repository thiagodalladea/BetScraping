import re
from kthread_sleep import sleep
from seleniumbase import Driver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer
add_printer(1)

def obter_dataframe(query="*"):
    df = pd.DataFrame()
    while df.empty:
        df = get_df(
            driver,
            By,
            WebDriverWait,
            expected_conditions,
            queryselector=query,
            with_methods=True,
        )
    return df

driver = Driver(uc=True)
driver.get("https://br.betano.com/live/")

while True:
    sleep(5)
    df_teams = obter_dataframe(query="a.tw-flex.tw-flex-row.tw-justify-start.tw-w-full.tw-h-full.tw-items-center.tw-no-underline.tw-cursor-pointer")
    df_teams = df_teams.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x)
        if not re.match(r"^\d$", q)
    ])).dropna().reset_index(drop=True)
    df_teams = df_teams.rename(columns={
        0: "betano_team1",
        1: "betano_team2",
    })
    df_odds = obter_dataframe(query="div.tw-w-full.tw-flex.tw-flex-row.tw-flex-1.tw-items-center.tw-justify-center")
    df_odds = df_odds.aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x)
        if re.match(r"^\d{1,3}\.\d{2}$", q)
    ])).reset_index(drop=True)
    df_odds = df_odds.rename(columns={
        0: "betano_odd1",
        1: "betano_odd2",
        2: "betano_odd3",
    })
    df_betano = pd.concat([df_teams, df_odds.reset_index(drop=True)], axis=1).dropna().sort_values(by=["betano_name1", "betano_name2"])
    print(df_betano)