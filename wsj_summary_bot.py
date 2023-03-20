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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

WSJ_URL = 'https://www.wsj.com/'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def get_top_stories():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')  # Only add this line if running in a headless environment
    
        # Replace '/path/to/chromedriver' with the path to your ChromeDriver binary if needed
    chrome_driver_path = '/usr/local/bin/chromedriver'
    service = Service(executable_path=chrome_driver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(WSJ_URL)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    top_stories = soup.find_all('h3', {'class': 'WSJTheme--headlineText--He1ANr9C'})

    driver.quit()
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

async def send_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_stories = get_top_stories()
    summaries = [summarize(story.text) for story in top_stories]

    # Add print statements for debugging
    print("Top stories:", top_stories)
    print("Summaries:", summaries)

    message = "\n\n".join(summaries)
    
    # Check if the message is empty
    if not message.strip():
        message = "Sorry, I couldn't generate summaries for the top stories at this moment."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def daily_summary():
    send_summary()

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    summary_handler = CommandHandler('summary', send_summary)
    start_handler = CommandHandler('start', start)

    application.add_handler(start_handler)
    application.add_handler(summary_handler)
    application.run_polling()

    # schedule.every().day.at("08:00").do(daily_summary)
    while True:
        schedule.run_pending()
        time.sleep(1)
    updater.idle()

if __name__ == '__main__':
    main()
