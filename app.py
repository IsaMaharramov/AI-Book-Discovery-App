'''
Fixing speed leads to high token usage -> fix
'''

import streamlit as st
import os
import asyncio
from ai_engine import extract_books, get_recommendations

st.set_page_config(page_title="Perspicua", page_icon="🔍")

st.title("Perspicua 🔍")
st.markdown("Scan a bookshelf and get AI-powered recommendations based on real-time data.")

prefs = st.text_input("Reading Preferences", placeholder="e.g. Sci-fi with deep world-building, or dark history")
uploaded_file = st.file_uploader("Upload Shelf Photo", type=['jpg', 'jpeg', 'png'])

if st.button("Analyze Shelf", use_container_width=True):
    if not prefs or not uploaded_file:
        st.warning("Please provide both reading preferences and a shelf photo.")
    else:
        with st.spinner("Perspicua is analyzing the shelf..."):
            temp_path = "temp_shelf_image.jpg"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                book_list = extract_books(temp_path)
                
                if not book_list:
                    st.info("No books detected. Please try a clearer image.")
                else:
                    with st.expander("Detected Books"):
                        st.write(book_list)

                    # the asynchronous retrieval engine
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
                                    if b.get("image"):
                                        st.image(b["image"])
                                    else:
                                        st.write("No Cover")
                                with col2:
                                    st.write(f"### {b['title']}")
                                    
                                    st.write(f"**{b['author']}** | ⭐ {b['rating']}")   # fix                               

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
    <!-- <p><a href="https://yourwebsite.com" target="_blank">Visit my Website</a></p> -->
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)