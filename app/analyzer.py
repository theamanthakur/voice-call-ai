from openai import OpenAI
from app.prompt import SYSTEM_PROMPT
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_call(transcript: str):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript}
        ]
    )

    return response.choices[0].message.content
