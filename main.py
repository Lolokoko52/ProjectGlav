import telebot
import requests
import json
from currency_converter import CurrencyConverter
from telebot import types


bot = telebot.TeleBot('6431576369:AAGEZw6_k-FM6MwxlohYVv6v2CoXdfMPTQg')
API = '3d9de74844d28377e81415151cbe6a66'
currency = CurrencyConverter()
amount = 0

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} введите сумму')
    bot.register_next_step_handler(message, summa)

@bot.message_handler(commands=["weather"])
def weather(message):
    bot.send_message(message.chat.id, "Привет, рад тебя видеть! Напиши название города")

@bot.message_handler(content_types=["text"])
def get_weather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    data = json.loads(res.text)
    bot.reply_to(message, f'Сейчас погода: {res.json()}')
def summa(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат, введите сумму")
        bot.register_next_step_handler(message, summa)
        return
    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn2 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn3 = types.InlineKeyboardButton('USD/GBP', callback_data='usd/gbp')
        btn4 = types.InlineKeyboardButton('Другое значение', callback_data='else')
        markup.add(btn1,btn2,btn3,btn4)
        bot.send_message(message.chat.id, 'Выберете пару валют', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Число должно быть больше 0')
        bot.register_next_step_handler(message, summa)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != 'else':
        values = call.data.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f'Получается: {round(res, 2)}. Можете заново вписать сумму')
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, 'Введите пару значений через слэш')
        bot.register_next_step_handler(call.message, my_currency)

def my_currency(message):
    try:
        values = message.text.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'Получается: {round(res, 2)}. Можете заново вписать сумму')
        bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(message.chat.id, f'Что-то не так. Впишите значение заново')
        bot.register_next_step_handler(message, my_currency)



bot.polling(none_stop=True)