# Perspicua: AI-Powered Semantic Shelf Scanner

<div align="center">
  <img src="images/perspicua.webp" width="600">
</div>

**Perspicua** is a high-performance Vision-AI application designed to solve the "Paradox of Choice" in libraries and bookstores. By combining **GPT-4o Vision** with a **Vector Embedding Brain** and an **Asynchronous Retrieval Pipeline**, Perspicua turns a simple photo of a bookshelf into a semantically searchable digital library.

---

## The Elite Engineering Pipeline
Perspicua moves beyond simple keyword matching by implementing a multi-stage AI architecture built for speed and reliability:

1.  **High-Precision Vision Extraction:** Utilizes **GPT-4o Vision** with `detail: high` to perform OCR on non-uniform, stylized, and vertical book spines across multiple images.
2.  **Semantic Brain (Vector Search):** Every book is converted into a **1536-dimensional vector embedding** using `text-embedding-3-small`. When a user provides preferences, the system performs a **Cosine Similarity Search** in vector space to find matches based on deep context, not just titles.
3.  **Memory Layer (SQLite Cache):** Implements an **aiosqlite** caching system. Once a book is scanned, its metadata and vector are stored locally, reducing API latency by **95%** and eliminating redundant token costs.
4.  **Asynchronous Mastery:** Orchestrates concurrent API lookups (Google Books/Open Library) and database I/O using `asyncio` and `httpx`, processing entire libraries (50+ books) in seconds.
5.  **Live Telemetry UI:** A real-time system status sidebar that streams the "thought process" of the AI, providing transparency into the vision extraction and vector math stages.

---

## Tech Stack
* **AI/ML:** OpenAI GPT-4o (Vision), `text-embedding-3-small` (Vectors), NumPy (Similarity Math)
* **Database:** SQLite (aiosqlite) for persistent caching & vector storage
* **DevOps:** Docker & Docker Compose for environment isolation and deployment
* **Backend:** Python 3.11 (Asyncio / HTTPX)
* **Frontend:** Streamlit (Custom Grid Layout & Telemetry UI)

---

## Engineering Highlights
* **Environment Isolation:** Fully Dockerized to ensure a hardened, reproducible security context, preventing "environment drift."
* **Self-Healing RAG:** Implemented a Chain-of-Verification logic that corrects visual OCR errors (e.g., "19B4") using verified API ground truth.
* **Concurrency Connection Pooling:** Used asynchronous pooling to handle high-volume network I/O without blocking the main execution thread.
* **Production UI:** Features a responsive grid gallery, multi-image upload support, and an exportable recommendations engine.

---

## Installation & Setup

### Option A: The "Deployment Armor" (Recommended)
If you have Docker installed, you can launch the entire production environment with a single command:

```bash
docker-compose up --build -d
```

### Option B: Local Manual Setup

1. **Clone the repository:**

```bash
git clone [https://github.com/IsaMaharramov/AI-Book-Discovery-App.git](https://github.com/IsaMaharramov/AI-Book-Discovery-App.git)
cd AI-Book-Discovery-App
```

2. **Set up Environment:**

```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. **Configure API Keys:**

Create a `.env` file in the root directory:

```plaintext
OPENAI_API_KEY=your_actual_openai_key_here
```

4. **Launch:**

```bash
streamlit run app.py
```

## Performance Benchmarks

| Phase | Standard Execution | Perspicua (Cached & Async) |
| :--- | :--- | :--- |
| **Inventory Retrieval (50 books)** | ~75.0s | **~3.5s** |
| **Recommendation Precision** | Keyword-based | **Semantic/Context-aware** |
| **Data Persistence** | None (Stateless) | **Persistent Local Memory** |


## License & Usage
This project is licensed under the GNU GPLv3.

## Terms of Use:
**Open-Source Requirement:** Any distribution or modification must remain open-source under the same license.

**Non-Commercial:** This software is strictly for non-commercial/educational use.

**Attribution:** Clear credit to Isa Maharramov is required.

## Commercial Inquiries
For proprietary or commercial licensing, please contact the author directly.

© 2026 Isa Maharramov