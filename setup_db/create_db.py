import logging
import requests
from random import choice

import datetime

from setup_db.skill_list_sql import create_base
from setup_db.skill_list_find_links import find_links

import sys
import os
sys.path.append(os.path.dirname(__file__) + "/../parserfrilanse/")
from external_connections.connections_utils import get_proxy, get_html

def create_db():
	logging.info('Запуск')
	url = 'https://www.freelancer.com/job/'
	proxies = get_proxy()

	while True: #Повторяй цикл до ответа от прокси сервера
		proxy = {'http':'http://'+ choice(proxies)}
		try:
			html = get_html(url,proxy)	#'запрашивает страницу притворяясь человеком'
			break
		except request.exceptions.RequestExceptions as e:
			logging.info(e)

	create_base()
	find_links(html)
	print('Данные занесены в базу')

if __name__ == '__main__':
	create_db()
	