import requests

def get_from_google_books(title, author):
    """Internal helper for Google Books API."""
    query = f"intitle:{title} inauthor:{author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
    try:
        res = requests.get(url, timeout=5).json()
        if "items" in res:
            item = res["items"][0]["volumeInfo"]
            return {
                "rating": item.get("averageRating", "N/A"),
                "desc": item.get("description", "No description available.")[:250],
                "link": item.get("infoLink", "#"),
                "image": item.get("imageLinks", {}).get("thumbnail", ""),
                "source": "Google"
            }
    except:
        return None
    return None

def get_from_open_library(title):
    """Internal helper for Open Library API."""
    url = f"https://openlibrary.org/search.json?title={title}&limit=1"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("docs"):
            doc = res["docs"][0]
            return {
                "rating": doc.get("ratings_average", "N/A"),
                "desc": "Subjects: " + ", ".join(doc.get("subject", []))[:200],
                "link": f"https://openlibrary.org{doc.get('key', '')}",
                "image": f"https://covers.openlibrary.org/b/id/{doc.get('cover_i')}-M.jpg" if doc.get('cover_i') else "",
                "source": "OpenLibrary"
            }
    except:
        return None
    return None

def get_book_metadata(title, author):
    """
    Perspicua Engine: Orchestrates multiple sources to get the best data.
    The core of RAG Retrieval step.
    """
    # Try Google Books first
    data = get_from_google_books(title, author)
    
    # If Google fails or doesn't have a description, try Open Library
    if not data or data.get("desc") == "No description available.":
        ol_data = get_from_open_library(title)
        if ol_data:
            # If had some Google data but no desc, merge them
            if data:
                data.update({"desc": ol_data["desc"], "source": "Google+OpenLibrary"})
            else:
                data = ol_data
                
    return data