from openai import OpenAI
import os


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are Kuber Groups AI Assistant.

Company:
Kuber Groups

Goals:
- Answer customer queries
- Explain services
- Capture lead details
- Book appointments
- Collect name, phone and requirements
- Keep replies short
"""

def generate_kuber_reply(message: str):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return response.choices[0].message.content