import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import PICS
from Script import script   # ✅ IMPORT CLASS


print("✅ commands.py loaded")


@Client.on_message(filters.private & filters.command("start"))
async def start_cmd(client, message):

    user = message.from_user
    pic = random.choice(PICS) if PICS else None

    text = script.START_TXT.format(
        user.first_name,
        user.mention
    )

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
            [InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{client.me.username}?startgroup=true")]
        ]
    )

    if pic:
        await message.reply_photo(
            photo=pic,
            caption=text,
            reply_markup=buttons
        )
    else:
        await message.reply_text(
            text=text,
            reply_markup=buttons
        )



@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client, query):
    await query.answer()

    pic = random.choice(PICS)

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⬅ Back", callback_data="start")]
        ]
    )

    await query.message.edit_media(
        media=InputMediaPhoto(
            media=pic,
            caption=script.HELP_TXT,
            parse_mode="html"
        ),
        reply_markup=buttons
    )
