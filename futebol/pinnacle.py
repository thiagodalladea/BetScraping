import re
import pandas as pd
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer
from time import sleep
from rename import rename

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
    df = df.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x)
        if not re.match(r".*?(\d+:\d+)", q)
        if not re.match(r"-\d+\.\d+", q)
        if not re.match(r"^\d+$", q)
        if not re.match(r"[^()]+ metade - \d+\"", q)
        if not re.match(r"Intervalo", q)]))[[0, 1, 2, 3, 4]].rename(columns={
            0: "pinnacle_name1",
            1: "pinnacle_name2",
            2: "pinnacle_odd1",
            3: "pinnacle_odd2",
            4: "pinnacle_odd3"}).dropna().assign(pinnacle_odd1 = lambda q:q.pinnacle_odd1.str.replace(",", "."),
                pinnacle_odd2=lambda q:q.pinnacle_odd2.str.replace(",", "."),
                pinnacle_odd3=lambda q:q.pinnacle_odd3.str.replace(",", ".")).astype({
                    "pinnacle_odd1": "Float64",
                    "pinnacle_odd3": "Float64",
                    "pinnacle_odd2": "Float64"
                })

    return df.reset_index(drop=True)

def get_pinnacle():
    try:
        driver = Driver(uc=True)
        sleep(2)
        driver.get(
            "https://pinnacle.com/pt/soccer/brazil-serie-a/matchups/#all"
        )
        sleep(3)
        df = get_dataframe(driver, query="div.style_row__12oAB")
        driver.quit()
        df["pinnacle_name1"] = df["pinnacle_name1"].str.replace(" (Jogo/Partida)", "")
        df["pinnacle_name2"] = df["pinnacle_name2"].str.replace(" (Jogo/Partida)", "")
        df["pinnacle_name1"] = df["pinnacle_name1"].apply(rename)
        df["pinnacle_name2"] = df["pinnacle_name2"].apply(rename)
        print("\nRequisição de dados da PINNACLE concluída com sucesso!\n")

        return df.sort_values(by=["pinnacle_name1", "pinnacle_name2"]).reset_index(drop=True)
    except Exception as exception:
        print("Ocorreu algum erro durante a requisição de dados da PINNACLE\n\n")
        print("Mais informações:\n", exception)
        driver.quit()