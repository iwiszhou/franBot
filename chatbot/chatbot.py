# from dotenv import load_dotenv
# load_dotenv()
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
#https://api.telegram.org/bot<YOUR_OWN_TELEGRAM_TOKEN>/getWebhookInfo
#https://docs.python-telegram-bot.org/en/stable/examples.echobot.html
#https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#creating-a-self-signed-certificate-using-openssl
import os
import redis
import logging
from ChatGPT_HKBU import HKBU_ChatGPT
import json
import time

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def getMessageWithBotName(str):
    try:
        botNameWithPort = f"(Bot-%s)"%os.environ['LISTEN_PORT']
        return botNameWithPort + str
    except:
        logging.info("Not able get bot port number.")
        return str

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logging.info("calling start function\nUpdate: {}".format(str(update)))
    user = update.effective_user
    response_msg = 'Hi there! \n '
    response_msg += 'You can /review to start to read/write TV show review! \n'
    response_msg +='You can also /allReviews to quickly review! \n'
    response_msg += 'You can /video to start to share your video link! \n'
    response_msg +='You can also /allVideos to quickly view all links! \n'
    response_msg += 'Directly typing text our smart ChatGPT will assist you!'
    await update.message.reply_text(getMessageWithBotName(response_msg))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    logging.info("calling help_command function\nUpdate: {}".format(str(update)))
    await update.message.reply_text(getMessageWithBotName("Help!"))


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    logging.info("calling echo function\nUpdate: {}".format(str(update)))
    await update.message.reply_text(getMessageWithBotName(update.message.text))

async def equiped_chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    logging.info("calling equiped_chatgpt function\nUpdate: {}".format(str(update)))
    chatgpt = HKBU_ChatGPT()
    reply_message = chatgpt.submit(update.message.text)
    await update.message.reply_text(getMessageWithBotName(reply_message))

async def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    logging.info("calling add function\nUpdate: {}".format(str(update)))
    try:
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        logging.info(context.args[0])
        db = redis.Redis(host=(os.environ['REDIS_HOST']),password=(os.environ['REDIS_PASSWORD']),port=(os.environ['REDIS_PORT']))
        db.incr(msg)
        response_msg = getMessageWithBotName('You have said ' + msg +  ' for ' + db.get(msg).decode('UTF-8') + ' times.')
        await update.message.reply_text(response_msg)
    except (IndexError, ValueError):
        await update.message.reply_text('Usage: /add <keyword>')

async def launch_web_ui(update: Update, callback: CallbackContext):
    logging.info("calling launch_web_ui function\nUpdate: {}".format(str(update)))
    # display our web-app!
    kb = [
        [KeyboardButton(
            "Start to read/write TV show review",
            web_app=WebAppInfo(url="https://iwiszhou.github.io/franBot/index.html")
        )]
    ]
    await update.message.reply_text(getMessageWithBotName("Launching the TV show review..."), reply_markup=ReplyKeyboardMarkup(kb))


async def web_app_data(update: Update, context: CallbackContext):
    logging.info("calling web_app_data function\nUpdate: {}".format(str(update)))
    try:
        global redisClient
        data = json.loads(update.message.web_app_data.data)
        print(data)
        # store to redis
        redisClient.hset("tvReview", data['key'], json.dumps(data)) 
        await update.message.reply_text(getMessageWithBotName("Thank you for your review!"))
    except (IndexError, ValueError):
        print(ValueError)
        await update.message.reply_text(getMessageWithBotName('Unable to process the save review feature. Please try later'))

async def show_all_reviews(update: Update, context: CallbackContext):
    logging.info("calling show_all_reviews function\nUpdate: {}".format(str(update)))
    try:
        global redisClient
        # get all review data from redis
        data = redisClient.hgetall("tvReview")
        html_string = '<b>'+ getMessageWithBotName("All reviews:") + '</b>\n'
         # Parse JSON data and construct HTML string
        for key, value in data.items():
            review = json.loads(value)
            show_name = review.get("showName", "")
            author = review.get("author", "")
            review_text = review.get("review", "")
            html_string += f"<b>------------------------</b>\n<code><u>Show Name: {show_name}</u>, <b>Author:</b> {author}, <b>Review:</b> {review_text}</code>\n"

        # Reply with HTML formatted message
        await update.message.reply_html(html_string)
    except (IndexError, ValueError):
        print(ValueError)
        await update.message.reply_text('Unable to process the get all reviews. Please try later')

