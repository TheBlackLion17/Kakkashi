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



@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    print(f"Callback data received: {data}")  # Debugging line

    if data == "home":
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ᴍʏ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs •", callback_data='help')],
                [InlineKeyboardButton('• ᴜᴘᴅᴀᴛᴇs', url='https://t.me/Codeflix_Bots'), InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ •', url='https://t.me/CodeflixSupport')],
                [InlineKeyboardButton('• ᴀʙᴏᴜᴛ', callback_data='about'), InlineKeyboardButton('sᴏᴜʀᴄᴇ •', callback_data='source')]
            ])
        )

    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT.format(client.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴛ •", callback_data='file_names')],
                [InlineKeyboardButton('• ᴛʜᴜᴍʙɴᴀɪʟ', callback_data='thumbnail'), InlineKeyboardButton('ᴄᴀᴘᴛɪᴏɴ •', callback_data='caption')],
                [InlineKeyboardButton('• ᴍᴇᴛᴀᴅᴀᴛᴀ', callback_data='meta'), InlineKeyboardButton('ᴅᴏɴᴀᴛᴇ •', callback_data='donate')],
                [InlineKeyboardButton('• ʜᴏᴍᴇ', callback_data='home')]
            ])
        )
     

