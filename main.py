import dotenv
import os
from openai import OpenAI

dotenv.load_dotenv()
myOpenAI = OpenAI()
myOpenAI.api_key = os.getenv("OPENAI_API_KEY")

user_input = input("Write down your prompt >>>")

response = myOpenAI.chat.completions.create(
    model = "gpt-4o",
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input}
    ]
)

print(response.choices[0].message.content)