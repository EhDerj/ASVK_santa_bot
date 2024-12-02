from telebot import TeleBot, types
import json
import os

with open(f"token", "r") as file:
    token = file.readline()
bot = TeleBot(token)


@bot.message_handler(content_types=["text"])
def message_handler(message):
    match message.text, str(message.from_user.id):
        case "/ahelp", "495668267":
            bot.send_message(
                "495668267",
                "/ahelp\n/ainfo\n/adel"
            )

        case "/ainfo", "495668267":
            admin_info(message)

        case "/adel", "495668267":
            bot.register_next_step_handler(message, admin_delete)

        case "/start", _:
            greet(message)

        case "/info", _:
            get_info(message)

        case "/gift", _:
            gift_to(message)

        case "/members", _:
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
    if id_str not in os.listdir("data"):
        bot.send_message(
            message.from_user.id,
            "Пожалуйста введите /start для регистрации"
        )
        return
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
    if id_str not in os.listdir("data"):
        bot.send_message(
            message.from_user.id,
            "Пожалуйста введите /start для регистрации"
        )
        return

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
    if id_str not in os.listdir("data"):
        bot.send_message(
            message.from_user.id,
            "Пожалуйста введите /start для регистрации"
        )
        return

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
    for n, id_str in enumerate(os.listdir("data"), 1):
        with open(f"data/{id_str}", "r") as file:
            data = json.load(file)
        names.append(f"{n}. {data['name']}")
    names = "\n".join(names)

    bot.send_message(
        message.from_user.id,
        f"Текущие участники: \n{names}"
    )


def admin_info(message):
    for id_str in os.listdir("data"):
        with open(f"data/{id_str}", "r") as file:
            data = json.load(file)
        bot.send_message(
            message.from_user.id,
            f"{id_str}-{data['name']}"
        )


def admin_delete(message):
    id_str, name = str(message.text).split("-")
    if id_str not in os.listdir("data"):
        bot.send_message(
            message.from_user.id,
            "Нет такого id"
        )
        return

    with open(f"data/{id_str}", "r") as file:
        data = json.load(file)

    if name != data["name"]:
        bot.send_message(
            message.from_user.id,
            "Имя не совпадает"
        )
        return

    os.remove(f"data/{id_str}")
    bot.send_message(
        message.from_user.id,
        f"{message.text} удален"
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