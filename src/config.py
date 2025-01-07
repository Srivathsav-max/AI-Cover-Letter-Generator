import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv('NVIDIA_API_BASE_URL'),
    api_key=os.getenv('NVIDIA_API_KEY')
)

MODEL_NAME = os.getenv('MODEL_NAME')
