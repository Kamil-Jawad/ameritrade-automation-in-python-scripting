import datetime
from datetime import timedelta
from pandas._libs import indexing
# from pandas._libs.tslibs import Day
from pandas.core.indexes.base import Index
from tda import auth, client
import config
import numpy as np
import pandas as pd
import tda
import json
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
# authenticate
try:
    c = auth.client_from_token_file(
        config.token_path, config.api_key)
except FileNotFoundError:
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # with webdriver.Chrome(executable_path=config.chromedriver_path) as driver:
    c = auth.client_from_login_flow(
        driver, config.api_key, config.redirect_uri, config.token_path)

# function for getting position symbol from api


def api_position_fun():
    api_positions = c.get_account(config.account_id, fields=['positions'])
    api_positions = api_positions.json()
    position = api_positions["securitiesAccount"]["positions"]
    position_list = {'api_position': []}
    for pos in position:
        position_list['api_position'].append(pos["instrument"]["symbol"])
    position_list = pd.DataFrame(position_list)
    return position_list


api_position_data = api_position_fun()
# print(api_position_data)
# getting file from user


def get_user_file():
    path1 = input(
        "please enter your file path (must be one excel sheet at time) :")
    df1 = pd.read_excel(path1)
    return df1


# calling the function
df1 = get_user_file()

# function for getting orders from api


def orders_api_fun():
    # yesterday = datetime.datetime.now() - timedelta(days=1)
    # year = yesterday.strftime('%Y')
    # month = yesterday.strftime('%m')
    # day = yesterday.strftime('%d')
    # yesterday_date = datetime.datetime(int(year), int(month), int(day))
  # print(yesterday_date)
  # print(datetime.datetime.now())
    get_order_details = c.get_orders_by_path(config.account_id,  max_results=None, from_entered_datetime=datetime.datetime.now(),
                                             to_entered_datetime=datetime.datetime.now(), status=None, statuses=None)
    order_api = get_order_details.json()
    # for i in order_api:
    #     print()
    #     print(i)

# orders_api_fun()
    order_api_data = {"api_orderType": [],
                      "api_order_id": [],
                      "api_order_status": [],
                      "api_order_symbol": [],
                      "api_order_price": [],
                      "api_order_instruction": []}

    for orders in order_api:

        order_api_data['api_orderType'].append(orders['orderType'])

        order_api_data['api_order_id'].append(orders['orderId'])

        order_api_data['api_order_status'].append(orders['status'])

        [order_api_data['api_order_symbol'].append(
            x['instrument']['symbol']) for x in orders['orderLegCollection']]

        [order_api_data["api_order_instruction"].append(
            y["instruction"]) for y in orders['orderLegCollection']]

        if orders["orderType"] == "LIMIT":
            order_api_data["api_order_price"].append(orders["price"])

        elif (orders["orderType"] == "MARKET") and (orders["status"] == "CANCELED" or orders["status"] == "REJECTED" or orders["status"] == "QUEUED"):
            l = 0.0
            order_api_data["api_order_price"].append(l)

        elif (orders["orderType"] == "MARKET") and (orders["status"] != "CANCELED" or orders["status"] != "REJECTED" or orders["status"] != "QUEUED"):
            for p in orders['orderActivityCollection']:
                [order_api_data["api_order_price"].append(
                    d["price"]) for d in p['executionLegs']]
        elif (orders["orderType"] == "MARKET") and (orders["status"] == "FILLED"):
            l = 0.0
            order_api_data["api_order_price"].append(l)
        elif(orders["orderType"] == "STOP") or (orders["status"] != "EXPIRED"):
            order_api_data["api_order_price"].append(orders["stopPrice"])

    # print(order_api_data)
    order_api_df = pd.DataFrame(order_api_data)
    return order_api_df


# calling the function
order_api_df = orders_api_fun()
# print(order_api_df)

