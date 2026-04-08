import base64
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

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
    """Match the extracted books against user preferences."""
    prompt = f"""
    The user likes: {user_prefs}
    Available books on the shelf: {json.dumps(book_list)}
    
    Act as a professional librarian. Based on the user's preferences, pick the top 3 books from the list.
    Explain briefly (1-2 sentences) why each is a good match.
    If none match well, suggest the closest one and explain why.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful and witty librarian."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content