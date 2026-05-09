# ---------------------------------------------------------
# Perspicua AI Engine
# Developed by: Isa Maharramov
# License: GNU GPLv3 (Open-Source / Non-Commercial)
# Copyright (c) 2026 Isa Maharramov
# ---------------------------------------------------------

import base64
import os
import json
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
from books_api import get_all_book_metadata

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
            {
                "role": "system",
                "content": "You are a high-precision library digitization robot. Scan the shelf exhaustively (20-40 books). Return strictly a JSON object with a key 'books' containing a list of objects with 'title' and 'author'."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract every single book title and author from this image. Focus on vertical or stylized text on spines."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        response_format={"type": "json_object"}
    )
    result = json.loads(response.choices[0].message.content)
    return result.get("books", [])

async def get_recommendations(book_list, user_prefs):
    """
    Performs Chain of Verification (Self-Healing) by comparing 
    Vision data with API Ground Truth before recommending.
    """
    # 1. Fetch live metadata for the entire inventory
    all_metadata = await get_all_book_metadata(book_list)
    
    # 2. Build the Verification Prompt
    # This provides the LLM with both the 'noisy' image data and the 'clean' API data
    prompt = f"""
    USER PREFERENCES: {user_prefs}
    
    RAW VISION DATA (From Spines):
    {json.dumps(book_list, indent=2)}
    
    API METADATA (Verified Ground Truth):
    {json.dumps(all_metadata, indent=2)}
    
    INSTRUCTIONS:
    1. SELF-HEALING: Cross-reference 'Raw Vision Data' with 'API Metadata'. 
       - Correct OCR misreads (e.g., if vision saw "19B4" but API found "1984", use "1984").
       - Discard detections that failed to return valid book metadata.
    
    2. ANALYSIS: Evaluate the corrected inventory against the USER PREFERENCES.
    
    3. SELECTION: Recommend the top 3-5 best matches.
    
    4. OUTPUT: Provide a reasoning for each choice (using 'desc' and 'rating') and include the 'link'.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": "You are Perspicua. You use Chain-of-Verification logic to fix visual OCR errors with database ground truth before reasoning."
            },
            {"role": "user", "content": prompt}
        ]
    )
    
    # 3. Create the enriched list for the UI display
    enriched_books = []
    for i, meta in enumerate(all_metadata):
        if meta:
            book = book_list[i].copy()
            book.update(meta)
            enriched_books.append(book)
    
    return response.choices[0].message.content, enriched_books