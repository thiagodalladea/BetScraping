import re
import pandas as pd
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer
from time import sleep

add_printer(1)

def get_dataframe(driver, query="*", selector="*"):
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
    # df = df.loc[df.aa_className==selector]
    # df = df.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x)]))[[0, 2, 13, 14]]\
    #     .rename( columns={0: "sportingbet_name1", 2: "sportingbet_name2", 13: "sportingbet_odd1", 14: "sportingbet_odd2"}).dropna()\
    #         .assign(sportingbet_odd1 = lambda q:q.sportingbet_odd1.str.replace(",", "."), sportingbet_odd2=lambda q:q.sportingbet_odd2.str\
    #             .replace(',', '.')).astype({'sportingbet_odd1': 'Float64', 'sportingbet_odd2': 'Float64'})
    return df.reset_index(drop=True)

def get_sporting_bet():
    try:
        driver = Driver(uc=True)
        sleep(2)
        driver.get(
            "https://sports.sportingbet.com/pt-br/sports/basquete-7/aposta/am%C3%A9rica-do-norte-9/nba-6004"
        )
        sleep(5)
        df = get_dataframe(driver)
        # driver, selector="grid-event grid-six-pack-event ms-active-highlight two-lined-name ng-star-inserted"
        driver.quit()
        return df
    except Exception as exception:
        print("Ocorreu algum erro durante a requisição de dados da BETANO\n\n")
        print("Mais informações:\n", exception)
        driver.quit()