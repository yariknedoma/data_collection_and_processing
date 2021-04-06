# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from lesson8_scrapy.items import Lesson8ScrapyItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from lesson8_scrapy.login_password import login, password


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    insta_login = login()
    insta_pwd = password()
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_user = ['randomuser1', 'randomuser2']

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    followers_hash = '5aefa9893005572d237da5068082d8d5'
    following_hash = '3dec7e2c57367ef3da3d987d89f9dbc8'

    def parse(self, response:HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)   # csrf token забираем из html
        yield scrapy.FormRequest(                   # заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username':self.insta_login, 'enc_password':self.insta_pwd},
            headers={'X-CSRFToken':csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for name in self.parse_user:
                yield response.follow(
                    f'/{name}/',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': name}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)       # Получаем id пользователя
        variables={'id': user_id,                                    # Формируем словарь для передачи даных в запрос
                   'first': 50,
                   'include_reel': 'true',
                   'fetch_mutual': 'false'}                                      # 12 постов. Можно больше (макс. 50)
        variables_encoded = urlencode(variables)
        for hash, function in zip(reversed([self.followers_hash, self.following_hash]),
                                  reversed([self.followers_parse, self.following_parse])):
            url_request = f'{self.graphql_url}query_hash={hash}&{variables_encoded}'
            yield response.follow(
                url_request,
                callback=function,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}         # variables ч/з deepcopy во избежание гонок
            )

    def followers_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):                                          # Если есть следующая страница
            variables['after'] = page_info['end_cursor']
            variables_encoded = urlencode(variables)
            url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{variables_encoded}'
            yield response.follow(
                url_followers,
                callback=self.followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        followers = j_data.get('data').get('user').get('edge_followed_by').get('edges')
        for follower in followers:
            item = Lesson8ScrapyItem(
                user_id=follower['node']['id'],
                full_name=follower['node']['full_name'],
                username=follower['node']['username'],
                photo=follower['node']['profile_pic_url'],
                data=follower['node'],
                profile_owner=username,
                follower=follower['node']['username'],
                being_scraped=username
            )
            yield item

    def following_parse(self, response: HtmlResponse, username, user_id,
                        variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']
            variables_encoded = urlencode(variables)  # Новый параметр для перехода на след. страницу
            url_following = f'{self.graphql_url}query_hash={self.following_hash}&{variables_encoded}'
            yield response.follow(
                url_following,
                callback=self.following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        following = j_data.get('data').get('user').get('edge_follow').get('edges')
        for one in following:
            item = Lesson8ScrapyItem(
                user_id=one['node']['id'],
                full_name=one['node']['full_name'],
                username=one['node']['username'],
                photo=one['node']['profile_pic_url'],
                data=one['node'],
                follower=username,
                profile_owner=one['node']['username'],
                being_scraped=username
            )
            yield item  # В пайплайн

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')