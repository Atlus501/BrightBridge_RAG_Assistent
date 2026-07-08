from dotenv import load_dotenv
import os

load_dotenv()

# TEMP DEBUG PRINTS: Run your test script and look at your terminal output
print("--- ENV DEBUGGING ---")
print(f"What's in GEMINI_API_KEY env: {os.getenv('GEMINI_API_KEY')}")
print(f"What's in GEMINI_API env: {os.getenv('GEMINI_API')}")
print("---------------------")