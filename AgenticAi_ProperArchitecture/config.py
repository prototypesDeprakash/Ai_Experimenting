from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API"),
    base_url="https://openrouter.ai/api/v1"
)