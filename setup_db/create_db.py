import logging
import requests

import sys
import os

sys.path.append(os.path.dirname(__file__) + "/..")
from external_connections.connections_utils import use_proxy
from setup_db.skill_list_sql import create_base
from setup_db.skill_list_find_links import find_links

def create_db():
	logging.info('Создание базы')
	url = 'https://www.freelancer.com/job/'
	html = use_proxy(url)
	create_base()
	find_links(html)
	logging.info('Данные занесены в базу')

if __name__ == '__main__':
	create_db()

