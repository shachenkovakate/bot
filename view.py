import asyncio
import datetime
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, BotCommand

import model

from tk import token

TOKEN = token
dp = Dispatcher()


async def setup_bot_commands(bot: Bot):
    bot_commands = [
        BotCommand(command="/earn", description="добавить доход"),
        BotCommand(command="/spend", description="добавить расход"),
        BotCommand(command="/mean_earn", description="вычислить средний дневной доход за период времени"),
        BotCommand(command="/mean_spend", description="вычислить средний дневной расход за период времени")
        ]
    await bot.set_my_commands(bot_commands)


@dp.message(Command("start"))
async def command_spend_handler(message: Message) -> None:
    user_id = message.from_user.id
    await model.create_user(user_id, 0)


@dp.message(Command("earn"))
async def command_earn_handler(message: Message) -> None:
    await message.answer('Введите полученную сумму')

    await model.change_state(message.from_user.id, 1)


async def earn(message: Message) -> None:
    value = int(message.text)
    user_id = message.from_user.id
    ts = datetime.datetime.now()
    await model.create_delta(user_id, ts, value)

    await message.answer(f"Ваш баланс изменён на {value}")

    await model.change_state(message.from_user.id, 0)


@dp.message(Command("spend"))
async def command_spend_handler(message: Message) -> None:
    await message.answer('Введите потраченную сумму')

    await model.change_state(message.from_user.id, 2)


async def spend(message: Message) -> None:
    value = int(message.text)
    user_id = message.from_user.id
    ts = datetime.datetime.now()
    await model.create_delta(user_id, ts, -value)
    await message.answer(f"Ваш баланс изменён на -{value}")

    await model.change_state(message.from_user.id, 0)


@dp.message(Command("mean_earn"))
async def command_mean_handler(message: Message) -> None:
    await message.answer('Введите временной промежуток в формате "ДД.ММ.ГГГГ-ДД.ММ.ГГГГ"')

    await model.change_state(message.from_user.id, 3)


@dp.message(Command("mean_spend"))
async def command_mean_handler(message: Message) -> None:
    await message.answer('Введите временной промежуток в формате "ДД.ММ.ГГГГ-ДД.ММ.ГГГГ"')

    await model.change_state(message.from_user.id, 4)


async def mean_earn(message: Message) -> None:
    m = message.text
    user_id = message.from_user.id
    if len(m) != 21:
        await remaining(message)
        return

    try:
        ts1 = datetime.datetime.strptime(m[:10], '%d.%m.%Y')
        ts2 = datetime.datetime.strptime(m[11:], '%d.%m.%Y')
        ts2 = ts2.replace(hour=23, minute=59, second=59)
        await message.answer(f"Средний дневной доход за период {message.text}: "
                             f"{await model.mean(ts1, ts2, user_id, 1):.2f}")
    except Exception:
        await remaining(message)

    finally:
        await model.change_state(message.from_user.id, 0)


async def mean_spend(message: Message) -> None:
    m = message.text
    user_id = message.from_user.id
    if len(m) != 21:
        await remaining(message)
        return

    try:
        ts1 = datetime.datetime.strptime(m[:10], '%d.%m.%Y')
        ts2 = datetime.datetime.strptime(m[11:], '%d.%m.%Y')
        ts2 = ts2.replace(hour=23, minute=59, second=59)
        await message.answer(f"Средний дневной расход за период {message.text}: "
                             f"{await model.mean(ts1, ts2, user_id, -1):.2f}")
    except Exception:
        await remaining(message)

    finally:
        await model.change_state(message.from_user.id, 0)


@dp.message()
async def not_a_command_handler(message: Message) -> None:
    user_state = await model.get_state(message.from_user.id)
    if message.text.isdigit() and user_state == 1:
        await earn(message)
    if message.text.isdigit() and user_state == 2:
        await spend(message)
    if user_state == 3:
        await mean_earn(message)
    if user_state == 4:
        await mean_spend(message)


async def remaining(message: Message) -> None:
    await message.answer("Неизвестная команда. Воспользуйтесь одной из представленных ниже в правильном формате")
    await model.change_state(message.from_user.id, 0)


async def main() -> None:
    await model.init_models()
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.startup.register(setup_bot_commands)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
