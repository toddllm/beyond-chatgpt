import os
from openai import OpenAI
import chainlit as cl  # importing chainlit for our app

# Read OpenAI API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ChatOpenAI Templates
system_template = """You are a helpful assistant who always speaks like a pirate!
"""

user_template = """{input}
Think through your response step by step.
"""


@cl.on_chat_start  # marks a function that will be executed at the start of a user session
async def start_chat():
    settings = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": 500,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }

    cl.user_session.set("settings", settings)


@cl.on_message  # marks a function that should be run each time the chatbot receives a message from a user
async def main(message: cl.Message):
    settings = cl.user_session.get("settings")

    # Prepare the prompt
    prompt = [
        {"role": "system", "content": system_template},
        {"role": "user", "content": user_template.format(input=message.content)},
    ]

    msg = cl.Message(content="")

    # Call OpenAI API with stream=True
    response = client.chat.completions.create(
        model=settings["model"],
        messages=prompt,
        temperature=settings["temperature"],
        max_tokens=settings["max_tokens"],
        top_p=settings["top_p"],
        frequency_penalty=settings["frequency_penalty"],
        presence_penalty=settings["presence_penalty"],
        stream=True,
    )

    # Handle the response
    for stream_resp in response:
        # Directly access the 'content' attribute instead of using .get()
        token = stream_resp.choices[0].delta.content if stream_resp.choices[0].delta.content else ''
        await msg.stream_token(token)

    # Finalize the message
    await msg.send()
