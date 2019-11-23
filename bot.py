from telegram.ext import Updater
import os
from services.initial.configure import setup as setup_initial
from services.email.configure import setup as setup_email
from services.sport_attendance.configure import setup as setup_sport_attendance
from services.stoic.configure import setup as setup_stoic
from services.RedisPersistence import RedisPersistence
import redis
import logging

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


def main():
    TOKEN = os.environ['BOT_TOKEN']
    redis_connection = redis.from_url(os.environ["REDISCLOUD_URL"])

    updater = Updater(token=TOKEN, use_context=True,
                      persistence=RedisPersistence(redis_connection))

    setup_initial(updater)
    setup_email(updater)
    setup_sport_attendance(updater)
    setup_stoic(updater)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
