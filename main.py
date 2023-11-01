import telebot
import sqlite3

from newsapi import NewsApiClient


# подключение к базе данных
conn = sqlite3.connect('news.db')
cursor = conn.cursor()


# Init
newsapi = NewsApiClient(api_key='bdda7a7ac58d477c92bd22ce1276b40f')


TOKEN = '6235319425:AAFBgx4Pfbjq_r9_FShhBpjU06U8mqyT6rI'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['text'])
def talk(message):
    if message.text == 'Привет':
        bot.send_message(message.chat.id, 'Привет, как у тебя дела?')
    elif message.text == 'Нормально':
        bot.send_message(message.chat.id, 'Отлично! Я рад за Вас.')

def subscribe(chat_id, group_name):
    cursor.execute("SELECT * FROM groups WHERE name=?", (group_name,))
    group = cursor.fetchone()
    if group:
        cursor.execute("INSERT INTO subscriptions (chat_id, group_id) VALUES (?, ?)", (chat_id, group[0]))
        conn.commit()
        bot.send_message(chat_id, f"Вы подписались на группу {group_name}")
    else:
        bot.send_message(chat_id, f"Группа {group_name} не найдена")


# функция для отписки от группы
def unsubscribe(chat_id, group_name):
    cursor.execute("SELECT * FROM groups WHERE name=?", (group_name,))
    group = cursor.fetchone()
    if group:
        cursor.execute("DELETE FROM subscriptions WHERE chat_id=? AND group_id=?", (chat_id, group[0]))
        conn.commit()
        bot.send_message(chat_id, f"Вы отписались от группы {group_name}")
    else:
        bot.send_message(chat_id, f"Группа {group_name} не найдена")

# функция для получения новостей из группы
def get_news_for_group(group_id):
    cursor.execute("SELECT * FROM news WHERE group_id=? ORDER BY id DESC LIMIT 10", (group_id,))
    news = cursor.fetchall()
    return news

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Введите /subscribe <название группы>, чтобы подписаться на группу")

@bot.message_handler(commands=['subscribe'])
def subscribe_to_group(message):
    group_name = message.text.split(' ')[1]
    subscribe(message.chat.id, group_name)

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe_from_group(message):
    group_name = message.text.split(' ')[1]
    unsubscribe(message.chat.id, group_name)

@bot.message_handler(func=lambda message: True)
def get_news_for_user(message):
    cursor.execute("SELECT * FROM subscriptions WHERE chat_id=?", (message.chat.id,))
    subscriptions = cursor.fetchall()
    for subscription in subscriptions:
        news = get_news_for_group(subscription[1])
        for article in news:
            bot.send_message(message.chat.id, article[2] + "\n" + article[3])




bot.polling(none_stop=True)