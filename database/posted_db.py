from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI
from datetime import date

mongo = AsyncIOMotorClient(DATABASE_URI)
db = mongo["auto_post"]
posted_collection = db["posted_titles"]

async def is_posted(title: str, series_only=False) -> bool:
    """Check if title or series already posted today"""
    today_str = str(date.today())
    query = {"title": title, "date": today_str}
    if series_only:
        # Series filter ignores episode number
        query = {"series_title": title, "date": today_str}
    result = await posted_collection.find_one(query)
    return bool(result)

async def mark_posted(title: str, series_title=None):
    """Mark title or series as posted today"""
    today_str = str(date.today())
    data = {"date": today_str, "title": title}
    if series_title:
        data["series_title"] = series_title
    await posted_collection.update_one(
        {"title": title, "date": today_str},
        {"$set": data},
        upsert=True
    )
