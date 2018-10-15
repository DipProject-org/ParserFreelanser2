import logging
import settings

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import sqlalchemy

from skilllist_sql import db_session, Skillbase

from get5cards_main import get_five_cards

#Настройки лога
logging.basicConfig(format= '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO, filename = 'bot.log')

def greet_user(bot,update,user_data):
	text = 'Привет {}!'.format(update.message.chat.first_name)
	update.message.reply_text(text, reply_markup= get_keyboard())

def talk_to_me(bot, update, user_data):
	print('talk_to_me вход')
	#принимаем текст от пользователя
	user_text = "Привет {}! Ты написал: {}".format(
		update.message.chat.first_name, update.message.text)

	logging.info("User: %s, Chat id: %s, Message: %s", update.message.chat.username, 
			update.message.chat.id, update.message.text)


def get_keyboard():
	my_keyboard = ReplyKeyboardMarkup(
		[['Получить 5 заказов']], resize_keyboard = True)
	return my_keyboard



def zapros_start(bot, update, user_data):
	print('in def zapros_start')
	update.message.reply_text('Привет {}! Напиши свой навык и я выведу тебе 5 последних предложений с Freelancer.com'.format(update.message.chat.first_name), reply_markup = ReplyKeyboardRemove())
	return 'skill'

def zapros_get_skill(bot, update, user_data):
	print('in def zapros_get_skill')
	user_skill = update.message.text
	print(user_skill)
	u = Skillbase
	user_tip = []
	try:
		q = u.query.filter(Skillbase.skill == user_skill).first()
		link = q.link
		print(link)
		cards = get_five_cards(link)
		for card in cards:
			if card['verified'] == True:
				pay_metod = '\tСпособ оплаты подтвержден'
			else: 
				pay_metod = ''
			update.message.reply_text('\nЗадание: {0}\nОплата:{5}{6}\nАктивно еще {1}.\n\nОписание: {2}\n\nТребуемые навыки{3}\n\nПредложений от фрилансеров:{7}\n\nСтраница заказа:  {4}\n\n'.format(card['title'],card['time'],card['description'],card['list_skill'],card['link'],card['price'],pay_metod,card['bids']), reply_markup= get_keyboard())
		return ConversationHandler.END

	except AttributeError:
		print('Такого навыка в базе нет')

		u1 = Skillbase

		user_skill = user_skill.lower()
		user_input = "%" + user_skill + "%"
		print(user_input)

		u1 = Skillbase
		q_user = u1.query.filter(Skillbase.skill_words.like(user_skill)).all()
		print("вся выборка "    + str(q_user))

		for skil in q_user:
			user_tip.append(skil.skill)
		user_tip = str(user_tip)

		print(user_tip)
		update.message.reply_text('Может быть вы имели ввиду {}'.format(user_tip), reply_markup= get_keyboard())
		return 'skill'

def rus_nuber(num):
	if num >= 11 and num <= 19:
		word = 'слов'
	else:
		if num % 10 == 1:
			word = 'слово'
		elif num % 10 in (2,3,4):
			word = 'слова'
		else:
			word = 'слов'
	return word



def main():
	'''Тело бота. Главная функция.'''
	mybot = Updater(settings.API_KEY,
		request_kwargs=settings.PROXY)

	logging.info('бот запускается')
	
	dp = mybot.dispatcher


	dp.add_handler(CommandHandler("start", greet_user, pass_user_data=True))
	zapros = ConversationHandler(
		entry_points = [RegexHandler('^Получить 5 заказов$',zapros_start, pass_user_data = True)], 
		states = {
		'skill':[MessageHandler(Filters.text, zapros_get_skill, pass_user_data = True)]
		}, 
		fallbacks = [],
		)
	dp.add_handler(zapros)
	dp.add_handler(MessageHandler(Filters.text, talk_to_me, pass_user_data = True))


	mybot.start_polling()
	mybot.idle()


main()