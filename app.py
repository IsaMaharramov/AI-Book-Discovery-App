# ---------------------------------------------------------
# Perspicua AI Engine - UI & Production Guard
# Developed by: Isa Maharramov
# License: GNU GPLv3 (Open-Source / Non-Commercial)
# Copyright (c) 2026 Isa Maharramov
# ---------------------------------------------------------

import streamlit as st
import os
import asyncio
import io
import time
from PIL import Image
from ai_engine import extract_books, get_recommendations

st.set_page_config(page_title="Perspicua", page_icon="🔍", layout="wide")

# --- UI Components: Sidebar Telemetry ---
st.sidebar.title("🛠️ System Telemetry")
status_container = st.sidebar.container()

def update_status(msg):
    """Helper to write logs to the sidebar terminal."""
    status_container.code(f"> {msg}")

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
st.markdown("Scan multiple bookshelves at once to get consolidated AI-powered recommendations.")

prefs = st.text_input("Reading Preferences", placeholder="e.g. Sci-fi with deep world-building")

uploaded_files = st.file_uploader(
    "Upload Shelf Photos", 
    type=['jpg', 'jpeg', 'png'], 
    accept_multiple_files=True
)

if st.button("Analyze Library", use_container_width=True):
    if not prefs or not uploaded_files:
        st.warning("Please provide both reading preferences and at least one shelf photo.")
    else:
        start_time = time.time() # Start Performance Clock
        all_detected_books = []
        
        with st.spinner("Perspicua is processing all images..."):
            for i, uploaded_file in enumerate(uploaded_files):
                update_status(f"📸 Processing Image {i+1}/{len(uploaded_files)}...")
                temp_path = f"temp_shelf_{i}.jpg"
                
                optimized_data = process_and_validate_image(uploaded_file)
                with open(temp_path, "wb") as f:
                    f.write(optimized_data)

                try:
                    update_status(f"👁️ Vision Engine: Extracting spines from Image {i+1}...")
                    new_books = extract_books(temp_path)
                    all_detected_books.extend(new_books)
                except Exception as e:
                    update_status(f"⚠️ Warning: Failed to process Image {i+1}: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            try:
                if not all_detected_books:
                    st.info("No books detected in any of the images.")
                else:
                    # DEDUPLICATION
                    unique_map = {}
                    for b in all_detected_books:
                        key = f"{b.get('title', '')}|{b.get('author', '')}".lower().strip()
                        if key not in unique_map:
                            unique_map[key] = b
                    
                    final_book_list = list(unique_map.values())
                    update_status(f"✅ Library Scan Complete. Found {len(final_book_list)} unique books.")

                    # Execute recommendation engine
                    recommendations, metadata = asyncio.run(
                        get_recommendations(final_book_list, prefs, status_cb=update_status)
                    )
                    
                    total_time = round(time.time() - start_time, 2)
                    update_status(f"🚀 Total processing time: {total_time}s")

                    # Display Reasoning
                    st.subheader("Perspicua's Selection")
                    st.success(f"Analysis complete in {total_time} seconds!")
                    st.markdown(recommendations)

                    # Export Feature
                    st.download_button(
                        label="📥 Download Reading List",
                        data=recommendations,
                        file_name="perspicua_reading_list.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                    if metadata:
                        st.divider()
                        st.subheader("📚 Library Gallery")
                        
                        # 🛡️ NEW: Filter out None values to prevent attribute errors
                        valid_metadata = [b for b in metadata if b is not None]
                        
                        if not valid_metadata:
                            st.info("Inventory processed, but no detailed metadata was found for these items.")
                        else:
                            # --- Grid Layout (3 columns) ---
                            cols = st.columns(3)
                            for idx, b in enumerate(valid_metadata):
                                with cols[idx % 3]: 
                                    with st.container(border=True):
                                        # Safe check for cover image
                                        image_url = b.get("image")
                                        if image_url:
                                            st.image(image_url, use_container_width=True)
                                        else:
                                            st.write("No Cover Image")
                                        
                                        # Safe extraction of details
                                        title = b.get('title', 'Unknown Title')
                                        author = b.get('author', 'Unknown Author')
                                        rating = b.get('rating', 'N/A')
                                        rating_text = f"⭐ {rating}" if rating != "N/A" else "Not yet rated"
                                        
                                        st.markdown(f"**{title}**")
                                        st.caption(f"{author}\n\n{rating_text}")
                                        
                                        with st.expander("Description"):
                                            st.write(b.get("desc", "No description available."))
                                        
                                        st.link_button("View Book", b.get("link", "#"), use_container_width=True)
                                    
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                update_status(f"❌ ERROR: {str(e)}")

footer_html = """
<div style="text-align: center;">
    <p>© 2026 <b>Isa Maharramov</b>. All rights reserved.</p>
    <p><a href="https://yourwebsite.com" target="_blank" style="color: #ff4b4b; text-decoration: none;">Visit My Website</a></p>
    <p style="font-size: 0.8em; color: grey;">Licensed under GNU GPLv3</p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)