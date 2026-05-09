# ---------------------------------------------------------
# Perspicua AI Engine - UI & Production Guard
# Developed by: Isa Maharramov
# License: GNU GPLv3
# Copyright (c) 2026 Isa Maharramov
# ---------------------------------------------------------

import streamlit as st
import os
import asyncio
import io
from PIL import Image
from ai_engine import extract_books, get_recommendations

st.set_page_config(page_title="Perspicua", page_icon="🔍", layout="wide")

def process_and_validate_image(uploaded_file, max_dim=2048):
    """Resizes and compresses images to optimize tokens and prevent DoS."""
    img = Image.open(uploaded_file)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
    return img_byte_arr.getvalue()

st.title("Perspicua 🔍")
st.markdown("Scan a bookshelf and get AI-powered recommendations based on real-time data.")

prefs = st.text_input("Reading Preferences", placeholder="e.g. Sci-fi with deep world-building")
uploaded_file = st.file_uploader("Upload Shelf Photo", type=['jpg', 'jpeg', 'png'])

if st.button("Analyze Shelf", use_container_width=True):
    if not prefs or not uploaded_file:
        st.warning("Please provide both reading preferences and a shelf photo.")
    else:
        with st.spinner("Perspicua is analyzing..."):
            temp_path = "temp_shelf_image.jpg"
            optimized_data = process_and_validate_image(uploaded_file)
            with open(temp_path, "wb") as f:
                f.write(optimized_data)

            try:
                book_list = extract_books(temp_path)
                if not book_list:
                    st.info("No books detected.")
                else:
                    with st.expander("Detected Books"):
                        st.write(book_list)

                    recommendations, metadata = asyncio.run(get_recommendations(book_list, prefs))
                    
                    st.subheader("Perspicua's Selection")
                    st.markdown(recommendations)

                    if metadata:
                        st.divider()
                        st.subheader("Verified Book Details")
                        for b in metadata:
                            with st.container():
                                col1, col2 = st.columns([1, 4])
                                with col1:
                                    if b.get("image"): st.image(b["image"])
                                    else: st.write("No Cover")
                                with col2:
                                    rating = b['rating'] if b['rating'] != "N/A" else "Not yet rated"
                                    st.write(f"### {b['title']}")
                                    st.write(f"**{b.get('author', 'Unknown')}** | ⭐ {rating}")
                                    st.caption(b.get("desc", ""))
                                    st.link_button("Details", b.get("link", "#"))
                                st.write("---")
            except Exception as e:
                st.error(f"Analysis failed: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

footer_html = """
<div style="text-align: center;">
    <p>© 2026 <b>Isa Maharramov</b>. All rights reserved.</p>
    <p><a href="working..." target="_blank" style="color: #ff4b4b; text-decoration: none;">Visit My Website</a></p>
    <p style="font-size: 0.8em; color: grey;">Licensed under GNU GPLv3</p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)