from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db_name = 'mail_ru'
db = client[db_name]
data = db.messages
data.drop()

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://mail.ru/')

login = driver.find_element_by_class_name('email-input')
login.send_keys('study.ai_172@mail.ru')
login.send_keys(Keys.ENTER)

password = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'password-input'))
        )

while True:
    try:
        password.send_keys('NextPassword172')
        password.send_keys(Keys.ENTER)
        break
    except:
        continue

messages = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'llc'))
        )
all_links = [message.get_attribute('href') for message in messages]

while True:
    last_message = messages[-1]
    actions = ActionChains(driver)

    actions.move_to_element(last_message)
    actions.perform()
    messages = driver.find_elements_by_class_name('llc')
    if messages[-1] == last_message:
        break
    links = [message.get_attribute('href') for message in messages]
    all_links += links

unique_links = list(set(all_links))
messages_list = []

for link in unique_links:
    message_dict = dict()
    driver.execute_script(f'''window.open("{link}","_blank");''')
    driver.switch_to.window(driver.window_handles[1])

    sender_date = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'letter__author'))
    )
    sender = sender_date.find_element_by_class_name('letter-contact').get_attribute('title')
    date = sender_date.find_element_by_class_name('letter__date').text
    title = driver.find_element_by_tag_name('h2').text
    message = driver.find_element_by_class_name('letter__body').text

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    message_dict['sender'] = sender
    message_dict['date'] = date
    message_dict['title'] = title
    message_dict['message_text'] = message
    messages_list.append(message_dict)

data.insert_many(messages_list)
driver.quit()
