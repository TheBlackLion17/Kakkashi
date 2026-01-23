import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import CHANNELS, MOVIE_UPDATE_CHANNEL, FILE_BOT_USERNAME
from Script import script   # ✅ IMPORT CLASS


def extract_title(filename: str) -> str:
    filename = re.sub(r"\.[^.]+$", "", filename)
    filename = re.sub(
        r"\b(480p|720p|1080p|2160p|HDRIP|WEBRip|x264|x265|BluRay|HEVC)\b",
        "",
        filename,
        flags=re.I
    )
    filename = re.sub(r"[._\-]", " ", filename)
    filename = re.sub(r"\s+", " ", filename)
    return filename.strip().title()


@Client.on_message(
    filters.chat(CHANNELS) &
    (filters.document | filters.video)
)
async def auto_movie_post(client, message):

    media = message.document or message.video
    if not media or not media.file_name:
        return

    title = extract_title(media.file_name)

    caption = script.AUTO_POST_TXT.format(
        title=title,
        type="Movie / Series",
        quality="HDRip"
    )

    buttons = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "⬇️ DOWNLOAD",
                url=f"https://t.me/{FILE_BOT_USERNAME}?start={media.file_unique_id}"
            )
        ]]
    )

    await client.send_message(
        chat_id=MOVIE_UPDATE_CHANNEL,
        text=caption,
        reply_markup=buttons,
        disable_web_page_preview=True
    )

    print(f"✅ Auto posted: {title}")
