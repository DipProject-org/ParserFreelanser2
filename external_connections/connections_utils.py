import logging
import requests

import datetime
from random import uniform, choice
from time import sleep

def get_new_proxies(date_this_request):
	proxy_list = []
	result = requests.get('https://htmlweb.ru/geo/api.php?proxy&short&json')
	if result.status_code == 200:
		result = result.json()
		del result['limit']			#Удаляем лишнее значение.
		x=0
		for key in result:
			x= str(x)
			proxy_site = result[x]
			proxy_list.append(proxy_site)
			x= int(x)
			x+=1
		proxy_list_for_save = proxy_list
		proxy_list_for_save.append(str(date_this_request))			#Добавляем дату.
		proxy_list_for_save = str(proxy_list_for_save)			#Превращаем словарь в строку.
		logging.info('Получен новый список прокси')
		with open('proxies.txt','w',encoding = 'utf-8') as f:
			f.write(proxy_list_for_save)
	else:
		logging.info("Мы не получили новый прокси лист, используем старый.")
		del proxies_list['date']
		x=0
		for key in proxies_list:
			proxy_site = proxies_list[x]
			proxy_list.append(proxy_site)
			x+=1
	return proxy_list

def load_proxies():
	#Загружаем файл	и делаем из него словарь с датой создания на конце.
	proxy_list = []
	date_this_request = datetime.datetime.now()
	date_this_request = str(date_this_request).split(' ')[0]			#Мы получили дату.

	try:
		proxies_list = open('proxies.txt').read()			#Читаем данные из файла в строку.
	except FileNotFoundError:
		proxy_list = get_new_proxies(date_this_request)
		return proxy_list

	proxies_list = proxies_list.replace("['",'')
	proxies_list = proxies_list.replace("']",'')
	proxies_list = proxies_list.split("', '")

	if proxies_list[-1] == date_this_request:
		logging.info('Сегодня уже был запрос по прокси')
		#Используем список
		del proxies_list[-1]
		x=0
		for key in proxies_list:
			proxy_site = proxies_list[x]
			proxy_list.append(proxy_site)
			x+=1
	else:
		#Запрашиваем новый список прoкси.
		proxy_list = get_new_proxies(date_this_request)
	return proxy_list


def use_proxy(url):
	proxies = load_proxies()
	proxy = {'http':'http://'+ choice(proxies)}
	html = get_html(url,proxy)
	return html


def get_html(url, proxy = None):
	'''запрашивает страницу притворяясь человеком'''
	logging.info('вход в гет штмл')
	try:
		result = requests.get(url, proxies = proxy)
	except TimeoutError as e:
		logging.info(e)
		sleep(uniform(3,6))
		use_proxy(url)
	except requests.exceptions.ConnectionError as e:
		logging.info(e)
		sleep(uniform(3,6))
		use_proxy(url)

	if result.status_code == 200 and result!=None:
		logging.info('притворился')
		return result.text
	elif result.status_code == 404:
		logging.info("404 status_code")
		sleep(uniform(3,6))
		use_proxy(url)
	elif result.status_code == 403:
		logging.info("403 status_code")
		sleep(uniform(3,6))
		use_proxy(url)
	elif result.status_code == 500:
		logging.info("500 status_code")
		sleep(uniform(3,6))
		use_proxy(url)

