from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json
import tda
import time
from datetime import date
from genericpath import exists
from pandas.core.arrays.categorical import contains
from tda import auth, client
import config
import pandas as pd
from pandas.core.common import SettingWithCopyWarning
import warnings
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

# authenticate
try:
    c = auth.client_from_token_file(
        config.token_path, config.api_key)
except FileNotFoundError:
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # with webdriver.Chrome(executable_path=config.chromedriver_path) as driver:
    c = auth.client_from_login_flow(
        driver, config.api_key, config.redirect_uri, config.token_path)

# Function that get the file


def get_user_file():
    path1 = input(
        "please enter your file path (must be one excel sheet at time) :")
    df1 = pd.read_excel(path1)
    return df1


# calling the function
df1 = get_user_file()
# converting the file into Dataframe
df_output = pd.DataFrame(df1)
# print(df_output)
index = len(df_output['Stock_List'])-1
# getting history from api
for Stock_individual in enumerate(df_output['Stock_List']):
    history = c.get_price_history(Stock_individual[1],
                                  period_type=client.Client.PriceHistory.PeriodType.DAY,
                                  period=client.Client.PriceHistory.Period.ONE_DAY,
                                  frequency_type=client.Client.PriceHistory.FrequencyType.DAILY.MINUTE,
                                  frequency=client.Client.PriceHistory.Frequency.DAILY)

    # print(json.dumps(hist.json(), indent=4))
    history = history.json()
    # Dictionary to store the history given by the api
    history_dict = {'Date': [],
                    'Open': [],
                    'High': [],
                    'Low': [],
                    'Close': [],
                    'Volume': []}
    # Getting the result one by one and append into the dictionary
    for hist in history['candles']:
        # convert the datatime into proper data time format
        date_time = pd.to_datetime(hist['datetime'], unit='ms')
        # date_time = date_time.strftime('%m/%d/%Y %I:%M') # datetime
        date_time = date_time.strftime('%I:%M')  # only time
        history_dict['Date'].append(date_time)
        history_dict['Open'].append(hist['open'])
        history_dict['High'].append(hist['high'])
        history_dict['Low'].append(hist['low'])
        history_dict['Close'].append(hist['close'])
        history_dict['Volume'].append(hist['volume'])
    # convert into dataframe
    df_stock = pd.DataFrame(history_dict)
    # appling conditions
    exists = '09:30' not in df_stock['Date']
    if exists == True:
        df_output['List_2'][Stock_individual[0]] = Stock_individual[1]
        df_output['bmo_high_2'][Stock_individual[0]] = '09:30 n/a'
        df_output['bmo_vol_2'][Stock_individual[0]] = '09:30 n/a'
    # slicing data until and not including '09:30'
    df_stock_date = df_stock[df_stock['Date'] < '09:30']
    # sum of column Volume until and not included '09:30'
    bmo_vol = df_stock_date['Volume'].sum()
    # High of column High until and not included '09:30'
    bmo_high = df_stock_date['High'].max()
    # print(df_output.columns[6])
    if (bmo_high > 1.00) & (bmo_vol > 250000):
        df_output['List_1'][Stock_individual[0]] = Stock_individual[1]
        df_output['bmo_high_1'][Stock_individual[0]] = bmo_high
        df_output['bmo_vol_1'][Stock_individual[0]] = bmo_vol
    else:
        index = index+1
        df_output.loc[index, df_output.columns[6]] = Stock_individual[1]
        df_output.loc[index, df_output.columns[7]] = bmo_high
        df_output.loc[index, df_output.columns[8]] = bmo_vol
time.sleep(3)
df_output.to_excel('output_'+str(date.today())+'.xlsx')
