import openai
import os
from dotenv import load_dotenv
load_dotenv()

# "Clever and Agreeable Friend", "Wholesome Quirky Moral Friend", "Quirky Morally Supportive Friend"
bot_description = "Quirky Morally Supportive Friend"


def generate_comment(user_input, parent_comment):
    openai.api_key = os.getenv('APENAI_KEY')

    if(parent_comment == ""):
        prompt = f"You: {user_input}\n" + bot_description + ":"
    else:
        prompt = f"Your Friend: {parent_comment}\nYou: {user_input}\n" + \
            bot_description + ":"
    print("Prompt: ", prompt)
    return openai.Completion.create(
        model="text-davinci-002",  # text-davinci-002 - text-curie-001
        prompt=prompt,
        temperature=0.9,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0,
        presence_penalty=0.6,
        best_of=1,
        stop=["\nYou:"]
    ).choices[0].text
