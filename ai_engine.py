# ---------------------------------------------------------
# Perspicua AI Engine - Semantic Brain & Telemetry
# Developed by: Isa Maharramov
# License: GNU GPLv3 (Open-Source / Non-Commercial)
# Copyright (c) 2026 Isa Maharramov
# ---------------------------------------------------------

import base64
import os
import json
import asyncio
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from books_api import get_all_book_metadata
from database import init_db, update_book_embedding, generate_slug

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text):
    """Generates a 1536-dimensional vector using OpenAI's latest model."""
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def encode_image(image_path):
    """Encodes a local image file to base64 for vision processing."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_books(image_path):
    """Uses GPT-4o Vision to extract raw titles/authors from stylized spines."""
    base64_image = encode_image(image_path)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a high-precision library digitization robot. Scan the shelf exhaustively. Return strictly a JSON object with 'books'."},
            {"role": "user", "content": [
                {"type": "text", "text": "Extract title and author for every book."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}}
            ]}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content).get("books", [])

async def get_recommendations(book_list, user_prefs, status_cb=None):
    """
    Performs Chain of Verification & Semantic Search with live telemetry.
    """
    def log(msg):
        if status_cb: status_cb(msg)

    log("🔍 Initializing Semantic Brain & Database...")
    await init_db()
    
    log(f"⚡ Fetching metadata for {len(book_list)} items...")
    all_metadata = await get_all_book_metadata(book_list)
    
    # Calculate cache stats for telemetry
    cache_hits = sum(1 for b in all_metadata if b and b.get('source') == 'Cache')
    log(f"🧠 Memory Layer: {cache_hits} hits, {len(book_list)-cache_hits} new lookups.")

    log("🧬 Vectorizing user preferences...")
    query_vector = np.array(get_embedding(user_prefs))
    
    scored_books = []
    log("🧮 Calculating Cosine Similarity in 1536-D space...")
    
    for book in all_metadata:
        if not book or not book.get('description'): continue
        
        embedding_data = book.get('embedding')
        if not embedding_data:
            # Generate new embedding if missing in cache
            combined_text = f"{book['title']} {book['description']}"
            vector = get_embedding(combined_text)
            vector_np = np.array(vector, dtype=np.float32)
            
            # Update cache with the new vector
            slug = generate_slug(book['title'], book['author'])
            await update_book_embedding(slug, vector_np.tobytes())
            book_vector = vector_np
        else:
            # Load vector from binary blob
            book_vector = np.frombuffer(embedding_data, dtype=np.float32)

        # Mathematical similarity score
        score = np.dot(query_vector, book_vector)
        scored_books.append((score, book))

    # Sort and take top matches
    scored_books.sort(key=lambda x: x[0], reverse=True)
    top_matches = [b for score, b in scored_books[:5]]

    log(f"✨ Found {len(top_matches)} semantic matches. Starting reasoning...")
    
    prompt = f"""
    USER PREF: {user_prefs}
    TOP SEMANTIC MATCHES: {json.dumps(top_matches, indent=2)}
    
    TASK: Using the 'description' and 'rating', explain why these matches are perfect.
    Be witty and professional. Fix any minor OCR typos found in titles.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Perspicua. You provide deep reasoning for semantic book matches."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Remove binary embeddings before sending to UI to keep it lightweight
    for b in all_metadata:
        if b and 'embedding' in b: b.pop('embedding')

    log("✅ Analysis complete. Rendering results.")
    return response.choices[0].message.content, all_metadata