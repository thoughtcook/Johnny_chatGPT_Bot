import os
import requests
import schedule
import time
from config import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, YOUR_CHAT_ID
from bs4 import BeautifulSoup
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

WSJ_URL = 'https://www.wsj.com/'


def get_top_stories():
    response = requests.get(WSJ_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    top_stories = soup.find_all('h3', {'class': 'WSJTheme--headline'})
    return top_stories[:10]

def summarize(text):
    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=f"Please summarize the following news article: {text}",
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )
    summary = response.choices[0].text.strip()
    return summary

def send_summary(chat_id):
    top_stories = get_top_stories()
    summaries = [summarize(story.text) for story in top_stories]
    message = "\n\n".join(summaries)
    updater.bot.send_message(chat_id=chat_id, text=message)

def daily_summary():
    send_summary(YOUR_CHAT_ID)

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("summary", send_summary))
    updater.start_polling()
    updater.idle()
    updater.start_polling()
    schedule.every().day.at("08:00").do(daily_summary)
    while True:
        schedule.run_pending()
        time.sleep(1)
    updater.idle()

if __name__ == '__main__':
    main()
