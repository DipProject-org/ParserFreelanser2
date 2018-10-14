import sqlalchemy
from skilllist_sql import db_session, Skillbase
import datetime
import requests
from random import choice
from time import sleep
from random import uniform
from bs4 import BeautifulSoup
import re

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
		print('Сегодня уже был запрос по прокси')
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

	#print(proxy_list)
	return proxy_list

#'Запрашивает данные с указанного сайта, притворяясь человеком'
def get_html(url, proxy = None, useragent = None):
	'запрашивает страницу притворяясь человеком'
	print('вход в гет штмл')
	r = requests.get(url, proxies = proxy) # headers = useragent,

	#with open('html.txt','w',encoding = 'utf-8') as f:
		#f.write(str(r.text))

	print('притворился')
	return r.text


def get_five_cards(link):
	print('Запуск')
	#url = 'https://www.freelancer.com/jobs/software-architecture/' #!!Это пока заглушка для запроса от бота!!
	url = link
	#useragents = open('useragents.txt').read().split('\n')
	proxies = get_proxy()

	while True: #Повторяй цикл до ответа от прокси сервера
		sleep(uniform(3,6))
		proxy = {'http':'http://'+ choice(proxies)}
		#useragent = {'User-Agent': choice(useragents)}
		try:
			html = get_html(url,proxy) #useragent,proxy)	#'запрашивает страницу притворяясь человеком'
			break
		except requests.exceptions.RequestException as e:
			#print(e)
			print('________________')

	print('Передаем стр в парсер')
	cards = find_works(html)
		
	#with open('text.txt','w',encoding = 'utf-8') as f:
		#f.write(html)
	#print (cards)
	return cards

def find_works(html):#получаем ссылку, число работ
	#bonus = ['local=true','&','fixed=true','fixed_min=','fixed_max=','contest=true','contest_min=','contest_max=','hourly=true','languages=','hourly_duration=']#1-6
	cards = []
	link = {}
	skill_tags = []
	card_list = []
	x=0
	
	#html = open(html).read()
	soup = BeautifulSoup(html,'lxml')
	#Находим лист проектов
	text_block1 = soup.find('div', id= "project-list", class_="JobSearchCard-list")
	#Находим карточки проектов
	text_block1 = text_block1.find_all('div', class_= "JobSearchCard-item-inner")
	#Драим по каждой карточке------------------------------
	for block in text_block1:
		#print(block)
		#Находим название карточки
		title = block.find('a', class_='JobSearchCard-primary-heading-link').contents[0]#,href = re.compile(regexp))
		title = title.replace('  ','')
		title = title.replace('\n','')
		#print(title)

		#Заявлено времени назад
		time = block.find('span', class_='JobSearchCard-primary-heading-Days').contents[0]
		time = time.split(' ')
		#print(time)

		#Описание
		description = block.find('p', class_='JobSearchCard-primary-description').contents[0]
		description= description.replace('  ','')
		description = description.replace('\n','')
		#print(description)

		#Список навыков
		skills_block = block.find('div', class_='JobSearchCard-primary-tags')
		skills = skills_block.find_all('a')
		for skill in skills:
			skill = str(skill)
			skill = skill.split('/">')[-1]
			skill = skill.replace('</a>','')
			skill_tags.append(skill)
		list_skill = skill_tags
		skill_tags = []
		#print(list_skill)

		featured = block.find('div', class_="JobSearchCard-primary-promotion")
		featured= 'Featured' in str(featured)
		#print(featured)

		need_login = block.find('p', class_='JobSearchCard-primary-description')
		need_login = 'Login</a> to see details.' in str(need_login)
		#print('For discription {}'.format(need_login))

		if need_login == True:
			price ='0'
			link = 'Error 404'
			bids ='0'
			description = 'Need Login for description'

		if featured == False and need_login == False:
			#Цена работы
			price_block = block.find('div', class_="JobSearchCard-secondary-price").contents[0]
			price= price_block.replace('  ','')
			price = price.replace('\n','')
			price = price.replace('/ hr','per hour')
			#print(price)

			#Ссылка на работу
			contest = block.find('span', class_="Icon JobSearchCard-primary-heading-Icon")
			contest = 'flicon-trophy' in str(contest)
			if contest:
				regexp= r'^/contest/'
			else:
				regexp= r'^/projects/'

			link_block = block.find('a',href = re.compile(regexp))
			link = link_block.get('href')
			link = 'https://www.freelancer.com' + link
			#print(link)

			#Количество заявок
			bids = block.find('div', class_='JobSearchCard-secondary-entry').contents[0]
			bids = bids.split(' ')[0]
			#print(bids)

		#Верифицировано или нет
		verified = block.find('div', class_="JobSearchCard-primary-heading-status Tooltip--top")
		verified = 'VERIFIED' in str(verified)
		#print(verified)

		#print('---------------')
		if featured == True:
			price = '0'
			link = 'Error 404'
			bids = '0'
		
		card = {'title':title, 'time':time, 'description':description, 'list_skill':list_skill, 'link':link, 'price':price, 'verified':verified, 'bids':bids}
		#print(card)
		cards.append(card)
		x+=1
		if x == 5:
			return cards
	return cards


def main():
	u = Skillbase

	while True:
		user_input = input('Укажите навык по которому искать заказы:\n')
		try:
			q = u.query.filter(Skillbase.skill == user_input).first()
			link = q.link
			print(link)
			break
		except AttributeError:
			print('Такого навыка в базе нет')
			user_input = "%" + user_input + "%"
			q_user = u.query.filter(Skillbase.skill_words.like(user_input)).all()
			print("Может быть вы имели ввиду:\n")
			for skil in q_user:
				print(skil.skill)

	cards = get_five_cards(link)
	for card in cards:
		if card['verified'] == True:
			pay_metod = '\tСпособ оплаты подтвержден'
		else: 
			pay_metod = ''
		print('\nЗадание: {0}\nОплата:{5}{6}\tАктивно еще {1}.\n\nОписание: {2}\n\nТребуемые навыки{3}\n\nПредложений от фрилансеров:{7}\n\nСтраница заказа:  {4}\n\n'.format(card['title'],card['time'],card['description'],card['list_skill'],card['link'],card['price'],pay_metod,card['bids']))
	pause = input('Any key for quit')

if __name__ == '__main__':
	main()