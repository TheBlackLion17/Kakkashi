# plugins/commands.py

import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import PICS
from Script import *


@Client.on_message(filters.private & filters.command("start"))
async def start_cmd(client, message):

    pic = random.choice(PICS) if PICS else None

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎥 Movies", callback_data="movies"),
                InlineKeyboardButton("ℹ️ Help", callback_data="help")
            ],
            [
                InlineKeyboardButton("📢 Updates", url="https://t.me/YourChannel")
            ]
        ]
    )

    if pic:
        await message.reply_photo(
            photo=pic,
            caption=START_TEXT.format(
                mention=message.from_user.mention
            ),
            reply_markup=buttons
        )
    else:
        await message.reply_text(
            text=START_TEXT.format(
                mention=message.from_user.mention
            ),
            reply_markup=buttons
        )
