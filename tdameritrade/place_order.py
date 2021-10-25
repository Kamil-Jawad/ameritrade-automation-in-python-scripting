import time
import datetime
from datetime import timedelta
from pandas._libs import indexing
from pandas.core.indexes.base import Index
from tda import auth, client
import config
import numpy as np
import pandas as pd
import json
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
# authenticate
try:
    c = auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # with webdriver.Chrome(executable_path=config.chromedriver_path) as driver:
    c = auth.client_from_login_flow(
        driver, config.api_key, config.redirect_uri, config.token_path)

path1 = input(
    "please enter your file path (must be one excel sheet at time) :")

df1 = pd.read_excel(
    path1)
# print(len(df1))
for i in range(len(df1)):
    # if str(df1["Price"].loc[i]) != "nan":
    #     df1["Price"].loc[i]

    # else:
    #     df1["Price"].loc[i] = None
    # else:
    #     pass
    payload = {
        "orderType": df1['Type'].loc[i],
        "price": None,
        # "price": df1['Price'].loc[i],
        # "price": df1['Price'].loc[i] if str(df1['Price'].loc[i]) != "nan" else None,
        "session": "NORMAL",
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {

                    # "BUY"
                    "instruction": df1["Direction"].loc[i],
                    "quantity": int(df1["Shares"].loc[i]),
                    "instrument": {
                        "symbol": df1["Stock"].loc[i],  # "RLGT"
                        "assetType": "EQUITY"
                    }
            }
        ]
    }

    response = c.place_order(
        config.account_id,
        order_spec=payload)
    print(payload)
    print(response.json)
    # print("stock placed")
# y=int(input("enter number : "))
# a_lambda_function = lambda x: x*2 if x < 3 else x
# x = 'nan'
# if (str(x) != 'nan'): x  else: None
# x = 6
# print(a_lambda_function(x))
