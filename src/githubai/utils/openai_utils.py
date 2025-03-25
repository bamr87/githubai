import os
import logging
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        filename='openai_api.log',
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def call_openai_chat(messages, model="gpt-4o-mini", temperature=0.2, max_tokens=2500):
    try:
        user_id = os.getenv('USER_ID', 'unknown_user')
        logging.info(f"User: {user_id}, Prompt: {messages}, Model: {model}")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Logging error: {str(e)}")
        return None

setup_logging()
