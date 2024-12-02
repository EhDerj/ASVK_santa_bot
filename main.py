from telebot import TeleBot, types
import json
import os

with open(f"token", "r") as file:
    token = file.readline()
bot = TeleBot(token)


@bot.message_handler(content_types=["text"])
def message_handler(message):
    match message.text:
        case "/start":
            greet(message)

        case "/info":
            get_info(message)

        case "/gift":
            gift_to(message)

        case "/members":
            members(message)

        case _:
            default(message)


def greet(message):
    id_str = str(message.from_user.id)

    if id_str not in os.listdir("data"):
        with open(f"data/{id_str}", "w") as file:
            json.dump(
                {
                    "name": f"{message.from_user.first_name} {message.from_user.last_name}",
                    "wish": None
                },
                file
            )

    bot.send_message(
        message.from_user.id,
        "Это бот для жеребьевки тайного санты на новогоднем корпоративе кафедры АСВК\n"
    )
    get_info(message)


def get_info(message):
    id_str = str(message.from_user.id)
    with open(f"data/{id_str}", "r") as file:
        data = json.load(file)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text="Изменить имя", callback_data="name_change"),
        types.InlineKeyboardButton(text="Изменить пожелания", callback_data="wish_change")
    )

    bot.send_message(
        message.from_user.id,
        f"Ваше текущее имя: {data['name'] if data['name'] else 'Отсутствует'}\n"
        f"Ваши текущие пожелания: {data['wish'] if data['wish'] else 'Отсутствуют'}\n"
        f"Желаете что-то изменить?",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    match call.data:
        case "name_change":
            bot.send_message(
                call.message.chat.id,
                "Введите новое имя"
            )
            bot.register_next_step_handler(call.message, change_name)
        case "wish_change":
            bot.send_message(
                call.message.chat.id,
                "Введите новые пожелания"
            )
            bot.register_next_step_handler(call.message, change_wish)


def change_name(message):
    id_str = str(message.from_user.id)
    with open(f"data/{id_str}", "r") as file:
        data = json.load(file)
    data["name"] = message.text
    bot.send_message(
        message.from_user.id,
        f"Имя изменено на: {data['name']}"
    )
    with open(f"data/{id_str}", "w") as file:
        json.dump(data, file)


def change_wish(message):
    id_str = str(message.from_user.id)
    with open(f"data/{id_str}", "r") as file:
        data = json.load(file)
    data["wish"] = message.text
    bot.send_message(
        message.from_user.id,
        f"Пожелания изменены на: {data['wish']}"
    )
    with open(f"data/{id_str}", "w") as file:
        json.dump(data, file)


def gift_to(message):
    bot.send_message(
        message.from_user.id,
        "Жеребьевка пока не проводилась"
    )


def members(message):
    names = []
    for id_str in os.listdir("data"):
        with open(f"data/{id_str}", "r") as file:
            data = json.load(file)
        names.append(data["name"])
    names = "\n".join(names)

    bot.send_message(
        message.from_user.id,
        f"Текущие участники: \n{names}"
    )


def default(message):
    bot.send_message(
        message.from_user.id,
        "Неизвестная команда"
    )


if __name__ == "__main__":
    if "data" not in os.listdir("."):
        os.mkdir("data")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)