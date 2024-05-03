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

def obter_dataframe(query='*'):
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
dfc = obter_dataframe()
dfc.loc[dfc.aa_classList.str.contains(
    'iip-IntroductoryPopup_Cross', regex=False, na=False)].se_click.iloc[0]()
sleep(2)
dfc.loc[dfc.aa_classList.str.contains(
    'ccm-CookieConsentPopup_Accept', regex=False, na=False)].se_click.iloc[0]()
df = obter_dataframe(query='div.ovm-Fixture_Container')
df.loc[df.aa_innerText.str.split('\n').str[2:].apply(
    lambda x: True if re.match(r'^[\d:]+Ç\d+Ç\d+Ç\d+Ç[\d.]+Ç[\d.]', 'Ç'.join(x)) else False)
].aa_innerText.str.split(
    '\n').apply(pd.Series).reset_index(drop=True)
df = df.dropna(subset="aa_innerText").aa_innerText.apply(lambda x: pd.Series([q for q in re.split(r"[\n]", x) if not re.match(r"\d{2}:\d{2}\b", q) if not re.search(r"\bGol\b", q)]))\
    [[0, 1, 5, 6, 7]].rename( columns={0: "bet365_name1", 1: "bet365_name2", 5: "bet365_odd1", 6: "bet365_odd2", 7: "bet365_odd3"}).dropna()
print(df)