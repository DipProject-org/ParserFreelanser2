import logging
import requests

import sqlalchemy
from setup_db.skill_list_sql import db_session, Skillbase

from bs4 import BeautifulSoup
import re
from random import uniform, choice
from time import sleep

from external_connections.connections_utils import get_proxy, get_html


def get_five_cards(link):
	logging.info('Запуск get_five_cards')
	url = link
	proxies = get_proxy()
	while True: 	#Повторяй цикл до ответа от прокси сервера
		sleep(uniform(3,6))
		proxy = {'http':'http://'+ choice(proxies)}
		try:
			html = get_html(url,proxy)		#'запрашивает страницу притворяясь человеком'
			break
		except requests.exceptions.RequestException as e:
			logging.info(e)
			logging.info('________________')

	logging.info('Передаем стр в парсер')
	cards = find_works_card(html)
	return cards


def find_works_card(html):		#получаем ссылку, число работ
	cards = []
	card_list = []
	x=0
	
	soup = BeautifulSoup(html,'lxml')
	#Находим лист проектов
	text_block1 = soup.find('div', id= "project-list", class_="JobSearchCard-list")
	#Находим карточки проектов
	text_block1 = text_block1.find_all('div', class_= "JobSearchCard-item-inner")
	#Драим по каждой карточке
	for block in text_block1:
		card = parser(block)
		cards.append(card)
		x+=1
		if x == 5:
			return cards
	return cards


def parser(block):
	skill_tags = []
	#Находим название карточки
	title = block.find('a', class_='JobSearchCard-primary-heading-link').contents[0]
	title = title.replace('  ','')
	title = title.replace('\n','')

	#Заявлено времени назад
	time = block.find('span', class_='JobSearchCard-primary-heading-Days').contents[0]
	time = time.split(' ')

	#Описание
	description = block.find('p', class_='JobSearchCard-primary-description').contents[0]
	description= description.replace('  ','')
	description = description.replace('\n','')

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

	featured = block.find('div', class_="JobSearchCard-primary-promotion")
	featured= 'Featured' in str(featured)

	need_login = block.find('p', class_='JobSearchCard-primary-description')
	need_login = 'Login</a> to see details.' in str(need_login)

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

		#Количество заявок
		bids = block.find('div', class_='JobSearchCard-secondary-entry').contents[0]
		bids = bids.split(' ')[0]

	#Верифицировано или нет
	verified = block.find('div', class_="JobSearchCard-primary-heading-status Tooltip--top")
	verified = 'VERIFIED' in str(verified)

	if featured == True:
		price = '0'
		link = 'Error 404'
		bids = '0'
		
	card = {'title':title, 'time':time, 'description':description, 'list_skill':list_skill, 'link':link, 'price':price, 'verified':verified, 'bids':bids}
	
	return card
