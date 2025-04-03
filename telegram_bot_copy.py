# -*- coding: utf-8 -*-
import telebot
import threading
import time
import requests
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import os

API_KEY = os.getenv("telgram_copy_bot_api")
token_url = os.getenv("token_url")


bot = telebot.TeleBot(API_KEY)

allowed_users = {
    885253145: "Нуртуган"
}

user_state = {}
modules = ['basic', 'status', 'riskfactor', 'trustworthy-extended']

bin_url_1 = "https://api.adata.kz/api/company/"
bin_url_2 = "/ZVloUOB6nHzxcHfs4jPJEW12V2YxEgY?iinBin="

def get_company_info(bin, module):
    try:
        url = f"{bin_url_1}{module}{bin_url_2}{bin}"
        r = requests.get(url)
        if r.status_code != 200:
            return {}

        token_id = r.json()['token']
        url_2 = f"{token_url}{token_id}"
        while True:
            r2 = requests.get(url_2)
            if r2.status_code != 200:
                return {}
            if r2.json()['message'] == 'ready':
                return r2.json()
            elif r2.json()['message'] != 'wait':
                return {}
            time.sleep(1)
    except Exception as e:
        print("Ошибка при запросе данных:", e)
        return {}

def send_company_info(bot, chat_id, basic):
    bot.send_message(chat_id, 'Полное наименование компании: ' + basic.get('name_ru', '—'))
    bot.send_message(chat_id, 'Дата регистрации: ' + basic.get('date_registration', '—'))
    bot.send_message(chat_id, f"ОКЭД ({basic.get('oked_id', '—')}): {basic.get('oked', '—')}")
    bot.send_message(chat_id, 'Юридический адрес: ' + basic.get('legal_address', '—'))
    bot.send_message(chat_id, 'ФИО руководителя: ' + basic.get('fullname_director', '—'))

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in allowed_users:
        bot.send_message(message.chat.id, "Извините, у вас нет доступа к этому боту.")
        return

    user_name = allowed_users[message.chat.id]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔍 Проверить компанию"))
    markup.add(KeyboardButton("ℹ️ Помощь"))

    bot.send_message(message.chat.id, f"Добро пожаловать, {user_name}! Выберите действие:", reply_markup=markup)
    user_state[message.chat.id] = "waiting_for_action"

@bot.message_handler(func=lambda message: message.text in ["🔍 Проверить компанию", "ℹ️ Помощь"])
def handle_menu(message):
    if message.chat.id not in allowed_users:
        bot.send_message(message.chat.id, "Извините, у вас нет доступа к этому боту.")
        return

    if message.text == "🔍 Проверить компанию":
        bot.send_message(message.chat.id, "Пришлите БИН компании.")
        user_state[message.chat.id] = "waiting_for_id"
    else:
        bot.send_message(message.chat.id, "Этот бот помогает проверять компании по БИН. Просто отправьте БИН.")

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_id")
def handle_company_id(message):
    if message.chat.id not in allowed_users:
        bot.send_message(message.chat.id, "Извините, у вас нет доступа к этому боту.")
        return

    company_id = message.text.strip()
    bot.send_message(message.chat.id, "⏳ Идёт проверка...")

    try:
        basic_info = get_company_info(company_id, modules[0])
        if not basic_info:
            raise ValueError("Компания не найдена")

        basic = basic_info['data']
        status = get_company_info(company_id, modules[1])['data']
        risk = get_company_info(company_id, modules[2])['data']
        trust = get_company_info(company_id, modules[3])['data']

        info = []

        if not status['company_status']:
            info.append("❗ В списке «Бездействующее предприятие»")
        if status['bankcrupt']:
            info.append("❗ В списке «Банкрот»")
        if risk['company']['seized_bank_account']:
            info.append("❗ Арест на банковские счета")
        if risk['company']['seized_property']:
            info.append("❗ Арест на имущество")
        if risk['company']['ban_registration_actions_legal_ent']:
            info.append("❗ Запрет на регистрационные действия ЮЛ")
        if risk['company']['ban_registration_actions_physical_ent']:
            info.append("❗ Запрет на регистрационные действия ФЛ")
        if risk['company']['ban_notarius_actions']:
            info.append("❗ Запрет на совершение нотариальных действий")
        if risk['head']['enforcement_debt']:
            info.append("❗ Должник по исполнительным производствам")
        if risk['head']['debtor_for_executive_documents']:
            info.append("❗ В списке должников по исполнительным документам")
        if trust['tax_arrears_150']:
            info.append("❗ Налоговая задолженность более 150 МРП")
        if trust['restriction_on_leaving']:
            info.append("❗ Временное ограничение на выезд из РК")
        if trust['transport_arrest']:
            info.append("❗ Арест на транспорт")

        send_company_info(bot, message.chat.id, basic)

        if not info:
            bot.send_message(message.chat.id, "Проблем нет ✅")
        else:
            for i in info:
                bot.send_message(message.chat.id, i)

        # Кнопка для новой проверки
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔄 Проверить другую компанию", callback_data="check_another"))
        bot.send_message(message.chat.id, "Хотите проверить другую компанию?", reply_markup=markup)

        user_state[message.chat.id] = "waiting_for_action"

    except Exception as e:
        print("❌ Ошибка:", e)
        bot.send_message(message.chat.id, "❗ Ошибка при обработке. Убедитесь, что БИН корректный.")

@bot.callback_query_handler(func=lambda call: call.data == "check_another")
def check_another(call):
    if call.message.chat.id not in allowed_users:
        bot.send_message(call.message.chat.id, "Извините, у вас нет доступа к этому боту.")
        return
    bot.send_message(call.message.chat.id, "Пришлите БИН компании.")
    user_state[call.message.chat.id] = "waiting_for_id"

# Запуск бота
def polling():
    bot.polling(non_stop=True, interval=0)

thread = threading.Thread(target=polling)
thread.start()
