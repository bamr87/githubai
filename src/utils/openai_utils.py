import os
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

def call_openai_chat(messages, model="gpt-4o-mini", temperature=0.2, max_tokens=2500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()