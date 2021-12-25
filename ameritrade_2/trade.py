# from datetime import datetime
import datetime
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
# print(df_output)ff
index = len(df_output['Stock_List'])-1
# getting history from api

# getting today date
x = datetime.datetime.now()
today_datetime = x.strftime('%Y-%m-%d %I:%M:%S')
dt_obj = datetime.datetime.strptime(today_datetime, '%Y-%m-%d %I:%M:%S')
millisec_datetime_today = dt_obj.timestamp() * 1000
millisec_datetime_today = int(millisec_datetime_today)
today_date = x.strftime('%m-%d-%Y')  # getting date
# getting tomorrow date
tomorrowtimestamp = datetime.datetime.now() + datetime.timedelta(days=1)
tomorrow = pd.to_datetime(tomorrowtimestamp)
millisec_datetime_tomorrow = tomorrow.timestamp() * 1000
millisec_datetime_tomorrow = int(millisec_datetime_tomorrow)

for Stock_individual in enumerate(df_output['Stock_List']):
    print(Stock_individual[1])
    history = c.get_price_history(Stock_individual[1],
                                  #  provide default values
                                  #   period_type=client.Client.PriceHistory.PeriodType.DAY,
                                  #   period=client.Client.PriceHistory.Period.ONE_DAY,
                                  frequency_type=client.Client.PriceHistory.FrequencyType.DAILY.MINUTE,
                                  frequency=client.Client.PriceHistory.Frequency.DAILY,
                                  end_datetime=pd.to_datetime(
                                      millisec_datetime_tomorrow, unit='ms'),
                                  #   end_datetime=1640384987468,
                                  # to uncomment this line please comment all other
                                  start_datetime=pd.to_datetime(
                                      millisec_datetime_today, unit='ms'),
                                  # start_datetime=1640298625751
                                  # parameters and uncomment line from 47 to 48
                                  )

    # print(json.dumps(hist.json(), indent=4))
    print(history.json)
    history = history.json()
    # print('fresh history : ', history)

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
        complete_datetime = pd.to_datetime(hist['datetime'], unit='ms')
        only_date = complete_datetime.strftime('%m-%d-%Y')  # date
        # print(only_date)
        # if (only_date == today_date):  # comparing to get current day, you can also remove this condition
        # print('true')
        only_time = complete_datetime.strftime('%I:%M')  # only time
        history_dict['Date'].append(only_time)
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
        # print('yes exists')
        df_output['List_2'][Stock_individual[0]] = Stock_individual[1]
        df_output['bmo_high_2'][Stock_individual[0]] = '09:30 n/a'
        df_output['bmo_vol_2'][Stock_individual[0]] = '09:30 n/a'
    # slicing data until and not including '09:30'

    new_time_df = df_stock[df_stock['Date'] < '09:30']
    # print('df_stock ::', df_stock.shape)
    # print('new_time_df ::', new_time_df.shape)

    # sum of column Volume until and not included '09:30'
    bmo_vol = new_time_df['Volume'].sum()
    # High of column High until and not included '09:30'
    bmo_high = new_time_df['High'].max()
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
try:
    df_output.to_excel('output_'+str(date.today())+'.xlsx')
    print("file saved successful")
except:
    print("failed to save the file")


# %%

Date_Time = pd.to_datetime(1639086231562)
Date_Time


# %%
tomorrowtimestamp = datetime.datetime.now() + datetime.timedelta(days=1)
tomorrow = pd.to_datetime(tomorrowtimestamp)
miliisec_tomorrow_datetime = tomorrow.timestamp() * 1000
# print(tomorrow)
print(miliisec_tomorrow_datetime)
int(miliisec_tomorrow_datetime)
# millisec_today_date = x.strftime('%m-%d-%Y')

# %%
pd.to_datetime(1639913568168, unit='ms')

# %%
x = datetime.datetime.now()
# print(x)
# today_datetime = x.strftime('%Y-%m-%d %I:%M:%S')
# dt_obj = datetime.strptime(today_datetime, '%Y-%m-%d %I:%M:%S')
x = pd.to_datetime(x)
millisec = x.timestamp() * 1000
print(millisec)
# pd.to_datetime(int(millisec))
# %%
y = '2021-12-02 21:26:24.514000'
y = pd.to_datetime(y)
milli_y = y.timestamp() * 1000
print(milli_y)


# %%
tomorrowtimestamp = datetime.datetime.now() - datetime.timedelta(days=6)
tomorrow = pd.to_datetime(tomorrowtimestamp)
miliisec_tomorrow_datetime = tomorrow.timestamp() * 1000
print(miliisec_tomorrow_datetime)
int(miliisec_tomorrow_datetime)
# %%
d = '09:30'
print('timestamp')
d = pd.to_datetime(d)
d
