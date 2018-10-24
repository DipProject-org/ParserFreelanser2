import sys
import os
import logging

sys.path.append(os.path.dirname(__file__) + "/../parserfrilanse/")

from setup_db.skill_list_sql import db_session, Skillbase
#настройки

#класс
class DataBaseSelector():
	"""docstring for DataBaseSelector"""

	def __init__(self, user_skill):
		u = Skillbase
		self.u = u
		self.user_skill = user_skill


	def query_to_base_skill(self):
		"""Прогоняет запрос пользователя по базе"""
		q = self.u.query.filter(Skillbase.skill == self.user_skill).first()
		link = q.link
		logging.info(link)
		return link

	def find_in_key_words(self):
		"""Что делать, если такого навыка нет в базе."""
		logging.info('in find_in_key_words')
		user_tip = []
		user_skill = self.user_skill.lower()
		user_input = "%" + user_skill + "%"
		logging.info(user_input)
		q_user = self.u.query.filter(Skillbase.skill_words.like(user_input)).all()

		for skil in q_user:
			user_tip.append(skil.skill)
		user_tip = str(user_tip)
		user_tip = user_tip.replace("['","")
		user_tip = user_tip.replace("']","")
		user_tip = user_tip.replace("', '","\n")

		return user_tip
