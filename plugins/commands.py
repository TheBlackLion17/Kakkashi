import random
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from Script import script as Txt
from info import PICS

print("✅ commands.py loaded")


# ===================== /START COMMAND =====================
@Client.on_message(filters.private & filters.command("start"))
async def start_cmd(client, message):
    user = message.from_user
    pic = random.choice(PICS) if PICS else None

    text = Txt.START_TXT.format(
        user.first_name,
        user.mention
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴍʏ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs •", callback_data="help")],
        [
            InlineKeyboardButton("• ᴜᴘᴅᴀᴛᴇs", url="https://t.me/Movies_Hub_OG"),
            InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ •", url="https://t.me/AgsModsOG")
        ],
        [
            InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
            InlineKeyboardButton("sᴏᴜʀᴄᴇ •", callback_data="source")
        ]
    ])

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


# ===================== CALLBACK HANDLER =====================
@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data
    user = query.from_user

    print(f"Callback data received: {data}")  # debug

    # 🏠 HOME
    if data == "home":
        await query.message.edit_text(
            text=Txt.START_TXT.format(user.first_name, user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ᴍʏ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs •", callback_data="help")],
                [
                    InlineKeyboardButton("• ᴜᴘᴅᴀᴛᴇs", url="https://t.me/Movies_Hub_OG"),
                    InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ •", url="https://t.me/AgsModsOG")
                ],
                [
                    InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton("sᴏᴜʀᴄᴇ •", callback_data="source")
                ]
            ])
        )

    # 📖 HELP
    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="home")]
            ])
        )

    # ℹ️ ABOUT
    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="home")]
            ])
        )

    # 🧑‍💻 SOURCE
    elif data == "source":
        await query.message.edit_text(
            text=Txt.SOURCE_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="home")]
            ])
        )

    else:
        await query.answer("Unknown button!", show_alert=True)


