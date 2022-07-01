import openai
import os
from dotenv import load_dotenv
load_dotenv()

def generate_comment(user_input):
    openai.api_key = os.getenv('APENAI_KEY')
    prompt = f"You: {user_input}\nQuirky and Wholesome Friend:"
    return openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0.15,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0,
        stop=["\nYou:"]
    ).choices[0].text
