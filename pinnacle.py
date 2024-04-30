import re
import pandas as pd
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer

add_printer(1)

def get_dataframe(query="*", selector="*"):
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
    df = df.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x)]))[[0, 1, 3, 4, 5]].rename( columns={0: "team1_name", 1: "team2_name", 3: "team1_odd", 4: "draw_odd", 5: "team2_odd"}).dropna().assign(team1_odd = lambda q:q.team1_odd.str.replace(",", "."), team2_odd=lambda q:q.team2_odd.str.replace(',', '.'),draw_odd=lambda q:q.draw_odd.str.replace(',', '.')).astype({'team1_odd': 'Float64', 'draw_odd': 'Float64', 'team2_odd': 'Float64'})
    return df.reset_index(drop=True)

try:
    driver = Driver(uc=True)
    driver.get(
        "https://pinnacle.com/pt/soccer/brazil-serie-a/matchups/#all"
    )
    df = get_dataframe(selector="style_row__yBzX8 style_row__12oAB")
except Exception as exception:
    print("Ocorreu algum erro durante a requisição de dados :(\n\n")
    print("Mais informações:\n", exception)