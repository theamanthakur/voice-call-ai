# import httpx
# import os

# ANALYZER_URL = os.getenv("ANALYZER_URL")

# async def send_call_for_analysis(call_sid, transcript):

#     payload = {
#         "call_sid": call_sid,
#         "transcript": transcript
#     }

#     async with httpx.AsyncClient() as client:
#         res = await client.post(
#             f"{ANALYZER_URL}/analyze-call",
#             json=payload,
#             timeout=60
#         )

#     return res.json()