import requests
from lxml import html
from pprint import pprint
from datetime import date
from pymongo import MongoClient

# creating a mongodb client and database
client = MongoClient('localhost', 27017)
db_name = 'news'
db = client[db_name]
data = db.data
data.drop()

# getting news from lenta.ru
main_link = 'https://lenta.ru'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'}

response = requests.get(main_link, headers=headers)
dom = html.fromstring(response.text)

lenta_news = dom.xpath('//div[@class="b-yellow-box__wrap"]/div[@class="item"]/a')
news = []

for item in lenta_news:
    item_dict = dict()
    item_link = item.xpath('./@href')[0]
    title = item.xpath('./text()')[0]
    item_date = '.'.join(item_link.split('/')[2:5][::-1])
    source = 'lenta.ru'

    item_dict['title'] = title
    item_dict['link'] = main_link + item_link
    item_dict['date'] = item_date
    item_dict['source'] = source

    news.append(item_dict)

# # getting news from yandex.ru
main_link = 'https://yandex.ru/'
response = requests.get(main_link, headers=headers)
dom = html.fromstring(response.text)

yandex_news = dom.xpath('//ol/li/a')

for item in yandex_news:
    item_dict = dict()
    item_link = item.xpath('./@href')[0]
    source = item.xpath('./span/div/object/@title')[0]
    title = item.xpath('./span/span/text()')[0]
    item_date = date.today().strftime("%d.%m.%Y")

    item_dict['title'] = title
    item_dict['link'] = item_link
    item_dict['date'] = item_date
    item_dict['source'] = source

    news.append(item_dict)

pprint(news)
data.insert_many(news)

