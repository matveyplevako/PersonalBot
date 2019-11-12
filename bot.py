from telegram.ext import Updater
import os
from services.initial.configure import setup as setup_initial
from services.email.configure import setup as setup_email
from services.sport_attendance.configure import setup as setup_sport_attendance
from services.stoic.configure import setup as setup_stoic
import logging

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


def main():
    TOKEN = os.environ['BOT_TOKEN']
    PORT = int(os.environ.get('PORT', '8443'))
    updater = Updater(token=TOKEN, use_context=True)

    setup_initial(updater)
    setup_email(updater)
    setup_sport_attendance(updater)
    setup_stoic(updater)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook("https://dry-savannah-69984.herokuapp.com/" + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
