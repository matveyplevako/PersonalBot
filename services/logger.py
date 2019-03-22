import logging
import os

if not os.path.isfile('./logs/bot.log'):
    os.mkdir("logs")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s:%(lineno)d'
                           ' - %(message)s', handlers=[logging.FileHandler('logs/bot.log'),
                                                       logging.StreamHandler()], level=logging.INFO)
logger = logging.getLogger(__name__)
