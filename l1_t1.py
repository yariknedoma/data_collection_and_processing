"""
1. Посмотреть документацию к API GitHub,
разобраться как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json.
"""

import requests
import json

service = 'https://api.github.com'
username = 'yariknedoma'
url = '/users/' + username + '/repos'
full_link = service + url

response = requests.get(full_link).json()

print('Repositories of the user are: ')
for i, repo in enumerate(response):
    print(f'    {i+1}. {repo.get("name")}')

with open('*.json', 'w') as w:
    json.dump(response, w)