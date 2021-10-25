from pandas._libs import indexing
from pandas.core.indexes.base import Index
from tda import auth, client
import config
import json
import pandas as pd
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


# r = c.get_price_history('AAPL',
#                         period_type=client.Client.PriceHistory.PeriodType.YEAR,
#                         period=client.Client.PriceHistory.Period.TWENTY_YEARS,
#                         frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
#                         frequency=client.Client.PriceHistory.Frequency.DAILY)

# print(json.dumps(r.json(), indent=4))

# get a stock quote
sym = {'symbols': ['AAPL', 'NOC', 'ZOM', 'SNDL']}
sym = pd.DataFrame(sym)
# print(sym)
for i in range(len(sym)):
    response = c.get_quotes(symbols=sym['symbols'].loc[i])
    x = response.json()
    # x = dict(x)
    print(x)
    print("\n################\n")
    current_stock_price = x[sym['symbols'].iloc[i]]['closePrice']
    print(current_stock_price)

# print(x['AAPL']['assetType'])

# print(response.json())

# get stock fundamental data
# response = c.search_instruments(
#     ['AAPL', 'BA'], c.Instrument.Projection.FUNDAMENTAL)

# print(json.dumps(response.json(), indent=4))

# # get option chain
# response = c.get_option_chain('AAPL')

# print(json.dumps(response.json(), indent=4))

# # get all call options
# response = c.get_option_chain(
#     'AAPL', contract_type=c.Options.ContractType.CALL)

# print(json.dumps(response.json(), indent=4))

# # get call options for a specific strike
# response = c.get_option_chain(
#     'AAPL', contract_type=c.Options.ContractType.CALL, strike=300)

# print(json.dumps(response.json(), indent=4))

#########

 # else:
    #     payload = {
    #         "orderType": df1['Type'].iloc[i],

    #         "price": df1['Price'].iloc[i] if str(df1['Price'].iloc[i]) == 'nan' else None,
    #         "session": "NORMAL",
    #         "duration": "DAY",
    #         "orderStrategyType": "SINGLE",
    #         "orderLegCollection": [
    #             {

    #                 # "BUY"
    #                 "instruction": df1["Direction"].iloc[i],
    #                 "quantity": int(df1["Shares"].iloc[i]),
    #                 "instrument": {
    #                     "symbol": df1["Stock"].iloc[i],  # "RLGT"
    #                     "assetType": "EQUITY"
    #                 }
    #             }
    #         ]
    #     }

    #     response = c.place_order(
    #         config.account_id,
    #         order_spec=payload)
