# !FIX ME: still note set env variable in .env file
import os

from dotenv import find_dotenv, load_dotenv

# Load the .env file
load_dotenv(find_dotenv(), override=True)

print(f"Test load value of OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
