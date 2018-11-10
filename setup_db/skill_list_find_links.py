import logging
import re
import sqlalchemy
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker, scoped_session

from setup_db.skill_list_sql import db_session, Skillbase, add_skill

#парсим https://www.freelancer.com/job/

def normalize2_str(x, y=False):
	x = x.replace('(','')
	x = x.replace(')','')
	if y == True:
		return x
	x = x.replace('.','')
	x = x.replace(' / ',' ')
	x = x.replace('/',' ')
	x = x.replace(' for ',' ')
	x = x.replace(' on ',' ')
	x = x.lower()
	return x

def find_links(html):
	logging.info('вход в find_links')
	skill_words = []
	works = []
	jobs_prefix= r'^/jobs/'

	db_session.query(Skillbase).delete()
	db_session.commit()

	soup = BeautifulSoup(html,'lxml')
	#Находим блок "Websites, IT & Software"
	text_block1 = soup.find('ul', class_ = "PageJob-browse-list Grid")
	text_block3 = text_block1.find_all(
		'a', class_="PageJob-category-link ",
		href = re.compile(jobs_prefix)
		)

	for block in text_block3:

		#Получаем ссылку на лист заказов по навыку.
		link = block.get('href')
		link = 'https://www.freelancer.com' + link

		#Получаем название навыка.
		str2 = block.get('title')
		title_str = re.sub(r' Jobs','',str2)

		#Получаем количество заказов.
		str3 = block.contents[0]
		work_count = ' '.join(str3.split())
		work_count = work_count.split(" ")[-1]
		work_count = normalize2_str(work_count,True)

		#Получаем список навыков.
		skill_words = normalize2_str(title_str).split(' ')
		if ' ' in skill_words:
			skill_words = skill_words.remove(' ')
		if len(skill_words)>1:
			skill_words.append((title_str).lower())
		skill = {'skill':title_str, 'link':link, 'work_count':int(work_count), 'skill_words':str(skill_words)}
		add_skill(skill)
	add_skill(False)

