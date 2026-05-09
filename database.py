# ---------------------------------------------------------
# Perspicua AI Engine - Data Access Layer
# Developed by: Isa Maharramov
# License: GNU GPLv3
# Copyright (c) 2026 Isa Maharramov
# ---------------------------------------------------------

import aiosqlite
import json
import os

DB_PATH = "perspicua_cache.sqlite3"

async def init_db():
    """Initializes the SQLite database and creates the cache table."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS books_cache (
                title_slug TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                rating TEXT,
                description TEXT,
                link TEXT,
                image TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

def generate_slug(title, author):
    """Creates a unique key for lookup to avoid collisions."""
    return f"{str(title).lower().strip()}|{str(author).lower().strip()}"

async def get_cached_book(title, author):
    """Retrieves book metadata from the local cache if it exists."""
    slug = generate_slug(title, author)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM books_cache WHERE title_slug = ?", (slug,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
    return None

async def save_to_cache(title, author, metadata):
    """Saves newly retrieved API metadata to the local cache."""
    if not metadata:
        return
        
    slug = generate_slug(title, author)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO books_cache 
            (title_slug, title, author, rating, description, link, image, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            slug,
            title,
            author,
            metadata.get("rating", "N/A"),
            metadata.get("desc", ""),
            metadata.get("link", "#"),
            metadata.get("image", ""),
            metadata.get("source", "Unknown")
        ))
        await db.commit()