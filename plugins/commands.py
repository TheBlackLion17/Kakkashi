import random
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import pytz
from Script import script
from database.users_chats_db import db
from utils import temp
from info import *

@Client.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user

    if EMOJI_MODE and user:
        await message.react(emoji=random.choice(REACTIONS), big=True)

    # ================= GROUP START =================
    if message.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
        buttons = [
            [
                InlineKeyboardButton(
                    "• ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴜʀ ᴄʜᴀᴛ •",
                    url=f"http://t.me/{temp.U_NAME}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton("• ᴍᴀsᴛᴇʀ •", url="https://t.me/AgsModsOG"),
                InlineKeyboardButton("• sᴜᴘᴘᴏʀᴛ •", url="https://t.me/AgsModsOG")
            ],
            [
                InlineKeyboardButton(
                    "• ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ •",
                    url="https://t.me/AgsModsOG"
                )
            ]
        ]

        await message.reply(
            script.GSTART_TXT.format(
                user.mention if user else message.chat.title,
                temp.U_NAME,
                temp.B_NAME
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

        await asyncio.sleep(2)

        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_G.format(
                    message.chat.title,
                    message.chat.id,
                    total,
                    "Unknown"
                )
            )
            await db.add_chat(message.chat.id, message.chat.title)
        return

    # ================= PRIVATE START =================
    if user and not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            script.LOG_TEXT_P.format(user.id, user.mention)
        )

    if len(message.command) != 2:
        buttons = [
            [
                InlineKeyboardButton(
                    "ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                    url=f"http://t.me/{temp.U_NAME}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton("• ᴏᴛᴛ ᴜᴘᴅᴀᴛᴇ •", url="https://t.me/+RDsxY-lQ55wwOWI1"),
                InlineKeyboardButton("• ʙᴏᴛ ᴜᴘᴅᴀᴛᴇ •", url="https://t.me/AgsModsOG")
            ],
            [
                InlineKeyboardButton("• ᴍᴏᴠɪᴇ ᴄʜᴀɴɴᴇʟ •", url="https://t.me/+RDsxY-lQ55wwOWI1")
            ]
        ]

        now = datetime.now(pytz.timezone(TIMEZONE)).hour
        if now < 12:
            gtxt = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 👋"
        elif now < 17:
            gtxt = "ɢᴏᴏᴅ ᴀғᴛᴇʀɴᴏᴏɴ 👋"
        elif now < 21:
            gtxt = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 👋"
        else:
            gtxt = "ɢᴏᴏᴅ ɴɪɢʜᴛ 👋"

        m = await message.reply_text(
            "<i>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>ʟᴜᴄʏ</b>.\nʜᴏᴘᴇ ʏᴏᴜ'ʀᴇ ᴅᴏɪɴɢ ᴡᴇʟʟ...</i>"
        )

        await asyncio.sleep(0.4)
        for txt in ("⏳", "👀", "<b><i>ꜱᴛᴀʀᴛɪɴɢ...</i></b>"):
            await m.edit_text(txt)
            await asyncio.sleep(0.4)

        await m.delete()

        s = await message.reply_sticker(
            "CAACAgUAAxkBAAJFeWd037UWP-vgb_dWo55DCPZS9zJzAAJpEgACqXaJVxBrhzahNnwSHgQ"
        )
        await asyncio.sleep(1)
        await s.delete()

        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(
                user.mention if user else "User",
                gtxt,
                temp.U_NAME,
                temp.B_NAME
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
