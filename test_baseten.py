import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://inference.baseten.co/v1",
    api_key=os.environ["BASETEN_API_KEY"],
)

response = client.chat.completions.create(
    model="meta-models/muse-spark-open-1026",
    messages=[{"role": "user", "content": "An STM32 prints garbage on UART. List 3 likely causes."}],
)
print(response.choices[0].message.content)
