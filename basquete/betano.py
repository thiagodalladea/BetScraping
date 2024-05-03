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
    df = df.loc[df.aa_className==selector]
    df = df.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x)\
        if not re.match(r"\b\d{2}/\d{2}\b", q) if not re.match(r"\d{2}:\d{2}\b", q) if not re.match("AO VIVO", q) if not re.match("SO", q)]))\
            [[0, 1, 4, 6]].rename( columns={0: "betano_name1", 1: "betano_name2", 4: "betano_odd1", 6: "betano_odd2"})\
                .dropna().assign(betano_odd1 = lambda q:q.betano_odd1.str.replace(",", "."), betano_odd2=lambda q:q.betano_odd2.str.replace(',', '.'))\
                    .astype({'betano_odd1': 'Float64', 'betano_odd2': 'Float64'})
    return df.reset_index(drop=True)

def get_betano():
    try:
        driver = Driver(uc=True)
        sleep(2)
        driver.get(
            "https://br.betano.com/sport/basquete/eua/nba/441g/"
        )
        sleep(5)
        df = get_dataframe(driver, selector="vue-recycle-scroller__item-view")
        driver.quit()
        return df
    except Exception as exception:
        print("Ocorreu algum erro durante a requisição de dados da BETANO\n\n")
        print("Mais informações:\n", exception)
        driver.quit()