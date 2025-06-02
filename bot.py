import logging
import telegram

from tg_token import TOKEN

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputFile
)

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
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

FOOD = ["Омлет", "Скрембл", "Блинчики", "Каша", "Кофе", "Чай"]

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
    global FOOD, TOTAL_COST, TOTAL_TIME
    user = update.message.from_user

    FOOD = list(food_dict.keys())
    TOTAL_COST = 0
    TOTAL_TIME = 0

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Доброе утро, {user.first_name}. Я официант в кафе Вафельки.\n\n"
        "Чем завтракаем сегодня? 😊",
        reply_markup=generate_food_buttons()
    )

    return FOOD_CHOICE

async def choose_meal_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:    
    query = update.callback_query
    await query.answer()

    chosen_food = query.data
    if chosen_food not in FOOD:
        return FOOD_CHOICE

    FOOD.remove(chosen_food)

    cost, time, file_name = food_dict[chosen_food]
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
        ]
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Что делаем дальше?",
        reply_markup=InlineKeyboardMarkup(actions_options)
    )

    return BUYING_DECITION

def generate_food_buttons() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(name, callback_data=name)
        for name in FOOD
    ]
    buttons.append(InlineKeyboardButton("🍽 Завершить заказ", callback_data="finish_order"))
    
    button_rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]

    return InlineKeyboardMarkup(button_rows)

async def is_in_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TOTAL_COST, TOTAL_TIME

    query = update.callback_query
    await query.answer()

    match query.data:
        case "add_to_cart":
            TOTAL_COST += price_time_dict["current_price"]
            TOTAL_TIME += price_time_dict["current_time"]

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f"Общая стоимость завтрака: {TOTAL_COST} поцелуйчиков\n"
                    f"Время приготовления: {TOTAL_TIME} минут\n\n"
                    f"Хотите выбрать что-то ещё?"
                ),
                reply_markup=generate_food_buttons()
            )
            return FOOD_CHOICE

        case "buy_now":
            TOTAL_COST += price_time_dict["current_price"]
            TOTAL_TIME += price_time_dict["current_time"]

        case "finish_order":
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f"💋 Итоговая стоимость: {TOTAL_COST} поцелуйчиков.\n"
                    f"⏳ Время приготовления: {TOTAL_TIME} минут.\n\n"
                    f"☺️ Спасибо за заказ! Приятного аппетита!"
                )
            )
            return ConversationHandler.END


    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"💋 Итоговая стоимость: {TOTAL_COST} поцелуйчиков.\n"
            f"⏳ Время приготовления: {TOTAL_TIME} минут.\n\n"
            f"☺️ Спасибо за заказ!"
        )
    )
    return ConversationHandler.END

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FOOD_CHOICE: [
                CallbackQueryHandler(choose_meal_button, pattern="^(Омлет|Скрембл|Блинчики|Каша|Кофе|Чай)$"),
                CallbackQueryHandler(is_in_cart, pattern="^finish_order$")
            ],
            BUYING_DECITION: [
                CallbackQueryHandler(is_in_cart, pattern="^(add_to_cart|buy_now)$")
            ]
        },
        fallbacks=[]
    )

    application.add_handler(conversation_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()