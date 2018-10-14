import requests
from random import choice

from random import uniform
from ast import literal_eval as le

import datetime

from skilllist_sql import create_base
from skilllist_find_links import find_links

def get_proxy():
#Мы будем использовать этот код, когда будем запрашивать лист прокси с сайта
	#Загружаем файл	и делаем из него словарь с датой создания на конце
	proxy_list = []
	date_this_request = datetime.datetime.now()
	date_this_request = str(date_this_request).split(' ')[0]			#Мы получили дату

	proxies_list = open('proxies.txt').read()			#Читаем данные из файла в строку

	proxies_list = proxies_list.replace("['",'')
	proxies_list = proxies_list.replace("']",'')
	proxies_list = proxies_list.split("', '")

	if proxies_list[-1] == date_this_request:
		print('Сегодня уже был запрос')
		#Используем список
		del proxies_list[-1]
		x=0
		for key in proxies_list:
			proxy_site = proxies_list[x]
			proxy_list.append(proxy_site)
			x+=1
	else:
		#Запрашиваем новый список прoкси
		result = requests.get('https://htmlweb.ru/geo/api.php?proxy&short&json')
		if result.status_code == 200:
			result = result.json()
			del result['limit']			#Удаляем лишнее значение
			x=0
			for key in result:
				x= str(x)
				proxy_site = result[x]
				proxy_list.append(proxy_site)
				x= int(x)
				x+=1
			proxy_list_for_save = proxy_list
			proxy_list_for_save.append(str(date_this_request))			#Добавляем дату
			proxy_list_for_save = str(proxy_list_for_save)			#превращаем словарь в строку
			print ('Получен новый список прокси')
			with open('proxies.txt','w',encoding = 'utf-8') as f:
				f.write(proxy_list_for_save)
		else:
			print("Мы не получили новый прокси лист, используем старый.")
			del proxies_list['date']
			x=0
			for key in proxies_list:
				proxy_site = proxies_list[x]
				proxy_list.append(proxy_site)
				x+=1
	return proxy_list

#'Запрашивает данные с указанного сайта, притворяясь человеком'
def get_html(url, useragent = None, proxy = None):
	'запрашивает страницу притворяясь человеком'
	print('вход в гет штмл')
	r = requests.get(url, headers = useragent, proxies = proxy)
	print('притворился')
	return r.text



def main():
	print('Запуск')
	url = 'https://www.freelancer.com/job/'
	proxies = get_proxy()

	while True: #Повторяй цикл до ответа от прокси сервера
		#sleep(uniform(1,2))
		proxy = {'http':'http://'+ choice(proxies)}
		try:
			html = get_html(url,proxy)	#'запрашивает страницу притворяясь человеком'
			break
		except request.exceptions.RequestExceptions as e:
			print(e)

	create_base()
	find_links(html)
	print('Данные занесены в базу')

if __name__ == '__main__':
	main()