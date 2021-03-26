from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import time
import json

client = MongoClient('localhost', 27017)
db_name = 'mvideo'
db = client[db_name]
data = db.top_sales
data.drop()

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.mvideo.ru/')

top = driver.find_element_by_xpath('//div[contains(@class, "gallery-layout_products")]')
items = top.find_elements_by_xpath(".//a[@class='fl-product-tile-title__link sel-product-tile-title']")

actions = ActionChains(driver)
actions.move_to_element(top).perform()


button = top.find_element_by_xpath('.//a[contains(@class,"next-btn")]')

while True:
    amount = len(items)

    button.click()
    actions.perform()
    time.sleep(1)

    items = top.find_elements_by_xpath(".//a[@class='fl-product-tile-title__link sel-product-tile-title']")
    if len(items) == amount:
        break

json_data = [json.loads(item.get_attribute('data-product-info')) for item in items]
data.insert_many(json_data)
driver.quit()
