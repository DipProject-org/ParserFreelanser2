import logging

from telegram import (ReplyKeyboardMarkup,
 KeyboardButton, ReplyKeyboardRemove, 
 InlineKeyboardMarkup, InlineKeyboardButton)

import sqlalchemy

from bot.message_texts import (
	PAY_MESSAGE, GREET_USER, KEYBOARD_BUTTON, INLINE_BUTTON,
	 ECHO, START, VERIFIED, CORRECTOR
	)

import sys
import os
sys.path.append(os.path.dirname(__file__) + "/../parserfrilanse/")

from setup_db.create_db import create_db
from setup_db.skill_list_sql import db_session, Skillbase
from utils import get_five_cards

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


def query_to_base_start(bot, update, user_data):
	logging.info('in def query_to_base_start')
	update.message.reply_text(GREET_USER.format(update.message.chat.first_name), reply_markup = ReplyKeyboardRemove())
	return 'skill'


def query_to_base_get_skill(bot, update, user_data):
	logging.info('in def query_to_base_get_skill')
	user_skill = update.message.text
	logging.info(user_skill)
	u = Skillbase
	user_tip = []
	try:
		q = u.query.filter(Skillbase.skill == user_skill).first()
		link = q.link
		logging.info(link)
		cards = get_five_cards(link)
		for card in cards:
			if card['verified'] == True:
				pay_metod = VERIFIED
			else: 
				pay_metod = ''
			url = card['link']
			update.message.reply_text(PAY_MESSAGE.format(
				title = card['title'], time = card['time'], description = card['description'], list_skill = card['list_skill'], price = card['price'], pay_metod = pay_metod, bids = card['bids']), reply_markup= card_link_kb(url)
			)
		return ConversationHandler.END

	except AttributeError:
		logging.info('Такого навыка в базе нет')

		u1 = Skillbase

		user_skill = user_skill.lower()
		user_input = "%" + user_skill + "%"
		logging.info(user_input)

		u1 = Skillbase
		q_user = u1.query.filter(Skillbase.skill_words.like(user_skill)).all()
		logging.info("вся выборка " + str(q_user))

		for skil in q_user:
			user_tip.append(skil.skill)
		user_tip = str(user_tip)

		logging.info(user_tip)
		update.message.reply_text(CORRECTOR.format(user_tip), reply_markup= get_keyboard())
		return 'skill'

	except sqlalchemy.exc.OperationalError:
		create_db()
		return 'skill'