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

def get_dataframe(driver, query="*"):
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
    df = df.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x) if not re.match("CRIAR APOSTA", q) if not re.match("SO", q)  if not re.match(r'^\d+$', q)]))[[0, 1, 3, 4, 5]].rename( columns={0: "sportingbet_name1", 1: "sportingbet_name2", 3: "sportingbet_odd1", 4: "sportingbet_odd2", 5: "sportingbet_odd3"}).dropna().assign(sportingbet_odd1 = lambda q:q.sportingbet_odd1.str.replace(",", "."), sportingbet_odd2=lambda q:q.sportingbet_odd2.str.replace(',', '.'),sportingbet_odd3=lambda q:q.sportingbet_odd3.str.replace(',', '.')).astype({'sportingbet_odd1': 'Float64', 'sportingbet_odd3': 'Float64', 'sportingbet_odd2': 'Float64'})
    return df.reset_index(drop=True)

def get_sporting_bet():
    try:
        driver = Driver(uc=True)
        sleep(2)
        driver.get(
            "https://sports.sportingbet.com/pt-br/sports/futebol-4/aposta/brasil-33/brasileir%C3%A3o-a-102838"
        )
        sleep(5)
        df = get_dataframe(driver, query="ms-event")
        print("\nRequisição de dados da SPORTING BET concluída com sucesso!\n")
        driver.quit()
        df['sportingbet_name1'] = df['sportingbet_name1'].str.replace('RB ', '')
        df['sportingbet_name2'] = df['sportingbet_name2'].str.replace('RB ', '')
        df['sportingbet_name1'] = df['sportingbet_name1'].str.replace('Vasco ', 'Vasco da Gama')
        df['sportingbet_name2'] = df['sportingbet_name2'].str.replace('Vasco', 'Vasco da Gama')
        return df.sort_values(by=["sportingbet_name1", "sportingbet_name2"]).reset_index(drop=True)
    except Exception as exception:
        print("Ocorreu algum erro durante a requisição de dados da SPORTING BET\n\n")
        print("Mais informações:\n", exception)
        driver.quit()