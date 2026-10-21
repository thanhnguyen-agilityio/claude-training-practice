import logging

import requests
import streamlit as st
from utils.constants import API_BASE_URL


def health_check():
    try:
        response = requests.get(API_BASE_URL + "/health")
        if response.status_code != 200:
            st.error("Health check failed. Please check the server logs.")
            logging.error(f"Health check failed. Status code: {response.status_code}")
            st.stop()
    except Exception as e:
        st.error("Server is not healthy. Please check the server logs.")
        logging.error(f"Server is not healthy. Error: {e}")
        st.stop()
