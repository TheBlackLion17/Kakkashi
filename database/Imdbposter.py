import re
import aiohttp
import asyncio
import logging
from io import BytesIO
from PIL import Image
from imdb import Cinemagoer
from info import IMAGE_FETCH

logger = logging.getLogger(__name__)

ia = Cinemagoer()
LONG_IMDB_DESCRIPTION = False

# ---------- UTILS ---------- #
def list_to_str(lst, limit=None):
    if not lst:
        return ""
    if limit:
        lst = lst[:limit]
    return ", ".join(map(str, lst))


# ---------- IMAGE FETCH ---------- #
async def fetch_image(url, size=(720, 720), session: aiohttp.ClientSession = None):
    if not IMAGE_FETCH or not url:
        return None

    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
            if response.status != 200:
                logger.warning(f"Image fetch failed: {response.status}")
                return None

            content = await response.read()
            img = Image.open(BytesIO(content)).convert("RGB")
            img = img.resize(size, Image.LANCZOS)

            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG", quality=90)
            img_bytes.seek(0)
            return img_bytes

    except Exception as e:
        logger.error(f"fetch_image error: {e}")

    finally:
        if close_session:
            await session.close()

    return None


# ---------- IMDB CORE (BLOCKING → THREAD) ---------- #
def _imdb_lookup(query, year=None, by_id=False):
    if by_id:
        return ia.get_movie(query)

    results = ia.search_movie(query, results=10)
    if not results:
        return None

    if year:
        filtered = [m for m in results if str(m.get("year")) == str(year)]
        results = filtered or results

    results = [m for m in results if m.get("kind") in ("movie", "tv series")] or results
    return ia.get_movie(results[0].movieID)


# ---------- PUBLIC ASYNC API ---------- #
async def get_movie_details(query, id=False, file=None):
    try:
        loop = asyncio.get_running_loop()

        year = None
        if not id:
            year_match = re.findall(r"[1-2]\d{3}", query)
            if year_match:
                year = year_match[-1]
                query = re.sub(year, "", query).strip()
            elif file:
                file_year = re.findall(r"[1-2]\d{3}", file)
                if file_year:
                    year = file_year[-1]

        movie = await loop.run_in_executor(
            None,
            _imdb_lookup,
            query if not id else query,
            year,
            id
        )

        if not movie:
            return None

        plot = movie.get("plot") or movie.get("plot outline")
        if isinstance(plot, list):
            plot = plot[0]

        if plot and not LONG_IMDB_DESCRIPTION and len(plot) > 800:
            plot = plot[:800] + "..."

        release_date = (
            movie.get("original air date")
            or movie.get("year")
            or "N/A"
        )

        imdb_id = movie.get("imdbID")

        return {
            "title": movie.get("title"),
            "year": movie.get("year"),
            "kind": movie.get("kind"),
            "rating": str(movie.get("rating")),
            "votes": movie.get("votes"),
            "genres": list_to_str(movie.get("genres")),
            "countries": list_to_str(movie.get("countries")),
            "languages": list_to_str(movie.get("languages")),
            "runtime": list_to_str(movie.get("runtimes")),
            "director": list_to_str(movie.get("director")),
            "writer": list_to_str(movie.get("writer")),
            "cast": list_to_str(movie.get("cast"), limit=10),
            "poster_url": movie.get("full-size cover url"),
            "plot": plot,
            "release_date": release_date,
            "imdb_id": f"tt{imdb_id}" if imdb_id else None,
            "url": f"https://www.imdb.com/title/tt{imdb_id}" if imdb_id else None,
        }

    except Exception as e:
        logger.exception("get_movie_details failed")
        return None
