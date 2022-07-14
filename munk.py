import openai
import os
from dotenv import load_dotenv
load_dotenv()

###################################################################################################################################
# Use the bot a few times with different names, and then you can name the bot something accordingly, or whatever you come up with #
###################################################################################################################################

# You can create funny once, and certain characters; Mickey Mouse, Jack Sparrow, Dracula, etc. (the list is "endless")
# "Clever and Agreeable Friend", "Wholesome Quirky Moral Friend", "Quirky Morally Supportive Friend", "AI", "Friend"
bot_description = "Wholesome Quirky Morally Supportive Me"


def generate_comment(user_input, parent_comment="", is_self=False):
    openai.api_key = os.getenv('APENAI_KEY')

    if(parent_comment == ""):
        prompt = f"You: {user_input}\n" + bot_description + ":"
    elif(is_self):
        prompt = bot_description + ": " + parent_comment + "\nYou: {user_input}\n" + \
            bot_description + ":"
    else:
        prompt = f"Person: {parent_comment}\nYou: {user_input}\n" + \
            bot_description + ":"
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
