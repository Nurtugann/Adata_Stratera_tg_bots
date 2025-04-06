# -*- coding: utf-8 -*-
import os
import time
import requests
import json
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

API_KEY = os.getenv("telgram_copy_bot_api")
token_url = os.getenv("token_url")
bin_url_2 = os.getenv("bin_url_2")
bin_url_1 = "https://api.adata.kz/api/company/"

bot = telebot.TeleBot(API_KEY)
app = Flask(__name__)

allowed_users = {
    885253145: "Нуртуган"
}

user_state = {}
modules = ['basic', 'status', 'riskfactor', 'trustworthy-extended']

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

def format_company_info(basic, status, risk, trust):
    lines = []
    lines.append(f"🏢 *{basic.get('name_ru', '—')}*")
    lines.append(f"📅 Дата регистрации: {basic.get('date_registration', '—')}")
    lines.append(f"🏷 ОКЭД ({basic.get('oked_id', '—')}): {basic.get('oked', '—')}")
    lines.append(f"📍 Юр. адрес: {basic.get('legal_address', '—')}")
    lines.append(f"👤 Руководитель: {basic.get('fullname_director', '—')}")

    warnings = []

    if not status['company_status']:
        warnings.append("❗ В списке «Бездействующее предприятие»")
    if status['bankcrupt']:
        warnings.append("❗ В списке «Банкрот»")
    if risk['company']['seized_bank_account']:
        warnings.append("❗ Арест на банковские счета")
    if risk['company']['seized_property']:
        warnings.append("❗ Арест на имущество")
    if risk['company']['ban_registration_actions_legal_ent']:
        warnings.append("❗ Запрет на регистрационные действия ЮЛ")
    if risk['company']['ban_registration_actions_physical_ent']:
        warnings.append("❗ Запрет на регистрационные действия ФЛ")
    if risk['company']['ban_notarius_actions']:
        warnings.append("❗ Запрет на нотариальные действия")
    if risk['head']['enforcement_debt']:
        warnings.append("❗ Долги по исполнительным производствам")
    if risk['head']['debtor_for_executive_documents']:
        warnings.append("❗ В списке должников по исполнительным документам")
    if trust['tax_arrears_150']:
        warnings.append("❗ Налоговая задолженность >150 МРП")
    if trust['restriction_on_leaving']:
        warnings.append("❗ Ограничение на выезд из РК")
    if trust['transport_arrest']:
        warnings.append("❗ Арест на транспорт")

    if warnings:
        lines.append("\n⚠️ *Риски:*")
        lines += warnings
    else:
        lines.append("\n✅ *Проблем не найдено*")

    return "\n".join(lines)

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in allowed_users:
        bot.send_message(message.chat.id, "Извините, у вас нет доступа к этому боту.")
        return

    user_name = allowed_users[message.chat.id]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("\U0001F50D Проверить компанию"))
    markup.add(KeyboardButton("\u2139\ufe0f Помощь"))

    bot.send_message(message.chat.id, f"Добро пожаловать, {user_name}! Выберите действие:", reply_markup=markup)
    user_state[message.chat.id] = "waiting_for_action"

@bot.message_handler(func=lambda message: message.text in ["\U0001F50D Проверить компанию", "\u2139\ufe0f Помощь"])
def handle_menu(message):
    if message.chat.id not in allowed_users:
        bot.send_message(message.chat.id, "Извините, у вас нет доступа к этому боту.")
        return

    if message.text == "\U0001F50D Проверить компанию":
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
    if not company_id.isdigit() or len(company_id) != 12:
        bot.send_message(message.chat.id, "❗ Введите корректный 12-значный БИН.")
        return

    bot.send_message(message.chat.id, "\u23F3 Идёт проверка...")

    try:
        basic_info = get_company_info(company_id, modules[0])
        if not basic_info:
            raise ValueError("Компания не найдена")

        basic = basic_info['data']
        status = get_company_info(company_id, modules[1])['data']
        risk = get_company_info(company_id, modules[2])['data']
        trust = get_company_info(company_id, modules[3])['data']

        message_text = format_company_info(basic, status, risk, trust)
        bot.send_message(message.chat.id, message_text, parse_mode='Markdown')

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("\U0001F501 Проверить другую компанию", callback_data="check_another"))
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

@app.route(f"/{API_KEY}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

@app.route('/')
def index():
    return 'Бот работает'

@app.route('/set_webhook')
def set_webhook():
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{API_KEY}"
    success = bot.set_webhook(webhook_url)
    return f"Webhook {'установлен' if success else 'не удалось'}: {webhook_url}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10001, debug=True)
