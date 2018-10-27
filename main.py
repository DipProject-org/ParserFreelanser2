from telegram.ext import (Updater, CommandHandler, 
	MessageHandler, Filters, RegexHandler,
	 ConversationHandler)

import logging

import os
from setup_db.create_db import create_db
import settings
from bot.talk_with_user import (
	greet_user, talk_to_me, query_to_base_start,
	 query_to_base_get_skill, get_keyboard, card_link_kb
	)

#проверка на наличие папки logs
if not os.path.exists("logs"):
	os.mkdir("logs")
#Настройки лога
logging.basicConfig(format= '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO, filename = 'logs/bot.log')

def main():
	mybot = Updater(settings.API_KEY,
		request_kwargs=settings.PROXY)

	logging.info('бот запускается')

	#проверка на наличие файла базы и скрипт на его создание.
	if (os.stat("skillbase.db")).st_size < 100.0:
		create_db()

	dp = mybot.dispatcher
	dp.add_handler(CommandHandler("start", greet_user, pass_user_data=True))
	query_to_base = ConversationHandler(
		entry_points = [RegexHandler('^Получить 5 заказов$',query_to_base_start, pass_user_data = True)], 
		states = {
		'skill':[MessageHandler(Filters.text, query_to_base_get_skill, pass_user_data = True)]
		}, 
		fallbacks = [],
		)
	dp.add_handler(query_to_base)
	dp.add_handler(MessageHandler(Filters.text, talk_to_me, pass_user_data = True))


	mybot.start_polling()
	mybot.idle()

if __name__ == '__main__':
	main()

