import re
import pandas as pd
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer

add_printer(1)

def get_dataframe(query="*"):
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
    df = df.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x) if not re.match("CRIAR APOSTA", q) if not re.match("SO", q)  if not re.match(r'^\d+$', q)]))[[0, 1, 3, 4, 5]].rename( columns={0: "team1_name", 1: "team2_name", 3: "team1_odd", 4: "draw_odd", 5: "team2_odd"}).dropna().assign(team1_odd = lambda q:q.team1_odd.str.replace(",", "."), team2_odd=lambda q:q.team2_odd.str.replace(',', '.'),draw_odd=lambda q:q.draw_odd.str.replace(',', '.')).astype({'team1_odd': 'Float64', 'draw_odd': 'Float64', 'team2_odd': 'Float64'})
    return df.reset_index(drop=True)

try:
    driver = Driver(uc=True)
    driver.get(
        "https://sports.sportingbet.com/pt-br/sports/futebol-4/aposta/brasil-33/brasileir%C3%A3o-a-102838"
    )
    df = get_dataframe(query="ms-event")
except Exception as exception:
    print("Ocorreu algum erro durante a requisição de dados :(\n\n")
    print("Mais informações:\n", exception)