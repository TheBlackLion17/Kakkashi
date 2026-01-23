import re
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import CHANNELS, MOVIE_UPDATE_CHANNEL, FILE_BOT_USERNAME
from Script import script
from database.posted_db import get_series, add_or_update_series, mark_series_sent

BATCH_DELAY = 3  # seconds before sending combined series filter


def extract_title_and_quality(filename: str):
    """
    Extract clean title, detect series info, episode code, and quality
    """
    filename = re.sub(r"\.[^.]+$", "", filename)  # Remove extension

    # Detect quality (720p, 1080p, 2160P)
    quality_matches = re.findall(r"\b(720p|1080p|2160P)\b", filename, flags=re.I)
    quality_text = " ".join(sorted(set(quality_matches))) if quality_matches else "Unknown"

    # Clean filename
    filename_clean = re.sub(
        r"\b(HDR10Plus|DV|DVDRip|AAC|6CH|WEBRip|BluRay|x264|x265|\[.*?\]|720p|1080p|2160P|Hevc)\b",
        "",
        filename,
        flags=re.I
    )
    filename_clean = re.sub(r"[._\-]", " ", filename_clean)
    filename_clean = re.sub(r"\s+", " ", filename_clean)
    cleaned = filename_clean.strip()

    # Detect series episode
    series_match = re.search(r"(S\d{2}E\d{2})", cleaned, flags=re.I)
    is_series = bool(series_match)

    # Series name without episode code
    series_name = cleaned
    episode_code = None
    if series_match:
        episode_code = series_match.group(1)
        series_name = cleaned.replace(episode_code, "").strip()

    return cleaned.title(), is_series, episode_code, series_name.title(), quality_text


def create_payload(title, episode_codes=None):
    """Create payload for file bot"""
    keywords = [title]
    if episode_codes:
        keywords.extend(sorted(episode_codes))
    payload = "_".join(keywords).replace(" ", "_")
    return payload


async def send_series_filter(client, series_name, episodes, quality):
    """Send a combined filter message for a series"""
    if len(episodes) == 1:
        episode_text = episodes[0]
    else:
        episode_text = f"{episodes[0]} → {episodes[-1]}"

    payload = create_payload(series_name, episodes)

    caption = (
        f"✅ {series_name}\n\n"
        f"🎙 Japanese\n\n"
        f"📺 Episodes: {episode_text}\n"
        f"⚡ Quality: {quality}"
    )

    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            "⬇️ DOWNLOAD",
            url=f"https://t.me/{FILE_BOT_USERNAME}?start={payload}"
        )]]
    )

    await client.send_message(
        chat_id=MOVIE_UPDATE_CHANNEL,
        text=caption,
        reply_markup=buttons,
        disable_web_page_preview=True
    )

    print(f"✅ Sent combined filter: {series_name} -> {episode_text}")

    # Mark series as sent in DB
    await mark_series_sent(series_name, datetime.utcnow().date())


