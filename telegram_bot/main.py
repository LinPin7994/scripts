from locale import currency
import telebot
from telebot import types
from hh import Vacancies
from weather import Weather
from wiki import Wiki
from exchange import Exchange

telegram_bot_token = "<YOU TELEGRAM BOT TOKEN>"

bot = telebot.TeleBot(telegram_bot_token)

@bot.message_handler(commands=["start"])
def start(m):
    markup_inline = types.InlineKeyboardMarkup(row_width=2)
    weather_button = types.InlineKeyboardButton("Узнать погоду", callback_data="weather")
    hh_button = types.InlineKeyboardButton("Вакансии на Кипре", callback_data="cyprus")
    exchange_button = types.InlineKeyboardButton("Курсы валют", callback_data="ex")
    converter_button = types.InlineKeyboardButton("Конвертер валют", callback_data="convert")
    help_button = types.InlineKeyboardButton("Помощь", callback_data="help")
    wiki_button = types.InlineKeyboardButton("Wiki", callback_data="wiki")
    markup_inline.add(weather_button, hh_button, exchange_button, help_button, wiki_button, converter_button)
    if m.text == "/start":
        bot.send_message(m.chat.id, "Добро пожаловать в инфо Бот!", reply_markup=markup_inline)

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    currency_menu = types.InlineKeyboardMarkup(row_width=3)
    converter_menu = types.InlineKeyboardMarkup(row_width=3)
    convert_usd_button = types.InlineKeyboardButton("USD/RUB", callback_data="convert_usd_rub")
    convert_amd_button = types.InlineKeyboardButton("AMD/RUB", callback_data="convert_amd")
    convert_eur_button = types.InlineKeyboardButton("EUR/RUB", callback_data="convert_eur")
    convert_rub_to_usd_button = types.InlineKeyboardButton("RUB/USD", callback_data="convert_rub_to_usd")
    convert_rub_to_amd_button = types.InlineKeyboardButton("RUB/AMD", callback_data="convert_rub_to_amd")
    convert_rub_to_eur_button = types.InlineKeyboardButton("RUB/EUR", callback_data="convert_rub_to_eur")
    usd_rub_button = types.InlineKeyboardButton("USD/RUB", callback_data="usd_rub")
    amd_rub_button = types.InlineKeyboardButton("AMD/RUB", callback_data="amd_rub")
    euro_rub_button = types.InlineKeyboardButton("EUR/RUB", callback_data="eur_rub")
    currency_menu.add(usd_rub_button, amd_rub_button, euro_rub_button)
    converter_menu.add(convert_usd_button, convert_amd_button, convert_eur_button, convert_rub_to_usd_button, convert_rub_to_amd_button, convert_rub_to_eur_button)
    if call.message:
        if call.data == "weather":
            msg = bot.send_message(call.message.chat.id, "Введите название города: ")
            bot.register_next_step_handler(msg, show_weather)
        elif call.data == "cyprus":
            vac = Vacancies()
            vac_message = vac.get_vacancies()
            bot.send_message(call.message.chat.id, vac_message)
        elif call.data == "wiki":
            msg = bot.send_message(call.message.chat.id, "Введите запрос в wikipedia")
            bot.register_next_step_handler(msg, show_wiki_answer)
        elif call.data == "ex":
            bot.send_message(call.message.chat.id, "Курсы валют", reply_markup=currency_menu)
        elif call.data == "usd_rub":
            currency_usd_rub = Exchange("USDRUB")
            valutes_currency = float(currency_usd_rub.get_currency_exchange())
            message = f"USD: 1 => RUB: {round(valutes_currency, 2)}"
            bot.send_message(call.message.chat.id, message)
        elif call.data == "amd_rub":
            currency_amd_rub = Exchange("AMDRUB")
            valutes_currency = float(currency_amd_rub.get_currency_exchange())
            bot.send_message(call.message.chat.id, f"AMD: 1 => RUB: {round(valutes_currency, 2)}")
        elif call.data == "eur_rub":
            currency_eur_rub = Exchange("EURRUB")
            valutes_currency = float(currency_eur_rub.get_currency_exchange())
            bot.send_message(call.message.chat.id, f"EUR: 1 => RUB: {round(valutes_currency, 2)}")
        elif call.data == "help":
            bot.send_message(call.message.chat.id, "Для началы работы с ботом напишите /start")
        elif call.data == "convert":
            bot.send_message(call.message.chat.id, "Конвертер валют", reply_markup=converter_menu)
        elif call.data == "convert_rub_to_usd":
            msg = converter_send_message(call)
            bot.register_next_step_handler(msg, run_converter, "RUBUSD")
        elif call.data == "convert_usd_rub":
            msg = converter_send_message(call)
            bot.register_next_step_handler(msg, run_converter, "USDRUB")
        elif call.data == "convert_rub_to_amd":
            msg = converter_send_message(call)
            bot.register_next_step_handler(msg, run_converter, "RUBAMD")
        elif call.data == "convert_rub_to_eur":
            msg = converter_send_message(call)
            bot.register_next_step_handler(msg, run_converter, "RUBEUR")
        elif call.data == "convert_amd":
            msg = converter_send_message(call)
            bot.register_next_step_handler(msg, run_converter, "AMDRUB")
        elif call.data == "convert_eur":
            msg = converter_send_message(call)
            bot.register_next_step_handler(msg, run_converter, "EURRUB")

@bot.message_handler(content_types=["text"])
def message_handler(m):
    bot.send_message(m.chat.id, "Неверная команда")

def converter_send_message(call):
    msg = bot.send_message(call.message.chat.id, "Введите конвертируемую сумму")
    return msg

def show_weather(msg):
    weather = Weather(msg.text)
    weather_in_city = weather.get_current_weather()
    bot.send_message(msg.chat.id, weather_in_city)

def show_wiki_answer(msg):
    wiki = Wiki(msg.text)
    wiki_response = wiki.get_wiki_info()
    bot.send_message(msg.chat.id, wiki_response)

def run_converter(msg, ex):
    valute = Exchange(ex)
    first_ex = ex[:3]
    second_ex = ex[3:]
    currency = valute.get_currency_exchange()
    sum = int(msg.text)
    result = sum * float(currency)
    bot.send_message(msg.chat.id, f" {sum} {first_ex} => {round(result, 2)} {second_ex}")

def main():
    bot.polling(none_stop=True, interval=0)

if __name__ == "__main__":
    main()
