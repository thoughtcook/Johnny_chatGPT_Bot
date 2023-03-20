import os
import requests
import logging
import schedule
import time
from config import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, YOUR_CHAT_ID
from bs4 import BeautifulSoup
import openai
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

WSJ_URL = 'https://www.wsj.com/'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

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

def send_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_stories = get_top_stories()
    summaries = [summarize(story.text) for story in top_stories]
    message = "\n\n".join(summaries)
    context.bot.send_message(chat_id=YOUR_CHAT_ID, text=message.text)

def daily_summary():
    send_summary()

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    summary_handler = CommandHandler('summary', daily_summary)
    
    application.add_handler(CommandHandler("summary", daily_summary))
    application.run_polling()

    # schedule.every().day.at("08:00").do(daily_summary)
    while True:
        schedule.run_pending()
        time.sleep(1)
    updater.idle()

if __name__ == '__main__':
    main()
