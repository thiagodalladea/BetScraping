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
    # df = df.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x) if not re.match(r"\b\d{2}/\d{2}\b", q) if not re.match(r"\d{2}:\d{2}\b", q) if not re.match("AO VIVO", q) if not re.match("SO", q) if not re.match(r'^\d+$', q)]))
    return df.reset_index(drop=True)

def get_betano():
    try:
        driver = Driver(uc=True)
        sleep(2)
        driver.get(
            "https://br.betano.com/live/"
        )
        sleep(5)
        df = get_dataframe(driver)
        print("\nRequisição de dados da BETANO concluída com sucesso!\n")
        #driver.quit()
        return df
    except Exception as exception:
        print("Ocorreu algum erro durante a requisição de dados da BETANO\n\n")
        print("Mais informações:\n", exception)
        driver.quit()