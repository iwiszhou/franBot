#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
#https://api.telegram.org/bot7057874595:AAHeKGei04fFpKYIozkOVcILu8Mi6DH5pN8/getWebhookInfo
#https://docs.python-telegram-bot.org/en/stable/examples.echobot.html
#https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#creating-a-self-signed-certificate-using-openssl
import os
import redis
import logging
import configparser
from ChatGPT_HKBU import HKBU_ChatGPT


from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logging.info("calling start function\nUpdate: {}".format(str(update)))
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    logging.info("calling help_command function\nUpdate: {}".format(str(update)))
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    logging.info("calling echo function\nUpdate: {}".format(str(update)))
    await update.message.reply_text(update.message.text)

async def equiped_chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    logging.info("calling equiped_chatgpt function\nUpdate: {}".format(str(update)))
    chatgpt = HKBU_ChatGPT()
    reply_message = chatgpt.submit(update.message.text)
    await update.message.reply_text(reply_message)
    #context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

async def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    logging.info("calling add function\nUpdate: {}".format(str(update)))
    try:
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        logging.info(context.args[0])
        db = redis.Redis(host=(os.environ['REDIS_HOST']),password=(os.environ['REDIS_PASSWORD']),port=(os.environ['REDIS_PORT']))
        db.incr(msg)
        await update.message.reply_text('You have said ' + msg +  ' for ' + db.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        await update.message.reply_text('Usage: /add <keyword>')

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token((os.environ['TELEGRAM_ACCESS_TOKEN'])).build()

    #redis = redis.Redis(host=(os.environ['REDIS_HOST']), password=(os.environ['REDIS_PASSWORD']), port=(os.environ['REDIS_REDISPORT']))

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - Handles the message on Chatgpt 
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), equiped_chatgpt))
    # on non command i.e message - echo the message on Telegram
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_webhook(
        listen=(os.environ['LOCALHOST']),
        port=(os.environ['LISTEN_PORT']),
        url_path=(os.environ['URL_PATH']),
        secret_token=(os.environ['SECRET_TOKEN']),
        #secret_token='comp7940-group-al',
        #key='private.key',
        cert=(os.environ['CERT_PATH']),
        webhook_url=(os.environ['WEBHOOK_URL'])
        #webhook_url='https://35.185.245.61:8443',
        #allowed_updates=Update.ALL_TYPES
    )
    #application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()