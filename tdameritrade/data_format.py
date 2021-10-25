payload = {
    "orderType": "LIMIT",
    "price": "5.63",
    "session": "NORMAL",
    "duration": "DAY",
    "orderStrategyType": "SINGLE",
    "orderLegCollection": [
        {
            "instruction": "BUY",
            "quantity": 1,
            "instrument": {
                "symbol": "NOK",
                "assetType": "EQUITY"
            }
        }
    ]
}
# response =c.place_order(
#     config.account_id,
#     order_spec=payload)
print("data format: ", payload)