# try:
for i in range(len(df1)):

    for j in range(len(order_api_df)):
        if str(df1["Price"].iloc[i]) == 'nan':
            df1["Price"].iloc[i] = 0.0
            # print(df1["Price"].iloc[i])
        else:
            # print(df1["Price"].iloc[i])
            pass
        if df1['Action'].iloc[i] == 'Cancel':
            if (order_api_df['api_order_status'].iloc[j] == 'QUEUED') and (df1['Stock'].iloc[i] == order_api_df['api_order_symbol'].iloc[j]):
                cancel_response = c.cancel_order(
                    order_api_df['api_order_id'].iloc[j], config.account_id)
                break

        elif (df1['Action'].iloc[i] == 'Initiate') and (df1['Direction'].iloc[i] == 'Buy') and (df1['Type'].iloc[i] == 'Market'):
            for pos in range(len(api_position_data)):
                # Nick edits --------
                if df1['Stock'].iloc[i] == api_position_data["api_position"].iloc[pos]:
                    continue

                elif df1['Stock'].iloc[i] == order_api_df['api_order_symbol'].iloc[j] and order_api_df['api_order_status'].iloc[j] == 'FILLED':
                    continue
                # ---------------
            if (df1['Stock'].iloc[i] == order_api_df['api_order_symbol'].iloc[j]) and (order_api_df['api_order_status'].iloc[j] == 'QUEUED') or (df1['Direction'].iloc[i] == order_api_df["api_order_instruction"].iloc[j]):

                payload = {
                    "orderType": df1['Type'].iloc[i],
                    "price": df1["Price"].iloc[i],
                    "session": "NORMAL",
                    "duration": "DAY",
                    "orderStrategyType": "SINGLE",
                    "orderLegCollection": [
                        {

                                # "BUY"
                                "instruction": df1["Direction"].iloc[i],
                                "quantity": int(df1["Shares"].iloc[i]),
                            "instrument": {
                                    # "RLGT"
                                    "symbol": df1["Stock"].iloc[i],
                                    "assetType": "EQUITY"
                                }
                        }
                    ]
                }

                response = c.replace_order(
                    config.account_id, order_api_df['api_order_id'][j], order_spec=payload)
                break
            else:
                payload = {
                    "orderType": "Market",

                    "price": None,
                    "session": "NORMAL",
                    "duration": "DAY",
                    "orderStrategyType": "SINGLE",
                    "orderLegCollection": [
                        {

                            # "BUY"
                            "instruction": df1["Direction"].iloc[i],
                            "quantity": int(df1["Shares"].iloc[i]),
                            "instrument": {
                                # "RLGT"
                                "symbol": df1["Stock"].iloc[i],
                                "assetType": "EQUITY"
                            }
                        }
                    ]
                }

                response = c.place_order(
                    config.account_id,
                    order_spec=payload)
                break
                # done
