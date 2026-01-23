from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI

mongo = AsyncIOMotorClient(DATABASE_URI)
db = mongo["auto_post"]
posted_collection = db["posted_titles"]

async def is_posted(title: str) -> bool:
    """Check if title was already posted"""
    result = await posted_collection.find_one({"title": title})
    return bool(result)

async def mark_posted(title: str):
    """Mark title as posted"""
    await posted_collection.update_one(
        {"title": title},
        {"$set": {"title": title}},
        upsert=True
    )
