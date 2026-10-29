import logging

import requests
import streamlit as st
from utils.constants import API_BASE_URL, ERROR_CONNECTION, ERROR_REQUEST


def health_check():
    try:
        response = requests.get(API_BASE_URL + "/health")
        if response.status_code != 200:
            st.error(ERROR_REQUEST)
            logging.error(f"Health check failed. Status code: {response.status_code}")
            st.stop()
    except Exception as e:
        st.error(ERROR_CONNECTION)
        logging.error(f"Server is not healthy. Error: {e}")
        st.stop()
