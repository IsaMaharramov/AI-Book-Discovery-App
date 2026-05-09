# ---------------------------------------------------------
# Perspicua AI Engine - Enhanced Metadata Orchestrator
# Developed by: Isa Maharramov
# License: GNU GPLv3
# Copyright (c) 2026 Isa Maharramov
# ---------------------------------------------------------

import httpx
import asyncio
import logging
from database import get_cached_book, save_to_cache, init_db

# Configure logging to monitor cache hits vs network misses
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_with_retry(client, url, retries=3, backoff_factor=2):
    """Handles API calls with Exponential Backoff for HTTP 429 errors."""
    for i in range(retries):
        try:
            resp = await client.get(url, timeout=10)
            
            if resp.status_code == 429:
                wait_time = backoff_factor ** i
                logger.warning(f"Rate limited (429). Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
                
            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if i == retries - 1:
                logger.error(f"API Request failed after {retries} attempts: {e}")
                return None
            await asyncio.sleep(backoff_factor ** i)
    return None

async def fetch_google_books(client, title, author):
    """Retrieves metadata from Google Books API."""
    query = f"intitle:{title} inauthor:{author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
    
    data = await fetch_with_retry(client, url)
    if data and "items" in data:
        item = data["items"][0]["volumeInfo"]
        return {
            "title": item.get("title", title),
            "author": ", ".join(item.get("authors", ["Unknown Author"])),
            "rating": item.get("averageRating", "N/A"),
            "desc": item.get("description", "No description available.")[:250],
            "link": item.get("infoLink", "#"),
            "image": item.get("imageLinks", {}).get("thumbnail", ""),
            "source": "Google"
        }
    return None

async def fetch_open_library(client, title):
    """Retrieves metadata from Open Library API as a fallback."""
    url = f"https://openlibrary.org/search.json?title={title}&limit=1"
    data = await fetch_with_retry(client, url)
    if data and data.get("docs"):
        doc = data["docs"][0]
        return {
            "title": doc.get("title", title),
            "author": ", ".join(doc.get("author_name", ["Unknown Author"])),
            "rating": doc.get("ratings_average", "N/A"),
            "desc": "Subjects: " + ", ".join(doc.get("subject", []))[:200],
            "link": f"https://openlibrary.org{doc.get('key', '')}",
            "image": f"https://covers.openlibrary.org/b/id/{doc.get('cover_i')}-M.jpg" if doc.get('cover_i') else "",
            "source": "OpenLibrary"
        }
    return None

async def get_book_metadata(client, title, author):
    """Orchestrates the Cache-Aside pattern for metadata retrieval."""
    # 1. Check Memory Layer first
    cached_data = await get_cached_book(title, author)
    if cached_data:
        logger.info(f"Cache HIT: {title}")
        return cached_data

    logger.info(f"Cache MISS: {title}. Fetching from APIs...")

    # 2. If Miss: Fetch from Google Books
    data = await fetch_google_books(client, title, author)
    
    # 3. Fallback to Open Library if description is missing
    if not data or data.get("desc") == "No description available.":
        ol_data = await fetch_open_library(client, title)
        if ol_data:
            if data:
                data.update({"desc": ol_data["desc"], "source": "Google+OpenLibrary"})
            else:
                data = ol_data

    # 4. Save to Memory Layer for future requests
    if data:
        # Ensure we use the detected title/author if the vision model had a typo
        await save_to_cache(title, author, data)
        
    return data

async def get_all_book_metadata(book_list):
    """Initializes DB and gathers metadata for the entire shelf inventory."""
    await init_db() # Ensure the SQLite table exists
    async with httpx.AsyncClient() as client:
        tasks = [get_book_metadata(client, b['title'], b.get('author', '')) for b in book_list]
        return await asyncio.gather(*tasks)