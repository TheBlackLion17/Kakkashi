import sys
import glob
import importlib.util
from pathlib import Path
import logging
import logging.config
import asyncio
import time
from datetime import date, datetime
import pytz
from aiohttp import web

from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer

from database.ia_filterdb import Media, Media2, choose_mediaDB, tempDict, db as clientDB
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from plugins import web_server, check_expired_premium

# ---------------- LOGGING ---------------- #
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

botStartTime = time.time()

# ---------------- BOT CLIENT ---------------- #
Bot = Client(
    name=SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=WORKERS,
    plugins=dict(root="plugins")
)

# ---------------- STARTUP ---------------- #
async def start_bot():
    logging.info("🚀 Starting Bot...")

    await Bot.start()
    me = await Bot.get_me()

    # -------- Load Plugins Manually (Optional Safety) -------- #
    for file in Path("plugins").glob("*.py"):
        plugin_name = file.stem
        try:
            spec = importlib.util.spec_from_file_location(f"plugins.{plugin_name}", file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[f"plugins.{plugin_name}"] = module
            logging.info(f"✅ Plugin loaded: {plugin_name}")
        except Exception as e:
            logging.error(f"❌ Plugin failed: {plugin_name} | {e}")

    # -------- Banned Users / Chats -------- #
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats

    # -------- DB Index -------- #
    await Media.ensure_indexes()
    await Media2.ensure_indexes()

    stats = await clientDB.command("dbStats")
    used_mb = (stats["dataSize"] + stats["indexSize"]) / (1024 * 1024)
    free_mb = round(512 - used_mb, 2)

    if DATABASE_URI2 and free_mb < 62:
        tempDict["indexDB"] = DATABASE_URI2
        logging.warning(f"⚠️ Primary DB low ({free_mb}MB). Using Secondary DB.")
    else:
        logging.info(f"✅ Primary DB OK ({free_mb}MB free).")

    await choose_mediaDB()

    # -------- BOT META -------- #
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention

    logging.info(
        f"{me.first_name} started | Pyrogram v{__version__} | Layer {layer}"
    )

    logging.info(LOG_STR)
    logging.info(script.LOGO)

    # -------- Restart Log -------- #
    await Bot.send_message(
        chat_id=LOG_CHANNEL,
        text=script.RESTART_TXT
    )

    # -------- Premium Expiry Task -------- #
    asyncio.create_task(check_expired_premium(Bot))

    # -------- Web Server -------- #
    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", PORT).start()

    logging.info("🌐 Web server running")

    await idle()

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logging.info("🛑 Bot stopped manually")