@Client.on_message(
    filters.chat(CHANNELS) &
    (filters.document | filters.video)
)
async def auto_movie_post(client, message):
    media = message.document or message.video
    if not media or not media.file_name:
        return

    # Extract title, series info, episode code, and quality
    title, is_series, episode_code, series_name, quality = extract_title_and_quality(media.file_name)
    today = datetime.utcnow().date()

    if is_series:
        # Fetch series info from DB
        series_data = await get_series(series_name, today)

        episodes = {episode_code}
        if series_data:
            episodes.update(series_data.get("episodes", []))
            await add_or_update_series(series_name, list(episodes), quality, today)
        else:
            await add_or_update_series(series_name, list(episodes), quality, today)

        # Schedule sending after BATCH_DELAY
        async def delayed_send():
            await asyncio.sleep(BATCH_DELAY)
            latest = await get_series(series_name, today)
            if latest and not latest.get("sent", False):
                await send_series_filter(client, series_name, latest["episodes"], latest["quality"])

        asyncio.create_task(delayed_send())

    else:
        # Single movie
        payload = create_payload(title)
        caption = (
            f"✅ {title}\n\n"
            f"🎙 Japanese\n\n"
            f"⚡ Quality: {quality}"
        )
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(
                "⬇️ DOWNLOAD",
                url=f"https://t.me/{FILE_BOT_USERNAME}?start={payload}"
            )]]
        )
        await client.send_message(
            chat_id=MOVIE_UPDATE_CHANNEL,
            text=caption,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
        print(f"✅ Sent filter link: {title}")        text=caption,
        reply_markup=buttons,
        disable_web_page_preview=True
    

    print(f"✅ Sent combined filter: {series_name} -> {episode_text}")

    # Mark series as sent in DB
    await mark_series_sent(series_name, datetime.utcnow().date())


@Client.on_message(
    filters.chat(CHANNELS) &
    (filters.document | filters.video)
)
async def auto_movie_post(client, message):
    media = message.document or message.video
    if not media or not media.file_name:
        return

    # Extract title, series info, episode code, and quality
    title, is_series, episode_code, series_name, quality = extract_title_and_quality(media.file_name)
    today = datetime.utcnow().date()

    if is_series:
        # Fetch series info from DB
        series_data = await get_series(series_name, today)

        episodes = {episode_code}
        if series_data:
            episodes.update(series_data.get("episodes", []))
            await add_or_update_series(series_name, list(episodes), quality, today)
        else:
            await add_or_update_series(series_name, list(episodes), quality, today)

        # Schedule sending after BATCH_DELAY seconds
        async def delayed_send():
            await asyncio.sleep(BATCH_DELAY)
            latest = await get_series(series_name, today)
            if latest and not latest.get("sent", False):
                await send_series_filter(client, series_name, latest["episodes"], latest["quality"])

        asyncio.create_task(delayed_send())

    else:
        # Single movie
        payload = create_payload(title)
        caption = (
            f"✅ {title}\n\n"
            f"🎙 Japanese\n\n"
            f"⚡ Quality: {quality}"
        )
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(
                "⬇️ DOWNLOAD",
                url=f"https://t.me/{FILE_BOT_USERNAME}?start={payload}"
            )]]
        )
        await client.send_message(
            chat_id=MOVIE_UPDATE_CHANNEL,
            text=caption,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
        print(f"✅ Sent filter link: {title}")    return cleaned.title(), is_series, series_match.group(1) if series_match else None, series_name.title()


def create_payload(title, episode_codes=None):
    """Create payload for file bot"""
    keywords = [title]
    if episode_codes:
        keywords.extend(sorted(episode_codes))
    payload = "_".join(keywords).replace(" ", "_")
    return payload


async def send_series_filter(client, series_name):
    """Send combined filter message for series"""
    data = series_batch.pop(series_name, None)
    if not data:
        return

    episodes = sorted(list(data["episodes"]))
    if len(episodes) == 1:
        episode_text = episodes[0]
    else:
        episode_text = f"{episodes[0]} → {episodes[-1]}"

    payload = create_payload(series_name, episodes)

    # Enhanced caption
    caption = (
        f"🎬 {series_name}\n"
        f"📺 Episodes: {episode_text}\n"
        f"⚡ Quality: 2160P Hevc"
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

    print(f"✅ Sent combined filter: {series_name} -> {episode_text}")


@Client.on_message(
    filters.chat(CHANNELS) &
    (filters.document | filters.video)
)
async def auto_movie_post(client, message):
    media = message.document or message.video
    if not media or not media.file_name:
        return

    title, is_series, episode_code, series_name = extract_title(media.file_name)

    if is_series:
        if series_name not in series_batch:
            series_batch[series_name] = {"episodes": set()}

        series_batch[series_name]["episodes"].add(episode_code)

        # Cancel previous task if exists
        task = series_batch[series_name].get("task")
        if task and not task.done():
            task.cancel()

        # Schedule sending after BATCH_DELAY seconds
        async def delayed_send(s_name):
            await asyncio.sleep(BATCH_DELAY)
            await send_series_filter(client, s_name)

        series_batch[series_name]["task"] = asyncio.create_task(delayed_send(series_name))

    else:
        # Single movie
        payload = create_payload(title)
        caption = (
            f"🎬 {title}\n"
            f"⚡ Quality: 2160P Hevc"
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
