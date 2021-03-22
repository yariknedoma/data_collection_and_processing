from bs4 import BeautifulSoup as bs
import requests
import unicodedata
import pandas as pd
from pprint import pprint
from pymongo import MongoClient

main_link = 'https://hh.ru'
job_name = 'python'
params = {'L_is_autosearch': 'false', 'clusters': 'true', 'enable_snippets': 'true',
          'salary': '', 'st': 'searchVacancy', 'text': job_name, 'page':0}
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'}
vacancies = []

# creating a mongodb client and database
client = MongoClient('localhost', 27017)
db_name = job_name + '_vacancies'
db = client[db_name]
data = db.data


def salary_converter(salary):
    salary = unicodedata.normalize('NFKD', salary)
    salary = salary.replace(' ', '')

    if '-' in salary:
        dash = salary.find('-')
        min = int(salary[:dash])
        while True:
            currency_index = dash
            for character in salary[dash+1:]:
                is_letter = character.isalpha()
                currency_index += 1
                if is_letter:
                    break
            break

        max = int(salary[dash+1:currency_index])
        currency = salary[currency_index:]

    elif 'от' in salary:
        while True:
            currency_index = 1
            for character in salary[2:]:
                is_letter = character.isalpha()
                currency_index += 1
                if is_letter:
                    break
            break
        min = int(salary[2:currency_index])
        max = None
        currency = salary[currency_index:]

    elif 'до' in salary:
        while True:
            currency_index = 1
            for character in salary[2:]:
                is_letter = character.isalpha()
                currency_index += 1
                if is_letter:
                    break
            break
        min = None
        max = int(salary[2:currency_index])
        currency = salary[currency_index:]

    else:
        min = None
        max = None
        currency = None

    return min, max, currency




while True:
    response = requests.get(main_link+'/search/vacancy', params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    vacancies_list = soup.findAll('div', attrs={'class': 'vacancy-serp-item__row_header'})

    for vacancy in vacancies_list:
        vacancy_dict = {}

        element = vacancy.find('div')
        company = vacancy.nextSibling
        city_name = company.nextSibling.getText()
        company_name = company.find(attrs={'class': 'vacancy-serp-item__meta-info-company'})
        if company_name is not None:
            company_name = company_name.getText()
        else:
            company_name = city_name
            city_name = None
        vacancy_name = element.getText()
        vacancy_min, vacancy_max, vacancy_currency = salary_converter(element.nextSibling.getText())
        vacancy_link = element.find('a')['href']
        vacancy_source = 'https://hh.ru'

        vacancy_dict['name'] = vacancy_name
        vacancy_dict['salary_min'] = vacancy_min
        vacancy_dict['salary_max'] = vacancy_max
        vacancy_dict['salary_currency'] = vacancy_currency
        vacancy_dict['link'] = vacancy_link
        vacancy_dict['source'] = vacancy_source
        vacancy_dict['company'] = company_name
        vacancy_dict['city'] = city_name

        vacancies.append(vacancy_dict)

        # checking if link exists in database
        link_in = data.find({'link': vacancy_link})

        if link_in.count() == 0:
            data.insert_one(vacancy_dict)

    next_link = soup.find('a', {'data-qa': 'pager-next'})
    if next_link is None:
        break
    next_link = next_link['href']
    page_ind = next_link.rfind('page')
    page = next_link[page_ind + 5:]
    params['page'] = page
    print(f'page {page}')

# salary not less than 3000 USD or 250000 rub
condition1 = {'salary_currency': 'USD', '$or': [{'salary_min': {'$gt': 3000}}, {'salary_max': {'$gt': 3000}}]}
condition2 = {'salary_currency': 'руб.', '$or': [{'salary_min': {'$gt': 250000}}, {'salary_max': {'$gt': 250000}}]}
result = data.find({'$or': [condition1, condition2]})
print(f'database contains {result.count()} vacancies with salary over 3000 USD or 250000 rub')