async def share_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("calling share_video function\nUpdate: {}".format(str(update)))
    user = update.effective_user
    print(user['first_name'])
    msg = getMessageWithBotName(rf"Hi {user.mention_html()}! You can paste your Youtube video link below to share your video to others")
    response_data  = await update.message.reply_html(
        msg,
        reply_markup=ForceReply(selective=True),
    )
    print("video resp",response_data)

async def handle_video_response(update:Update, context: CallbackContext):
    logging.info("calling handle_video_response function\nUpdate: {}".format(str(update)))
    try:
        user = update.effective_user
        author = user['first_name'] + " " + user['last_name']
        link = update.message.text
        key = user['first_name'] + "_" + str(time.time_ns())
        userId = user['id']
        data = {
            'author': author,
            'link': link,
            'userId': userId
        }
        global redisClient
        # print(redisClient.hgetall('videos'))
        print(data)
        # store to redis
        redisClient.hset("videos", key, json.dumps(data)) 
        await update.message.reply_html(getMessageWithBotName("Thank you sharing your video!"))
    except (IndexError, ValueError):
        print(ValueError)
        await update.message.reply_text(getMessageWithBotName('Unable to process the save video link. Please try later'))

async def show_all_videos(update: Update, context: CallbackContext):
    logging.info("calling show_all_videos function\nUpdate: {}".format(str(update)))
    try:
        global redisClient
        # get all review data from redis
        data = redisClient.hgetall("videos")
        print(data)
        html_string = '<b>'+ getMessageWithBotName("All videos:") + '</b>\n'
         # Parse JSON data and construct HTML string
        for key, value in data.items():
            video = json.loads(value)
            v_link = video.get("link", "")
            v_author = video.get("author", "")
            html_string += f"<b>------------------------</b>\n<code><b>Author:</b> {v_author}, <b>Link:</b> {v_link}</code>\n"

        # Reply with HTML formatted message
        await update.message.reply_html(html_string)
    except (IndexError, ValueError):
        print(ValueError)
        await update.message.reply_text('Unable to process the get all reviews. Please try later')


def main() -> None:
    #Init redis
    global redisClient
    redisClient = redis.Redis(host=(os.environ['REDIS_HOST']),
    password=(os.environ['REDIS_PASSWORD']),
    port=(os.environ['REDIS_PORT']),
    decode_responses=True)

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token((os.environ['TELEGRAM_ACCESS_TOKEN'])).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Video link share
    application.add_handler(CommandHandler("video", share_video))
    application.add_handler(CommandHandler("allVideos", show_all_videos))
    application.add_handler(MessageHandler(filters.TEXT & (filters.Entity("url") | filters.Entity("text_link")), handle_video_response))

    # ChatGPT - on non command i.e message - Handles the message on Chatgpt 
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), equiped_chatgpt))

    # TV Review
    application.add_handler(CommandHandler("allReviews", show_all_reviews))
    # and let's set a command listener for /start to trigger our Web UI
    application.add_handler(CommandHandler('review', launch_web_ui))
    # as well as a web-app listener for the user-inputted data
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))


    # Run the bot until the user presses Ctrl-C

    # Debug version - local
    # application.run_polling();

    # Prod version with webhook
    application.run_webhook(
        listen=(os.environ['LOCALHOST']),
        port=(os.environ['LISTEN_PORT']),
        url_path=(os.environ['URL_PATH']),
        secret_token=(os.environ['SECRET_TOKEN']),
        cert=(os.environ['CERT_PATH']),
        webhook_url=(os.environ['WEBHOOK_URL'])
    )

if __name__ == "__main__":
    main()