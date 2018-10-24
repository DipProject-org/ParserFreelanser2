import logging
import re
import sqlalchemy
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker, scoped_session

from setup_db.skill_list_sql import db_session, Skillbase

#парсим https://www.freelancer.com/job/
def find_links(html):
	logging.info('вход в find_links')
	skill_words = []
	works = []
	regexp= r'^/jobs/'
	regexp2= r'\(\b\d\b\)'

	db_session.query(Skillbase).delete()
	db_session.commit()

	soup = BeautifulSoup(html,'lxml')
	#Находим блок "Websites, IT & Software"
	text_block1 = soup.find('ul', class_ = "PageJob-browse-list Grid")
	text_block3 = text_block1.find_all('a', class_="PageJob-category-link ", href = re.compile(regexp))

	for block in text_block3:
		link = block.get('href')
		link = 'https://www.freelancer.com' + link
		str2 = block.get('title')
		title_str = re.sub(r' Jobs','',str2)
		str3 = block.contents[0]
		str3 = re.sub(r'  ','',str3)
		str3 = re.sub(r'\n','',str3)
		str3 = str3.split('\xa0')
		work_count = (re.search(r'\d+', str(str3[-1].strip()))).group()
		skill_words = title_str.replace('(','')
		skill_words = skill_words.replace(')','')
		skill_words = skill_words.replace('.','')
		skill_words = skill_words.replace(' / ',' ')
		skill_words = skill_words.replace('/',' ')
		skill_words = skill_words.replace(' for ',' ')
		skill_words = skill_words.replace(' on ',' ')
		skill_words = skill_words.lower()
		skill_words = skill_words.split(' ')
		if ' ' in skill_words:
			skill_words = skill_words.remove(' ')
		if len(skill_words)>1:
			skill_words.append((title_str).lower())
		
		skill = {'skill':title_str, 'link':link, 'work_count': int(work_count),'skill_words':str(skill_words)}
		skill_db = Skillbase(skill['skill'], skill['link'], skill['work_count'], skill['skill_words'])
		db_session.add(skill_db)
	db_session.commit()
	