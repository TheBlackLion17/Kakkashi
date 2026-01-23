# commands.py

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import PICS
from Script import *


@Client.on_message(filters.private & filters.command("start"))
async def start_cmd(client, message):
    
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

    await message.reply_photo(
        photo=PICS,
        caption=START_TEXT.format(
            mention=message.from_user.mention
        ),
        reply_markup=buttons
    )


