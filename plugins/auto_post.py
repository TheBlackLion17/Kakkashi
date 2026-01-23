import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date

from info import CHANNELS, MOVIE_UPDATE_CHANNEL, FILE_BOT_USERNAME
from Script import script
from database.posted_db import is_posted, mark_posted

def extract_title(filename: str):
    """Clean file name for caption and filter payload"""
    filename = re.sub(r"\.[^.]+$", "", filename)
    filename = re.sub(
        r"\b(HDR10Plus|DV|DVDRip|AAC|6CH|WEBRip|BluRay|x264|x265|\[.*?\])\b",
        "",
        filename,
        flags=re.I
    )
    filename = re.sub(r"[._\-]", " ", filename)
    filename = re.sub(r"\s+", " ", filename)
    cleaned = filename.strip()

    # Detect series episode
    series_match = re.search(r"(S\d{2}E\d{2})", cleaned, flags=re.I)
    is_series = bool(series_match)

    # Series name without episode code
    series_name = cleaned
    if series_match:
        series_name = cleaned.replace(series_match.group(1), "").strip()

    return cleaned.title(), is_series, series_match.group(1) if series_match else None, series_name.title()


def create_payload(title, episode_code=None):
    keywords = [title]
    if episode_code:
        keywords.append(episode_code)
    payload = "_".join(keywords).replace(" ", "_")
    return payload


@Client.on_message(
    filters.chat(CHANNELS) &
    (filters.document | filters.video)
)
async def auto_movie_post(client, message):
    media = message.document or message.video
    if not media or not media.file_name:
        return

    title, is_series, episode_code, series_name = extract_title(media.file_name)

    # 🔹 Check for duplicates
    if is_series:
        # Only one filter per series per day
        if await is_posted(series_name, series_only=True):
            print(f"⚠ Skipped series duplicate today: {series_name}")
            return
    else:
        # Movie duplicate check
        if await is_posted(title):
            print(f"⚠ Skipped duplicate movie: {title}")
            return

    # Create payload for file bot
    payload = create_payload(title, episode_code)

    # Caption
    caption = script.AUTO_POST_TXT.format(
        title=title,
        type="Series" if is_series else "Movie",
        quality="HDRip"
    )

    # Inline button
    buttons = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "⬇️ DOWNLOAD",
                url=f"https://t.me/{FILE_BOT_USERNAME}?start={payload}"
            )
        ]]
    )

    # Send message
    await client.send_message(
        chat_id=MOVIE_UPDATE_CHANNEL,
        text=caption,
        reply_markup=buttons,
        disable_web_page_preview=True
    )

    # Mark posted
    if is_series:
        await mark_posted(title, series_title=series_name)
    else:
        await mark_posted(title)

    print(f"✅ Sent filter link: {title}")
