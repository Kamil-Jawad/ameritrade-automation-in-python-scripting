import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import lxml


def get_placed_orders():
    # def set_driver():
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.maximize_window()  # For maximizing window
    print("Please wait while the website loads.")
    driver.implicitly_wait(20)

    driver.get("https://invest.ameritrade.com/grid/p/site")

    get_login = driver.find_element_by_class_name('cafeLoginButton')
    time.sleep(2)
    get_login.click()
    user_id = input('Please enter User Id : ')
    passward = input('please enter passward : ')
    id_input = driver.find_element_by_id('username0')
    id_input.send_keys(user_id)
    passward_input = driver.find_element_by_id('password1')
    passward_input.send_keys(passward)
    login_button = driver.find_element_by_id('accept')
    time.sleep(2)
    login_button.click()
    question = driver.find_element_by_css_selector(
        "input[value='Answer a security question']")
    time.sleep(2)
    question.click()
    click_answer = driver.find_element_by_id("accept")
    time.sleep(15)
    click_answer.click()

    click_to_save = driver.find_element_by_id("accept")
    time.sleep(10)
    click_to_save.click()
    # click_order = driver.find_element_by_id("dt4")
    # time.sleep(2)
    # click_order.click()

    time.sleep(33)
    order_details = driver.find_element_by_id("dt4")
    order_details.click()
    time.sleep(6)
    order_page = driver.find_element_by_css_selector(
        "h2 a[href='/grid/p/site#r=jPage/cgi-bin/apps/u/ConsolidatedOrderStatus']")
    order_page.click()
    time.sleep(2)

    # main element for order id,order status and order symbol
    data_main = driver.find_elements_by_css_selector(
        "tbody[class='orderDetail']")

    # extracting order ids
    order_id_list = []
    for order_id in data_main:
        ids = order_id.get_attribute('data-id')
        order_id_list.append(ids)

    # extracting order status
    status_data = []
    for status in data_main:
        status_list = status.find_element_by_css_selector(
            "tr > td[class='status']")
        status_data.append(status_list.text)

    # extracting order symbol
    symbol_data = []
    for symbol in data_main:
        symbol_list = symbol.find_element_by_css_selector(
            "tr > td[class='symbol']")
        symbol_data.append(symbol_list.text)

    # placed_orders = {}
    # for id1, status1, symbol1 in zip(order_id_list, status_data, symbol_data):
    #     placed_orders = {'order_id': [id1],
    #                      "order_status": [status1],
    #                      "order_symbol": [symbol1]}

    # print(placed_orders)
    placed_orders = [order_id_list, status_data, symbol_data]
    placed_orders_df = pd.DataFrame(placed_orders)
    placed_orders_df = placed_orders_df.T
    placed_orders_df = placed_orders_df.rename(
        columns={0: 'order_id', 1: 'status_data', 2: 'order_symbol'})
    return placed_orders_df
