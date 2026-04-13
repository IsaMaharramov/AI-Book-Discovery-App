import httpx
import asyncio

async def fetch_google_books(client, title, author):
    query = f"intitle:{title} inauthor:{author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
    try:
        resp = await client.get(url, timeout=5)
        data = resp.json()
        if "items" in data:
            item = data["items"][0]["volumeInfo"]
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

async def fetch_open_library(client, title):
    url = f"https://openlibrary.org/search.json?title={title}&limit=1"
    try:
        resp = await client.get(url, timeout=5)
        data = resp.json()
        if data.get("docs"):
            doc = data["docs"][0]
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

async def get_book_metadata(client, title, author):
    data = await fetch_google_books(client, title, author)
    
    if not data or data.get("desc") == "No description available.":
        ol_data = await fetch_open_library(client, title)
        if ol_data:
            if data:
                data.update({"desc": ol_data["desc"], "source": "Google+OpenLibrary"})
            else:
                data = ol_data
    return data

async def get_all_book_metadata(book_list):
    """Orchestrates parallel retrieval for the entire shelf list."""
    async with httpx.AsyncClient() as client:
        tasks = [get_book_metadata(client, b['title'], b['author']) for b in book_list]
        return await asyncio.gather(*tasks)