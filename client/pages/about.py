import logging

import streamlit as st

try:
    with open("./assets/docs/about.md", "r") as f:
        about_us_content = f.read()
except FileNotFoundError:
    logging.error("File not found!")
    about_us_content = "# About Us"

# About Us Page
st.image("./assets/images/ecommer-about-hero-image.png", use_container_width=True)
st.markdown(about_us_content)
st.page_link("pages/agent.py", label="Let’s get started!", icon="🛍️")
