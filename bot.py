import logging
from tg_token import TOKEN

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    InputFile
)

from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# [0] - cost
# [1] - time
# [2] - file_name
food_dict = {
    "Омлет": (3, 20, "omelet.jpg"),
    "Скрембл": (2, 15, "scramble.jpg"),
    "Блинчики": (5, 40, "pancakes.jpg"),
    "Каша": (1, 20, "porridge.jpg"),
    "Кофе": (1, 2, "coffee.jpg"),
    "Чай": (1, 2, "tea.jpg")
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_options = [
        [
            InlineKeyboardButton("Омлет с ветчиной 🍳", callback_data="Омлет"),
            InlineKeyboardButton("Скрррембл 🥚", callback_data="Скрембл")
        ],
        [
            InlineKeyboardButton("Блинчики 🥞", callback_data="Блинчики"),
            InlineKeyboardButton("Каша 🥣", callback_data="Каша")
        ]
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Доброе утро, {context.bot.first_name}. Я официант в кафе Вафельки.\n\n"
        "Чем завтракаем сегодня? 😊",

        reply_markup=InlineKeyboardMarkup(reply_options)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    cost = food_dict[query.data][0]
    time = food_dict[query.data][1]
    file_name = food_dict[query.data][2]

    text = (
        f"{query.data}\n\n"
        f"Стоимость: {cost} поцелуйчик(а/ов)\n"
        f"Время приготовления: {time} минут"
    )

    with open(f"./Sources/{file_name}", "rb") as file:
        input_file = InputFile(file)

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=input_file, caption=text)

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    #application.add_handler(CommandHandler("help", help_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()