import openai


def generate_comment(user_input):
    openai.api_key = "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"
    prompt = f"You: {user_input}\nSmart and Wholesome Friend:"
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
