import aiosqlite
import os

DB_PATH = "perspicua_cache.sqlite3"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Main Metadata & Vector Table
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
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Full-Text Search (FTS5) Table for Keyword Matching
        await db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS books_fts 
            USING fts5(title_slug UNINDEXED, title, author, description);
        """)

        # Persistent Scan History Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                preferences TEXT,
                recommendations TEXT
            )
        """)
        await db.commit()

def generate_slug(title, author):
    return f"{str(title).lower().strip()}|{str(author).lower().strip()}"

async def get_cached_book(title, author):
    slug = generate_slug(title, author)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM books_cache WHERE title_slug = ?", (slug,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def save_to_cache(title, author, metadata):
    if not metadata: return
    slug = generate_slug(title, author)
    async with aiosqlite.connect(DB_PATH) as db:
        # Insert into main table
        await db.execute("""
            INSERT OR REPLACE INTO books_cache 
            (title_slug, title, author, rating, description, link, image, source, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, (SELECT embedding FROM books_cache WHERE title_slug = ?))
        """, (
            slug, title, author, metadata.get("rating", "N/A"),
            metadata.get("desc", ""), metadata.get("link", "#"),
            metadata.get("image", ""), metadata.get("source", "Unknown"),
            slug
        ))
        # Sync to Keyword Index (FTS5)
        await db.execute("""
            INSERT OR REPLACE INTO books_fts (title_slug, title, author, description)
            VALUES (?, ?, ?, ?)
        """, (slug, title, author, metadata.get("desc", "")))
        await db.commit()

async def update_book_embedding(title_slug, embedding_bytes):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE books_cache SET embedding = ? WHERE title_slug = ?",
            (embedding_bytes, title_slug)
        )
        await db.commit()

async def save_scan_history(preferences, recommendations):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO scan_history (preferences, recommendations) VALUES (?, ?)",
            (preferences, recommendations)
        )
        await db.commit()

async def get_history(limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT timestamp, preferences, recommendations FROM scan_history ORDER BY timestamp DESC LIMIT ?", 
            (limit,)
        ) as cursor:
            return await cursor.fetchall()