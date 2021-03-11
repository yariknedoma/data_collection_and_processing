"""
2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
Найти среди них любое, требующее авторизацию (любого типа).
Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
"""
# youtube api, для получения статистики о канале по его id

from googleapiclient.discovery import build

api_key = 'AIzaSyBL0v6PLAzEXlzjXjqSdd-MPUr1YsJT4jQ'
service = build('youtube', 'v3', developerKey=api_key)

request = service.channels().list(part='statistics', id='UCSJ4gkVC6NrvII8umztf0Ow')

response = request.execute()

items = response.get('items')
statistics = items[0].get('statistics')

for i, items in enumerate(statistics.items()):
    print(f'{i+1}. {items[0]}: {items[1]}')
