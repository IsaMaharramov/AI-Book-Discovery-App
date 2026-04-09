# AI-Powered Shelf Scanner

It is an end-to-end AI application designed to solve the "Paradox of Choice" in bookstores. Instead of manually searching for reviews, users can snap a photo of a bookshelf and receive instant, personalized recommendations based on their unique reading tastes.

---

## The Problem
Walking into a bookstore or library can be overwhelming. With hundreds of spines facing you, finding a book that matches your specific vibe (e.g., "Dark Academia" or "Technical Cybersecurity Thrillers") is time-consuming. 

## The Solution
This app uses a **Vision-Language Model (VLM)** pipeline to:
1.  **Extract:** Perform high-precision OCR on non-uniform text (vertical/stylized book spines).
2.  **Filter:** Clean messy text data and map it to structured JSON entities (Title/Author).
3.  **Reason:** Cross-reference the detected books with abstract user preferences using LLM semantic reasoning.

---

## Tech Stack
* **Language:** Python 3.10+
* **AI Orchestration:** OpenAI GPT-4o (Vision & Reasoning)
* **Frontend/UI:** Streamlit (Mobile-responsive web app)
* **Data Handling:** Base64 Image Encoding & JSON Schema Enforcement
* **Environment:** Python-Dotenv for secure API secret management

---

## Engineering Highlights
* **VLM Implementation:** Utilizes GPT-4o with `detail: high` parameter to handle complex, small-scale text extraction on physical objects.
* **JSON Mode Enforcement:** Strictly enforces structured data output from the LLM to ensure system stability and prevent parsing errors.
* **Semantic Recommender:** Moves beyond keyword matching by using LLM reasoning to understand the "vibe" of a user's preference rather than just genre tags.
* **Error Handling & Grounding:** Implemented validation gates to prevent "hallucinations" when an empty or unreadable shelf is provided.

---

## Installation & Setup

1. **Clone the repository:**
```bash
   git clone https://github.com/IsaMaharramov/AI-Book-Discovery-App.git
   cd AI-Book-Discovery-App
```
2. **Set up Virtual Environment:**

```Bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. **Configure Environment Variables:**

Create a .env file and add your key:
```Code snippet
OPENAI_API_KEY=your_actual_key_here
```

4. **Run the App:**

```Bash
streamlit run app.py
```

## **Working on:**
1. Optimizations;
    
2. Precision;
    
3. Et cētera.