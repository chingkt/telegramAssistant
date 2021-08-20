import os
import time
from forex_python.converter import CurrencyRates
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from user import User

OPTION, EXCHANGE, AMOUNT, CALCULATE = range(4)
users = dict()


def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about what they want to know"""
    reply_keyboard = [['Exchange Rate']]
    user = User(update.message.from_user.id)
    users[user.tg_id] = user

    update.message.reply_text(
        'What do you want to know?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='exchange rate?'
        ),
    )

    return OPTION


def option(update: Update, context: CallbackContext) -> int:
    """Asks for the first currency if the option is exchange rate"""
    if update.message.text == 'Exchange Rate':
        reply_keyboard = [['HKD', 'EUR'],
                          ['USD', 'GBP', 'CNY']]
        update.message.reply_text(
            'first currency',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder='first currency'
            ),
        )
        return EXCHANGE


def exchange(update: Update, context: CallbackContext) -> int:
    """Asks for the second currency"""
    user = users.get(update.message.from_user.id)

    user.info["first"] = update.message.text

    reply_keyboard = [['HKD', 'EUR'],
                      ['USD', 'GBP', 'CNY']]
    update.message.reply_text(
        'second currency',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='second currency'
        ),
    )
    return AMOUNT

def amount(update: Update, context: CallbackContext) -> int:
    """asks if certain amount should be calculated"""
    user = users.get(update.message.from_user.id)
    user.info["second"] = update.message.text
    update.message.reply_text("Do you need to convert an amount? Please enter 'No' or a number.")

    return CALCULATE

def calculate(update: Update, context: CallbackContext) -> int:
    """request the exchange rate from forex python converter api"""
    user = users.get(update.message.from_user.id)
    first = user.info["first"]
    second = user.info["second"]

    msg = update.message.text
    if msg == "No":
        update.message.reply_text(CurrencyRates().get_rate(first, second))
    elif msg.isnumeric() and int(msg) > 0:
        update.message.reply_text(CurrencyRates().convert(first, second, int(msg)))
    else:
        update.message.reply_text("Answer invalid. Please enter 'No' or a number.")
        return CALCULATE
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.

    TOKEN = os.environ["TEL_TOKEN"]
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            OPTION: [MessageHandler(Filters.regex('^(Exchange Rate)$'), option)],
            EXCHANGE: [MessageHandler(Filters.regex('^(HKD|EUR|USD|GBP|CNY)$'), exchange)],
            AMOUNT: [MessageHandler(Filters.regex('^(HKD|EUR|USD|GBP|CNY)$'), amount)],
            CALCULATE: [MessageHandler(Filters.text, calculate)]
        },
        fallbacks=[CommandHandler('cancel', start)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
