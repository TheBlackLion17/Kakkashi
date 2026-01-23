import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import CHANNELS, MOVIE_UPDATE_CHANNEL, FILE_BOT_USERNAME
from Script import script  # Capital S as requested


def extract_title(filename: str):
    """Clean file name for caption and filter payload"""
    # Remove extension
    filename = re.sub(r"\.[^.]+$", "", filename)

    # Remove unwanted tags
    filename = re.sub(
        r"\b(HDR10Plus|DV|DVDRip|AAC|6CH|WEBRip|BluRay|x264|x265|\[.*?\])\b",
        "",
        filename,
        flags=re.I
    )

    # Replace dots/underscores/dashes with spaces
    filename = re.sub(r"[._\-]", " ", filename)
    filename = re.sub(r"\s+", " ", filename)
    cleaned = filename.strip()

    # Detect if it's a series episode
    series_match = re.search(r"(S\d{2}E\d{2})", cleaned, flags=re.I)
    is_series = bool(series_match)

    return cleaned.title(), is_series, series_match.group(1) if series_match else None


def create_payload(title, episode_code=None):
    """
    Encode payload for Telegram deep-link.
    Multiple keywords supported.
    """
    # Base keyword
    keywords = [title]

    # Add episode code as separate keyword if exists
    if episode_code:
        keywords.append(episode_code)

    # Encode for start payload (replace spaces with _)
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

    title, is_series, episode_code = extract_title(media.file_name)

    # Generate payload for FILE BOT
    payload = create_payload(title, episode_code)

    # Auto-caption
    caption = script.AUTO_POST_TXT.format(
        title=title,
        type="Series" if is_series else "Movie",
        quality="HDRip"
    )

    buttons = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "⬇️ DOWNLOAD",
                url=f"https://t.me/{FILE_BOT_USERNAME}?start={payload}"
            )
        ]]
    )

    await client.send_message(
        chat_id=MOVIE_UPDATE_CHANNEL,
        text=caption,
        reply_markup=buttons,
        disable_web_page_preview=True
    )

    print(f"✅ Sent filter link: {title}")
