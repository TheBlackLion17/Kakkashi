from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI
from datetime import datetime

# MongoDB client
mongo = AsyncIOMotorClient(DATABASE_URI)
db = mongo["autofilter_bot"]
series_collection = db["series_filters"]


async def get_series(series_name: str, date: datetime.date):
    """Get series info for a specific date"""
    return await series_collection.find_one({"series_name": series_name, "date": date})


async def add_or_update_series(series_name: str, episodes: list, quality: str, date: datetime.date):
    """Add new series or update episodes for today"""
    await series_collection.update_one(
        {"series_name": series_name, "date": date},
        {"$set": {"episodes": episodes, "quality": quality, "sent": False}},
        upsert=True
    )


async def mark_series_sent(series_name: str, date: datetime.date):
    """Mark series as sent today"""
    await series_collection.update_one(
        {"series_name": series_name, "date": date},
        {"$set": {"sent": True}},
        upsert=True
    )
