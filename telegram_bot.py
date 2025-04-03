# -*- coding: utf-8 -*-
import os
import time
import requests
import json
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

API_KEY = os.getenv("telgram_real_bot_api")
token_url = os.getenv("token_url")
bin_url_2 = os.getenv("bin_url_2")
bin_url_1 = "https://api.adata.kz/api/company/"

bot = telebot.TeleBot(API_KEY)
app = Flask(__name__)

allowed_users = {
    7932774397: "Аруна",
    528517673: "Ескатов Алишер Маратович",
    1115327907: "Сафонов Александр",
    1090349915: "Баймурзинов Рустем Муратович",
    1106476172: "Абдиров Бекбулат Кайратович",
    435397805: "Глазырин Вячеслав Александрович",
    7852053436: "Коржов Дмитрий Александрович",
    752841282: "Шадрин Виталий Вячеславович",
    549557630: "Есентаев Дамир ",
    992265183: "Балгожа Рауан Еркебуланулы",
    1070083923: "Шубин Глеб Владимирович",
    1236379606: "Гугневич Евгений Павлович",
    1601907399: "Нургалиев Еламан",
    527670595: "Садовский Игорь Вальревич",
    7507209038: "Паршутин Евгений Игоревич",
    1787060581: "Вахнина Виктория Анатольевна",
    5087650386: "Кулбулдин Бауыржан",
    368200758: "Жунусов Айдын Бекович",
    6568553601: "Усенов Асанали Асхатович",
    7306728048: "Перешивкин Игорь",
    5970079059: "Шпаковский Сергей",
    717489456: "Шаткенов Арлан Нурдаулетович",
    5442237913: "Солдатенков Артем Викторович",
    543024941: "Жакиенов Данияр Берикович",
    477248141: "Анишкевич Владислав Сергеевич",
    780568746: "Терещенко Александр Григорьевич",
    2020413343: "Нургалиев Данияр Рамазанович",
    5303738892: "Койгелды Женис Даулетулы",
    508256083: "Яковлев Александр Александрович",
    8107067331: "Байгазиев Александр",
    1016809072: "Адомайтис Евгений",
    1897623417: "Лубянецкий Алексей Петрович",
    875411607: "Карташов Олег Валерьевич",
    1981124911: "Шульц Николай Викторович",
    6231136971: "Амирбек Жанибек Адильбекович",
    5176965194: "Кализатов Бауыржан Канатович",
    828188265: "Калиев Жанибек",
    782238817: "Сидоренко Алексей Александрович",
    7248286025: "Бородич Николай Михайлович",
    8088143874: "Авижич Виктор Викторович",
    436769994: "Максимов Станислав Валерьевич",
    230004989: "Кадырбек Куат",
    473547152: "Таукин Канат Аблаевич",
    516180924: "Ибраев Акежан Аулиханович",
    5679662661: "Соловьев Евгений Александрович",
    353184443: "Куташов Виталий",
    6110113341: "Тургумбаев Ильяс",
    715691300: "Турежанов Булат Агибаевич",
    1633629108: "Мади Назарбек",
    1372719987: "Джиоев Георгий",
    7022099012: "Сейдыков Максим Евгеньевич",
    7731034003: "Куаныш Мамбетов",
    592052143: "Герасимов Виталий Валерьевич",
    5672873644: "Жанат Охатов",
    170233096: "Наталья",
    7260153078: "Нурсултан",
    712766177: "Мурат",
    6263090827: "Кабимулдин Руфат Асетович",
    2096887718: "Ключка Сергей Сергеевич",
    6425627696: "Джексенбаев Ринат Каденович",
    5536766070: "Клиновицкий Андрей Александрович ",
    803315196: "Рак Егор Валерьевич",
    357140691: "Сериков Бахтияр",
    591725711: "Дауленов Азамат Айтжанович",
    5003150190: "Садвокасов Рустам",
    7687709758: "Жайырбаев Даурен Беимбекович",
    1101041371: "Яцынович Константин Юрьевич",
    892390481: "Бойко Олег",
    5086276503: "Асет Мукушев",
    7017920749: "Динара Айдарова",
    885253145: "Нуртуган",
    808225428: "Сундетбаев Болат"
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
    bot.send_message(message.chat.id, "\u23F3 Идёт проверка...")

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
            info.append("\u2757 В списке «Бездействующее предприятие»")
        if status['bankcrupt']:
            info.append("\u2757 В списке «Банкрот»")
        if risk['company']['seized_bank_account']:
            info.append("\u2757 Арест на банковские счета")
        if risk['company']['seized_property']:
            info.append("\u2757 Арест на имущество")
        if risk['company']['ban_registration_actions_legal_ent']:
            info.append("\u2757 Запрет на регистрационные действия ЮЛ")
        if risk['company']['ban_registration_actions_physical_ent']:
            info.append("\u2757 Запрет на регистрационные действия ФЛ")
        if risk['company']['ban_notarius_actions']:
            info.append("\u2757 Запрет на совершение нотариальных действий")
        if risk['head']['enforcement_debt']:
            info.append("\u2757 Должник по исполнительным производствам")
        if risk['head']['debtor_for_executive_documents']:
            info.append("\u2757 В списке должников по исполнительным документам")
        if trust['tax_arrears_150']:
            info.append("\u2757 Налоговая задолженность более 150 МРП")
        if trust['restriction_on_leaving']:
            info.append("\u2757 Временное ограничение на выезд из РК")
        if trust['transport_arrest']:
            info.append("\u2757 Арест на транспорт")

        send_company_info(bot, message.chat.id, basic)

        if not info:
            bot.send_message(message.chat.id, "Проблем нет ✅")
        else:
            for i in info:
                bot.send_message(message.chat.id, i)

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
    app.run(host='0.0.0.0', port=10000)