import logging
import sqlalchemy
import re
from bs4 import BeautifulSoup

from setup_db.skill_list_sql import db_session, Skillbase
from external_connections.connections_utils import use_proxy
from settings import card_cap

def get_cards(link):
	logging.info('Запуск get_cards')
	html = use_proxy(link)
	logging.info('Передаем стр в парсер')
	cards = find_works_card(html)
	logging.info('Передано {} карт'.format(len(cards)))
	return cards


def find_works_card(html):		#получаем ссылку, число работ
	cards = []
	card_list = []
	x=0
	
	soup = BeautifulSoup(html,'lxml')
	#Находим лист проектов
	text_block1 = soup.find(
		'div', id= "project-list", class_="JobSearchCard-list"
		)
	#Находим карточки проектов
	text_block1 = text_block1.find_all(
		'div', class_= "JobSearchCard-item-inner"
		)
	#Драим по каждой карточке
	for block in text_block1:
		card = parse(block)
		cards.append(card)
		x+=1
		if x == card_cap:
			return cards
	return cards


def serialize_card(**kwargs):
	return kwargs

def normalize_str(target_str):
	target_str = target_str.replace('  ','')
	target_str = target_str.replace('\n','')
	return target_str

def parse(block):
	skill_tags = []
	#Находим название карточки
	title = normalize_str(block.find(
		'a', class_='JobSearchCard-primary-heading-link'
		).contents[0])

	#Заявлено времени назад
	time = block.find(
		'span', class_='JobSearchCard-primary-heading-Days'
		).contents[0]

	#Описание
	description = normalize_str(block.find(
		'p', class_='JobSearchCard-primary-description'
		).contents[0])

	#Список навыков
	skills_block = block.find('div', class_='JobSearchCard-primary-tags')
	skills = skills_block.find_all('a')
	for skill in skills:
		skill = str(skill)
		skill = skill.split('/">')[-1]
		skill = skill.replace('</a>','')
		skill_tags.append(skill)

	list_skill = str(skill_tags)
	list_skill = list_skill.replace("['","")
	list_skill = list_skill.replace("']","")
	list_skill = list_skill.replace("', '",", ")

	skill_tags = []

	#Требуется ли логин.
	need_login = block.find('p', class_='JobSearchCard-primary-description')
	need_login = 'Login</a> to see details.' in str(need_login)

	#Верифицировано или нет.
	verified = block.find(
		'div', class_="JobSearchCard-primary-heading-status Tooltip--top"
		)
	verified = 'VERIFIED' in str(verified)

	if need_login:
		price ='0'
		link = 'Error 404'
		bids ='0'
		description = 'Need Login for description'
		return serialize_card(
			title=title, 
			time=time, 
			description=description, 
			list_skill=list_skill, 
			link=link, 
			price=price, 
			verified=verified, 
			bids=bids
			)

	#Карточка активна или только анонсирована.
	featured = block.find('div', class_="JobSearchCard-primary-promotion")
	featured= 'Featured' in str(featured)

	if featured:
		price = '0'
		link = 'Error 404'
		bids = '0'
		return serialize_card(
			title=title, 
			time=time, 
			description=description, 
			list_skill=list_skill, 
			link=link, 
			price=price, 
			verified=verified, 
			bids=bids
			)

	if featured == False and need_login == False:
		#Цена работы
		price_block = normalize_str(block.find(
			'div', class_="JobSearchCard-secondary-price"
			).contents[0])
		price = price_block.replace('/ hr','per hour')

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
		
	return serialize_card(
		title=title, 
		time=time, 
		description=description, 
		list_skill=list_skill, 
		link=link, 
		price=price, 
		verified=verified, 
		bids=bids
		)

