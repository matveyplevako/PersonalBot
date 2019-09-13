from services.initial.functions import *
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters


def setup(updater):
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.regex("Menu|Back to menu"), menu))
    dispatcher.add_handler(MessageHandler(Filters.regex("Settings|Back to settings"), settings))
