import base64
import os
import json
import asyncio
import numpy as np
import aiosqlite
from openai import OpenAI
from dotenv import load_dotenv
from books_api import get_all_book_metadata
from database import init_db, update_book_embedding, generate_slug, save_scan_history, DB_PATH

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_books(image_path):
    base64_image = encode_image(image_path)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a library digitization robot. Scan the shelf. Return strictly JSON with 'books'."},
            {"role": "user", "content": [
                {"type": "text", "text": "Extract title and author for every book."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}}
            ]}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content).get("books", [])

async def get_recommendations(book_list, user_prefs, status_cb=None):
    def log(msg):
        if status_cb: status_cb(msg)

    log("🔍 Initializing Hybrid Brain...")
    await init_db()
    
    log(f"⚡ Syncing metadata for {len(book_list)} items...")
    all_metadata = await get_all_book_metadata(book_list)
    
    # KEYWORD SEARCH (FTS5)
    log("🛰️ Keyword Search: Scanning for exact matches...")
    keyword_ranked_slugs = []
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT title_slug FROM books_fts WHERE books_fts MATCH ? ORDER BY rank",
            (user_prefs,)
        ) as cursor:
            rows = await cursor.fetchall()
            keyword_ranked_slugs = [r[0] for r in rows]

    # VECTOR SEARCH (Cosine Similarity)
    log("🧬 Vectorizing preferences & calculating 1536-D similarity...")
    query_vector = np.array(get_embedding(user_prefs))
    vector_scores = []

    for book in all_metadata:
        if not book or not book.get('description'): continue
        
        slug = generate_slug(book['title'], book['author'])
        embedding_data = book.get('embedding')
        
        if not embedding_data:
            combined_text = f"{book['title']} {book['description']}"
            vector = np.array(get_embedding(combined_text), dtype=np.float32)
            await update_book_embedding(slug, vector.tobytes())
            book_vector = vector
        else:
            book_vector = np.frombuffer(embedding_data, dtype=np.float32)

        score = np.dot(query_vector, book_vector)
        vector_scores.append((slug, score))

    vector_scores.sort(key=lambda x: x[1], reverse=True)
    vector_ranked_slugs = [item[0] for item in vector_scores]

    # RECIPROCAL RANK FUSION (RRF)
    log("🔀 Fusing Semantic and Keyword results...")
    k = 60
    fused_scores = {}
    
    combined_slugs = set(keyword_ranked_slugs + vector_ranked_slugs)
    for slug in combined_slugs:
        score = 0.0
        if slug in keyword_ranked_slugs:
            score += 1.0 / (k + keyword_ranked_slugs.index(slug) + 1)
        if slug in vector_ranked_slugs:
            score += 1.0 / (k + vector_ranked_slugs.index(slug) + 1)
        fused_scores[slug] = score

    final_slugs = sorted(fused_scores, key=fused_scores.get, reverse=True)[:5]
    top_matches = [next(b for b in all_metadata if b and generate_slug(b['title'], b['author']) == s) for s in final_slugs]

    log(f"✨ Found {len(top_matches)} Hybrid matches. Starting reasoning...")
    
    prompt = f"USER PREF: {user_prefs}\nHYBRID MATCHES: {json.dumps(top_matches, indent=2)}\n\nExplain why these are perfect choices."
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Perspicua. Provide professional reasoning for hybrid book matches."},
            {"role": "user", "content": prompt}
        ]
    )
    
    final_reasoning = response.choices[0].message.content

    await save_scan_history(user_prefs, final_reasoning)

    clean_metadata = [b for b in all_metadata if b is not None]
    for b in clean_metadata:
        if 'embedding' in b: b.pop('embedding')

    log("✅ Analysis complete.")
    return final_reasoning, clean_metadata