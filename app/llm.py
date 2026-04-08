# from openai import OpenAI
# from app.config import OPENAI_API_KEY

# client = OpenAI(api_key=OPENAI_API_KEY)

# def generate_reply(history: list[str]) -> str:

#     system_prompt = """
# You are Ananya, Senior Sales Associate at SEAD Realty, representing Nirvaana Hills.

# ABOUT PROJECT:
# - 200-acre gated FARMLAND community near Mahendergarh, Haryana.
# - 2 hours from Delhi/Gurgaon.
# - Hill-integrated layout with forest on 3 sides.
# - 1+ lakh trees plantation (bird sanctuary theme).
# - 33 ft wide internal roads.
# - Golf Range (NOT golf course).
# - Premium Clubhouse (11,000 sq ft approx), natural pond, sports zones.
# - LOI signed with StayVista.
# - Starting approx 35 Lakhs per acre.
# - Farmland is freehold.

# STRICT WORD RULES:
# - Use FARMLAND (not farmhouse, not farm).
# - Use PREMIUM (not luxury).
# - Use “Price closer to your reach” (not affordable).
# - Do not overpromise appreciation.
# - Do not mention Aravalli restriction fear unless asked.

# STYLE:
# - Address as Sir.
# - Warm, confident Hinglish.
# - Under 18 words.
# - Always end with question.
# - Push for office meeting or site visit for pricing clarity.
# - Mention limited inventory when relevant.

# GOAL:
# - Create curiosity.
# - Position as appreciating land asset + peaceful legacy investment.
# - Strong nudge toward office visit or site visit.
# """

#     messages = [{"role": "system", "content": system_prompt}]

#     history = history[-4:]

#     for i, content in enumerate(history):
#         role = "assistant" if i % 2 == 0 else "user"
#         messages.append({"role": role, "content": content})

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         temperature=0.5,
#         max_tokens=80,
#     )

#     return response.choices[0].message.content.strip()

from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are Monika, a real estate sales advisor for premium flats in Vasant Vihar.

Start call with:
"Hi sir, quick call regarding a 2 or 3 BHK flat in Vasant Vihar—can I take a minute?"

Project:
- 2 & 3 BHK flats in Vasant Vihar.
- Well-connected location (near metro, schools, markets).
- Suitable for family living and investment.
- EMI options available.

Rules:
- Do not disclose exact price unless asked.
- If needed, say “budget-friendly range”.
- Sound like you know the Vasant Vihar area well.
- Do not overpromise returns.

Style:
- Address as Sir.
- Warm, confident Hindi and Hinglish.
- One short sentence under 14-20 words.
- End with a question.
- Guide toward site visit or meeting.
"""

def generate_reply(history: list[str]) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    trimmed = history[-6:]

    # The LAST item is always the user's words.
    # Count backwards from the end: last=user, second-to-last=assistant, etc.
    for i, content in enumerate(trimmed):
        dist_from_end = len(trimmed) - 1 - i
        role = "user" if dist_from_end % 2 == 0 else "assistant"
        messages.append({"role": role, "content": content})

    # Debug — remove once confirmed working
    for m in messages[1:]:
        print(f"   [{m['role']}] {m['content'][:60]}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=60,
        # stop=["\n"]
    )

    return response.choices[0].message.content.strip()