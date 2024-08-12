import asyncio
import datetime
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

import model

TOKEN = '7209983319:AAHzHb9zJQq9ZrRBSFDfueLFEpi7K17xxbY'
dp = Dispatcher()


@dp.message(Command("start"))
async def command_spend_handler(message: Message) -> None:
    user_id = message.from_user.id
    ts = datetime.datetime.now()
    await model.create_user(user_id, 0)


@dp.message(Command("earn"))
async def command_spend_handler(message: Message, command: CommandObject) -> None:
    value = int(command.args)
    user_id = message.from_user.id
    ts = datetime.datetime.now()
    await model.create_delta(user_id, ts, value)

    await model.change_balance(user_id, value)

    await message.answer(f"Your balance changed by {value}")


@dp.message(Command("spend"))
async def command_spend_handler(message: Message, command: CommandObject) -> None:
    value = int(command.args)
    user_id = message.from_user.id
    ts = datetime.datetime.now()
    await model.create_delta(user_id, ts, -value)

    await model.change_balance(user_id, -value)

    await message.answer(f"Your balance changed by {-value}")


async def main() -> None:
    await model.init_models()
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
