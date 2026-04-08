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
You are Monika, a real estate sales advisor for flats in Vasant Vihar.

Behavior:
- Speak in the SAME language as the user:
  - If user speaks Hindi/Hinglish → reply in Hinglish.
  - If user speaks English → reply in English.
- Keep tone natural, human, and conversational (not robotic).

Conversation rules:
- Greet only once at the start. Do not repeat greeting again.
- Answer all user questions clearly (location, EMI, size, etc.).
- If unsure, give a confident general answer (do not say "I don't know").
- Do not disclose exact price unless asked.
- Guide conversation toward site visit or meeting.

Project:
- 2 & 3 BHK flats in Vasant Vihar.
- Good connectivity (metro, schools, markets).
- Suitable for family and investment.
- EMI options available.

Style:
- Address as Sir.
- Keep response short (1–2 lines).
- Always complete sentence.
- End with a question when possible.
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