# Perspicua: AI-Powered Shelf Scanner 🔍

**Perspicua** is a high-performance Vision-RAG (Retrieval-Augmented Generation) application designed to solve the "Paradox of Choice" in bookstores. Instead of manually searching for reviews, users can snap a photo of a bookshelf and receive instant, personalized recommendations grounded in real-world metadata.

---

## 🚀 The High-Performance Engine
This isn't just a simple wrapper; it's a multi-stage pipeline built for speed and reliability:

1.  **High-Precision Vision Extraction:** Utilizes **GPT-4o** with `detail: high` to perform OCR on non-uniform, stylized, and vertical book spines.
2.  **Asynchronous Metadata Retrieval:** Implements `httpx` and `asyncio` to perform concurrent API lookups across **Google Books** and **Open Library**. This allows the system to process an entire shelf (30+ books) in seconds.
3.  **Full-Inventory RAG:** Cross-references vision data with live API metadata to "ground" the LLM's reasoning, preventing hallucinations and providing real-world ratings and links for the *entire* shelf.
4.  **Semantic Reasoning:** Moves beyond keyword matching to understand the "vibe" of user preferences (e.g., "Cybersecurity Thrillers" or "Dark Academia").

---

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **AI Models:** OpenAI GPT-4o (Vision & Reasoning)
* **Asynchronous I/O:** `httpx`, `asyncio`
* **Frontend:** Streamlit
* **APIs:** Google Books API, Open Library API

---

## 🏗️ Engineering Highlights
* **Concurrency Mastery:** Used asynchronous connection pooling to handle high-volume network I/O without blocking the main execution thread.
* **Structured Output Enforcement:** Strictly enforces **JSON Schema** for extraction to ensure zero-fail parsing between the VLM and the metadata engine.
* **Self-Documenting Code:** Developed with a focus on clean, modular architecture, moving logic away from the UI and into specialized engines.
* **Robust Resource Management:** Integrated validation gates and `finally` blocks to ensure temporary system files are managed securely.

---

## ⚙️ Installation & Setup

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

---

## 🧩 How It Works:
1. **Input:** User uploads a shelf image + text-based preferences via Streamlit.
2. **Vision Stage:** GPT-4o Vision parses the image and returns a structured JSON inventory.
3. **Async Pipeline:** `httpx` fires parallel requests to multiple book APIs.
4. **RAG Context:** Metadata (descriptions, ratings) is injected into the final reasoning prompt.
5. **Output:** A grounded, witty recommendation list with real-world buy/view links.

---

## ⚡ Performance Benchmarks
| Method | Processing Time (1 book) | Processing Time (30 books) |
| :--- | :--- | :--- |
| **Standard Loop** | ~1.5s | ~45s |
| **Perspicua (Async)** | **~1.5s** | **~3.2s** |
*Note: Results depend on network latency and API response times.*

## 🛡️ Security & Optimization
- **Environment Isolation:** Uses `python-dotenv` to ensure API keys never touch the source code.
- **Resource Cleanup:** Automated temporary file deletion to maintain a zero-footprint local environment.
- **Error Boundaries:** Comprehensive try/except/finally blocks to prevent system crashes during API downtime.

---

## **Working on:**

1. Optimizations;
    
2. Precision;
    
3. Et cētera.


---
## 📜 License & Usage
This project is licensed under the [**GNU GPLv3**](LICENSE). 

### 🛡️ Terms of Use:
* **Open-Source Requirement:** If you use, modify, or distribute this code, your project **must** remain open-source under the same license.
* **Non-Commercial:** You are strictly prohibited from selling this software or using it as a paid product.
* **Attribution:** You must provide clear credit to the original author.

© 2026 **Isa Maharramov**