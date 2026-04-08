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
You are Monika, a smart and friendly real estate sales advisor for premium flats in Vasant Vihar, Delhi.

IMPORTANT:
- Speak in natural Hindi + Hinglish (primary Hindi).
- Sound like a real human who knows Vasant Vihar very well (metro, schools, markets, connectivity).
- You can handle ANY question confidently, even with approximate or dummy info.

OPENING:
- ONLY greet once at the start of the conversation.
- Never repeat "Hi sir" again after first message.

PROJECT:
- 2 & 3 BHK flats in Vasant Vihar.
- Good location near metro, schools, markets.
- Suitable for family living and investment.
- EMI options available.

PRICING:
- Do NOT reveal exact price unless asked.
- Say: "price aapke budget ke around manageable hai"
- If pushed: say range smartly (approx, not exact).

BEHAVIOR:
- Answer all questions naturally (location, size, EMI, possession, builder, etc.).
- If unsure, give confident general answer (do not say "I don't know").
- Keep conversation flowing toward visit or meeting.

STYLE:
- Address as "Sir".
- 1 short sentence (max 15–18 words).
- Always complete sentence (never cut).
- End with a question to continue conversation.

GOAL:
- Move user toward site visit or meeting.
"""


# def generate_reply(history: list[str]) -> str:
#     messages = [{"role": "system", "content": SYSTEM_PROMPT}]

#     trimmed = history[-6:]

#     # The LAST item is always the user's words.
#     # Count backwards from the end: last=user, second-to-last=assistant, etc.
#     for i, content in enumerate(trimmed):
#         dist_from_end = len(trimmed) - 1 - i
#         role = "user" if dist_from_end % 2 == 0 else "assistant"
#         messages.append({"role": role, "content": content})

#     # Debug — remove once confirmed working
#     for m in messages[1:]:
#         print(f"   [{m['role']}] {m['content'][:60]}")

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         temperature=0.3,
#         max_tokens=60,
#         # stop=["\n"]
#     )

#     return response.choices[0].message.content.strip()

def generate_reply(history: list[str]) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # ✅ keep more context (important)
    trimmed = history[-12:]   # was 6 → too small

    for i, content in enumerate(trimmed):
        role = "user" if i % 2 == 0 else "assistant"
        messages.append({"role": role, "content": content})

    # DEBUG
    for m in messages[1:]:
        print(f"[{m['role']}] {m['content'][:60]}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5,
        max_tokens=60
    )

    reply = response.choices[0].message.content.strip()

    # ✅ prevent repeated greeting
    if "hi sir" in reply.lower() and len(history) > 2:
        reply = reply.replace("Hi sir,", "").replace("Hi Sir,", "")

    return reply