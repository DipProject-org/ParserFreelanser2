from telegram import (
	ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, 
	InlineKeyboardMarkup, InlineKeyboardButton
	)
import logging
import sqlalchemy

import sys
import os

sys.path.append(os.path.dirname(__file__) + "/../parserfrilanse/")

from setup_db.create_db import create_db
from bot.message_texts import (
	KEYBOARD_BUTTON, INLINE_BUTTON, ECHO, START, GREET_USER, VERIFIED, PAY_MESSAGE, CORRECTOR
	)
from db_connections.connections import DataBaseSelector
from utils import get_five_cards

def query_to_base_start(bot, update, user_data):
	logging.info('in def query_to_base_start')
	update.message.reply_text(
		GREET_USER.format(update.message.chat.first_name),
		reply_markup = ReplyKeyboardRemove()
		)
	#проверка на наличие файла базы и скрипт на его создание.
	if not os.path.exists("skillbase.db"):
		create_db()
	return 'skill'


def query_to_base_get_skill(bot, update, user_data):
	"""Прогоняем запрос пользователя по базе, запускает парсер и выводит ответы в телеграмм"""
	logging.info('in def query_to_base_get_skill')
	user_skill = update.message.text
	try:
		selector = DataBaseSelector(user_skill)
		link = selector.query_to_base_skill()

	except AttributeError:
		logging.info('AttributeError')
		corrector = DataBaseSelector(user_skill)
		user_tip = corrector.find_in_key_words()
		logging.info(user_tip)
		update.message.reply_text(CORRECTOR.format(user_tip), reply_markup= get_keyboard())
		return 'skill'
	
	
	#Пускаем парсер по ссылке
	cards = get_five_cards(link)
	for card in cards:
		if card['verified'] == True:
			pay_metod = VERIFIED
		else: 
			pay_metod = ''
		url = card['link']
		update.message.reply_text(PAY_MESSAGE.format(
			title = card['title'], time = card['time'],
			description = card['description'], list_skill = card['list_skill'], 
			price = card['price'], pay_metod = pay_metod, bids = card['bids']),
			reply_markup= card_link_kb(url)
			)
	return ConversationHandler.END


def get_keyboard():
	my_keyboard = ReplyKeyboardMarkup(
		[[KEYBOARD_BUTTON]], resize_keyboard = True)
	return my_keyboard


def card_link_kb(url):
    button0 = InlineKeyboardButton(text=INLINE_BUTTON, url=url)
    buttons_list = [[button0]]
    keyboard = InlineKeyboardMarkup(buttons_list)
    return keyboard 


def greet_user(bot,update,user_data):
	text = START.format(update.message.chat.first_name)
	update.message.reply_text(text, reply_markup= get_keyboard())


def talk_to_me(bot, update, user_data):
	logging.info('talk_to_me вход')
	#принимаем текст от пользователя
	user_text = ECHO.format(
		update.message.chat.first_name, update.message.text)

	logging.info("User: %s, Chat id: %s, Message: %s", update.message.chat.username, 
			update.message.chat.id, update.message.text)
