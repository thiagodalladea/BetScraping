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

def get_dataframe(driver, query="*"):
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

driver_bet365 = Driver(uc=True)
driver_bet365.get("https://www.bet365.com/#/IP/B1")
driver_betano = Driver(uc=True)
driver_betano.get("https://br.betano.com/live/")

while True:
    sleep(7)

    # BET365
    df_bet365 = get_dataframe(driver_bet365, query="div.ovm-Fixture_Container")
    df_bet365 = df_bet365.loc[df_bet365.aa_innerText.str.split("\n").str[2:].apply(
        lambda x: True if re.match(r"^[\d:]+Ç\d+Ç\d+Ç\d+Ç[\d.]+Ç[\d.]", "Ç".join(x)) else False)
    ].aa_innerText.str.split(
        "\n").apply(pd.Series).reset_index(drop=True)
    df_bet365 = df_bet365[[0, 1, 6, 7, 8]]
    df_bet365 = df_bet365.rename(columns={
        0: "bet365_team1",
        1: "bet365_team2",
        6: "bet365_odd1",
        7: "bet365_ood2",
        8: "bet365_odd3"
    }).sort_values(by=["bet365_team1", "bet365_team2"])
    print(df_bet365)

    # BETANO
    df_teams = get_dataframe(driver_betano, query="div.tw-w-full.tw-flex.tw-flex-col.tw-items-start.tw-justify-center.tw-truncate")
    df_teams = df_teams.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x)
        if not re.match(r"^\d$", q)
    ])).dropna().reset_index(drop=True)
    df_teams = df_teams.rename(columns={
        0: "betano_team1",
        1: "betano_team2",
    })
    df_odds = get_dataframe(driver_betano, query="div.tw-w-full.tw-flex.tw-flex-row.tw-flex-1.tw-items-center.tw-justify-center")
    df_odds = df_odds.aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x)
        if re.match(r"^\d{1,3}\.\d{2}$", q)
    ])).reset_index(drop=True)
    df_odds = df_odds.rename(columns={
        0: "betano_odd1",
        1: "betano_odd2",
        2: "betano_odd3",
    })
    df_betano = pd.concat([df_teams, df_odds.reset_index(drop=True)], axis=1).dropna().sort_values(by=["betano_team1", "betano_team2"])
    print(df_betano)

    # BETFAIR