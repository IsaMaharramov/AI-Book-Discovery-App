import streamlit as st
import os
from ai_engine import extract_books, get_recommendations

# Page Config - Makes it look good on mobile
st.set_page_config(page_title="Shelf Scanner", page_icon="📚")

st.title("Shelf Scanner 📚")
st.markdown("Scan a bookshelf and get AI-powered recommendations based on your taste.")

# 1. User Inputs
prefs = st.text_input("What kind of books do you like?", placeholder="e.g. Sci-fi with deep world-building, or dark history")

uploaded_file = st.file_uploader("Take a photo of the shelf", type=['jpg', 'jpeg', 'png'])

# 2. The Logic Loop
if st.button("Scan & Recommend", use_container_width=True):
    if not prefs:
        st.error("Please tell me what you like first!")
    elif not uploaded_file:
        st.error("Please upload or take a photo of a bookshelf.")
    else:
        with st.spinner("🤖 AI is reading the spines..."):
            try:
                # Save the uploaded file temporarily so our engine can read it
                temp_filename = "temp_shelf_image.jpg"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Step 1: Extract titles using Vision
                book_list = extract_books(temp_filename)
                
                if not book_list:
                    st.warning("🕵️‍♂️ I couldn't find any readable book titles on this shelf. Try a clearer photo!")
                else:
                    # Show the user what we found
                    with st.expander("See detected books"):
                        st.write(book_list)

                    # Step 2: Get personalized recommendations
                    st.subheader("Top Picks for You")
                    recommendations = get_recommendations(book_list, prefs)
                    st.markdown(recommendations)

                    # Clean up the temp file
                    os.remove(temp_filename)

            except Exception as e:
                st.error(f"Something went wrong: {e}")