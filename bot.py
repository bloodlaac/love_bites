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

FOOD_CHOICE, BUYING_DECITION = 0, 1
TOTAL_COST, TOTAL_TIME = 0, 0

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

price_time_dict = {
    "current_price": 0,
    "current_time": 0
}

food_options = [
    [
        InlineKeyboardButton("Омлет с ветчиной 🍳", callback_data="Омлет"),
        InlineKeyboardButton("Скрррембл 🥚", callback_data="Скрембл")
    ],
    [
        InlineKeyboardButton("Блинчики 🥞", callback_data="Блинчики"),
        InlineKeyboardButton("Каша 🥣", callback_data="Каша")
    ]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Доброе утро, {user.first_name}. Я официант в кафе Вафельки.\n\n"
        "Чем завтракаем сегодня? 😊",

        reply_markup=InlineKeyboardMarkup(food_options)
    )

    return FOOD_CHOICE

async def choose_meal_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:    
    query = update.callback_query
    chosen_food = query.data

    cost = food_dict[chosen_food][0]
    time = food_dict[chosen_food][1]
    file_name = food_dict[chosen_food][2]

    price_time_dict["current_price"] = cost
    price_time_dict["current_time"] = time

    text = (
        f"{chosen_food}\n\n"
        f"💋 Стоимость: {cost} поцелуйчик(а/ов)\n"
        f"⏳ Время приготовления: {time} минут"
    )

    with open(f"./Sources/{file_name}", "rb") as file:
        input_file = InputFile(file)

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=input_file, caption=text)

    actions_options = [
        [
            InlineKeyboardButton("Добавить в корзину", callback_data="add_to_cart"),
            InlineKeyboardButton("Купить сейчас", callback_data="buy_now")
        ],
        [
            InlineKeyboardButton("Мне расхотелось :(", callback_data="no_need")
        ]
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Что делаем дальше?",
        reply_markup=InlineKeyboardMarkup(actions_options)
    )

    return BUYING_DECITION

async def is_in_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TOTAL_COST, TOTAL_TIME
    
    query = update.callback_query
    print(query.data)

    match query.data:
        case "add_to_cart":
            TOTAL_COST += price_time_dict["current_price"]
            TOTAL_TIME += price_time_dict["current_time"]

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f"Общая стоимость завтрака: {TOTAL_COST} поцелуйчиков\n"
                    f"Время приготовления: {TOTAL_TIME} минут"
                ),
                reply_markup=InlineKeyboardMarkup(food_options)
                # query = update.
            )

            #return FOOD_CHOICE
        
        case "buy_now":
            TOTAL_COST += price_time_dict["current_price"]
            TOTAL_TIME += price_time_dict["current_time"]

            await update.message.reply_text(
                f"Общая стоимость завтрака: {TOTAL_COST} поцелуйчиков\n"
                f"Время приготовления: {TOTAL_TIME} минут\n\n"
                f"⏰Ожидайте ваш завтрак"
            )

            return ConversationHandler.END
        
        case "no_need":
            ...

async def next_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_action = update.message.reply_markup
    
    print(user_action)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FOOD_CHOICE: [CallbackQueryHandler(choose_meal_button)],
            BUYING_DECITION: [CallbackQueryHandler(is_in_cart)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(choose_meal_button, pattern="^(Омлет|Скрембл|Блинчики|Каша)$"))
    application.add_handler(CallbackQueryHandler(is_in_cart, pattern="^(add_to_cart|buy_now|no_need)$"))
    application.add_handler(CallbackQueryHandler(next_actions))
    #application.add_handler(CommandHandler("help", help_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()