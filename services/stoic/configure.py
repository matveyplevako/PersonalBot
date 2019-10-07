from services.stoic.functions import *
from telegram.ext import MessageHandler, Filters, CommandHandler, CallbackQueryHandler


def setup(updater):
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.regex("Daily stoic quote"), stoic_menu))
    dispatcher.add_handler(MessageHandler(Filters.regex("Get quote for today"), get_quote_for_today))

    adding_new_attendance_record = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Get quote by day"), get_day_from_user)],
        states={
            PROCESS_DAY: [MessageHandler(Filters.text, get_quote_selected_day, pass_chat_data=True)],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    )

    dispatcher.add_handler(adding_new_attendance_record)
    dispatcher.add_handler(CallbackQueryHandler(get_content, pattern="^(ru|eng|img)"))


'''
add to menu
daily stoic citations

get citation for today
set time to receive new citation
get citation by day

'''
