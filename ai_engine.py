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
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_books(image_path):
    base64_image = encode_image(image_path)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a high-precision library digitization robot. Scan the shelf exhaustivey (20-40 books). Return strictly a JSON object with a key 'books' containing a list of objects with 'title' and 'author'."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract every single book title and author from this image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        response_format={"type": "json_object"}
    )
    result = json.loads(response.choices[0].message.content)
    return result.get("books", [])

async def get_recommendations(book_list, user_prefs):
    # Retrieve metadata for the ENTIRE list (no slicing)
    all_metadata = await get_all_book_metadata(book_list)
    
    enriched_books = []
    for i, meta in enumerate(all_metadata):
        if meta:
            book = book_list[i].copy()
            book.update(meta)
            enriched_books.append(book)
    
    # We pass the ENTIRE enriched shelf to the LLM
    # This allows Perspicua to see every single option detected
    prompt = f"""
    USER PREFERENCES: {user_prefs}
    
    COMPLETE SHELF INVENTORY:
    {json.dumps(enriched_books, indent=2)}
    
    TASK:
    1. Analyze the entire inventory.
    2. Recommend the top 3-5 books that best match the user's preference.
    3. For each recommendation, explain WHY based on the 'desc' and 'rating'.
    4. Provide the 'link' for each recommendation.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Perspicua. You have total visibility of the shelf. Your goal is to find the perfect needle in the haystack."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content, enriched_books

# context_data = enriched_books[:15] if enriched_books else book_list[:15]