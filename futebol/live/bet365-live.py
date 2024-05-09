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
driver.get("https://www.bet365.com/#/IP/B1")

while True:
    sleep(5)
    df_bet365 = obter_dataframe(query="div.ovm-Fixture_Container")
    df_bet365 = df_bet365.loc[df_bet365.aa_innerText.str.split("\n").str[2:].apply(
        lambda x: True if re.match(r"^[\d:]+Ç\d+Ç\d+Ç\d+Ç[\d.]+Ç[\d.]", "Ç".join(x)) else False)
    ].aa_innerText.str.split(
        "\n").apply(pd.Series).reset_index(drop=True)
    df_bet365 = df_bet365[[0, 1, 2, 6, 7, 8]]
    df_bet365 = df_bet365.rename(columns={
        0: "bet365_team1",
        1: "bet365_team2",
        2: "time",
        6: "bet365_odd1",
        7: "bet365_ood2",
        8: "bet365_odd3"
    }).sort_values(by=["bet365_name1", "bet365_name2"])
    print(df_bet365)