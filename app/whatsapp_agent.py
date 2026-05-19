# app/whatsapp_agent.py

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SYSTEM_PROMPT = """
You are Priya from Kuber Group Africa.

Your goal:
- answer customer queries
- qualify leads
- collect:
  - budget
  - location
  - property type
- encourage call or site visit

Keep replies:
- short
- premium
- human
- WhatsApp style
"""


def generate_whatsapp_reply(message: str):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.4,
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