# ---------------------------------------------------------------------------------------------------------------
        elif (df1['Action'].iloc[i] == 'Initiate') and (df1['Direction'].iloc[i] == 'Buy') and (df1['Type'].iloc[i] == 'Stop'):
            # getting current stock price
            response = c.get_quotes(symbols=df1['Stock'].iloc[i])
            x = response.json()
            print(x)
            current_stock_price = x[df1['Stock'].iloc[i]
                                    ]['closePrice']
            for pos in range(len(api_position_data)):
                # Nick edits ----
                # If Stock in Open_Positions:
                if df1['Stock'].iloc[i] == api_position_data["api_position"].iloc[pos]:
                    continue
                # If Stock in Competed_Orders:
                elif df1['Stock'].iloc[i] == order_api_df['api_order_symbol'].iloc[j] and order_api_df['api_order_status'].iloc[j] == 'FILLED':
                    continue
                # -----
            if (df1['Stock'].loc[i] == order_api_df['api_order_symbol'].loc[j]) and (order_api_df['api_order_status'].loc[j] == 'QUEUED') and (df1['Direction'].loc[i] == order_api_df["api_order_instruction"].loc[j]):
                if (order_api_df["api_order_price"].loc[j]) == (df1['Price'].loc[i]):
                    continue
                # done
                else:
                    # this order cancel logic is as per your direction in 1st logic word file,,,but trade.py file(you send us after for revision)
                    # you wrote this piece of cancel order in the if(current_stock_price.=df1['Price']/I;pc[I]): condition.....
                    # please check if I am placing this code is at right place or you can cut and past it in if condtion,
                    # but I write this code as per your 1st logic file

                    cancel_response = c.cancel_order(
                        order_api_df['api_order_id'].iloc[j], config.account_id)

                    # You set this in your current logic file if(current_stock_price>df1['Price'].iloc[I]) but
                    # in your revision trade.py you set this >=, so I did as per your revision trade.py,,now you can check and adjust as per your need

                    if (current_stock_price >= df1['Price'].iloc[i]):
                        payload = {
                            "orderType": "Market",

                            "price": None,
                            "session": "NORMAL",
                            "duration": "DAY",
                            "orderStrategyType": "SINGLE",
                            "orderLegCollection": [
                                {

                                    # "BUY"
                                    "instruction": df1["Direction"].iloc[i],
                                    "quantity": int(df1["Shares"].iloc[i]),
                                    "instrument": {
                                        # "RLGT"
                                        "symbol": df1["Stock"].iloc[i],
                                        "assetType": "EQUITY"
                                    }
                                }
                            ]
                        }

                        response = c.place_order(
                            config.account_id,
                            order_spec=payload)
                        break
                    else:
                        payload = {
                            "orderType": df1['Type'].iloc[i],
                            # in the first file you sent us for revision the price we have set to None but now in revision we pick the price from file
                            # now the order is replace as per from the excel sheet(as per your direction in second login file)
                            "price": None,
                            "session": "NORMAL",
                            "duration": "DAY",
                            "orderStrategyType": "SINGLE",
                            "orderLegCollection": [
                                {

                                        # "BUY"
                                        "instruction": df1["Direction"].iloc[i],
                                        "quantity": int(df1["Shares"].iloc[i]),
                                    "instrument": {
                                            # "RLGT"
                                            "symbol": df1["Stock"].iloc[i],
                                            "assetType": "EQUITY"
                                        }
                                }
                            ]
                        }
                        #  replacing the order as per your second login file
                        response = c.replace_order(
                            config.account_id, order_api_df['api_order_id'][j], order_spec=payload)
                        break
            else:
                if (current_stock_price >= df1['Price'].iloc[i]):
                    payload = {
                        "orderType": "Market",

                        "price": None,
                        "session": "NORMAL",
                        "duration": "DAY",
                        "orderStrategyType": "SINGLE",
                        "orderLegCollection": [
                            {

                                # "BUY"
                                "instruction": df1["Direction"].iloc[i],
                                "quantity": int(df1["Shares"].iloc[i]),
                                "instrument": {
                                    # "RLGT"
                                    "symbol": df1["Stock"].iloc[i],
                                    "assetType": "EQUITY"
                                }
                            }
                        ]
                    }

                    response = c.place_order(
                        config.account_id,
                        order_spec=payload)
                    break
                else:
                    payload = {
                        "orderType": df1['Type'].iloc[i],
                        # placing the stop buy order at the price from excel sheet
                        "price": df1['Price'].iloc[i],
                        "session": "NORMAL",
                        "duration": "DAY",
                        "orderStrategyType": "SINGLE",
                        "orderLegCollection": [
                            {

                                    # "BUY"
                                    "instruction": df1["Direction"].iloc[i],
                                    "quantity": int(df1["Shares"].iloc[i]),
                                "instrument": {
                                        # "RLGT"
                                        "symbol": df1["Stock"].iloc[i],
                                        "assetType": "EQUITY"
                                    }
                            }
                        ]
                    }

                    response = c.place_order(
                        config.account_id,
                        order_spec=payload)
                    break

# # saving into file
order_api_df = orders_api_fun()
api_position = api_position_fun()
order_api_df = order_api_df.join(api_position["api_position"])
order_api_df.to_excel('api_data.xlsx')
# print("Success")
# except:
#     print("There is an error (error maybe in file or in file path or maybe in stocks) please check and try again")
