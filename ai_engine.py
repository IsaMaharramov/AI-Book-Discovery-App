import base64
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from books_api import get_book_metadata

# Load variables from .env
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path):
    """Convert an image file to a base64 string for the API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_books(image_path):
    """Use GPT-4o Vision to extract book titles and authors from an image."""
    base64_image = encode_image(image_path)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are a high-precision library digitization robot. 
                Scan the bookshelf from top-to-bottom and left-to-right. 

                Rules for extraction:
                1. EXHAUSTIVE SCAN: There are likely 20-40 books. Do not stop after 10. Look at every single spine.
                2. QUALITY THRESHOLD: If a book spine is completely blurry with zero readable characters, SKIP it. Do not hallucinate or guess.
                3. PARTIAL SIGNAL: If you can see even a few letters or a partial title, use your internal knowledge to identify the book (e.g., if you see 'Harr.. Potte..', identify it as Harry Potter).
                
                Return ONLY a JSON object with a key "books" containing a list of objects with 'title' and 'author'."""
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "List every identifiable book on this shelf. I expect a high count (20-30+)."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high" 
                        }
                    },
                ],
            }
        ],
        response_format={"type": "json_object"}
    )
    
    # Parse the string response into a Python list
    result = json.loads(response.choices[0].message.content)
    return result.get("books", result) # Handles different JSON structures

def get_recommendations(book_list, user_prefs):
    """Match extracted books against preferences using RAG (Retrieval-Augmented Generation)."""
    
    # 1. RETRIEVAL: Get real-world data for the books we found
    enriched_books = []
    # We limit to the top 7-8 to keep the API calls fast and the prompt clean
    for book in book_list[:8]: 
        metadata = get_book_metadata(book['title'], book['author'])
        if metadata:
            # Merge the vision data with the API data
            book.update(metadata)
            enriched_books.append(book)
    
    # Use the enriched list if we found matches, otherwise fall back to original
    context_data = enriched_books if enriched_books else book_list

    # 2. AUGMENTATION: Build a prompt with 'Ground Truth' data
    prompt = f"""
    USER PREFERENCES: {user_prefs}
    
    VERIFIED BOOK CONTEXT (from Google Books API):
    {json.dumps(context_data, indent=2)}
    
    TASK:
    Act as a professional librarian. Based on the user's preferences AND the verified data above:
    1. Pick the top 3 matches.
    2. Use the 'rating' and 'desc' (description) from the context to justify your choices.
    3. If a 'link' is provided, include it as a call-to-action for the user.
    
    Tone: Professional, insightful, and slightly witty.
    """
    
    # 3. GENERATION: GPT-4o now reasons based on the data we provided
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a grounded AI librarian. You only recommend books present in the provided context."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Return the AI text AND the data list so app.py can show the covers/stars
    return response.choices[0].message.content, enriched_books