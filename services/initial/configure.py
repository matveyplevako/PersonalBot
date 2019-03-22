from services.initial.functions import *
from telegram.ext import CommandHandler
from telegram.ext import RegexHandler


def setup(updater):
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(RegexHandler("Menu|Back to menu", menu))
    dispatcher.add_handler(RegexHandler("Settings|Back to settings", settings))
