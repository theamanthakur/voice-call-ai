# # app/twilio_call.py
# from twilio.rest import Client
# from app.config import (
#     TWILIO_SID,
#     TWILIO_TOKEN,
#     TWILIO_FROM_NUMBER,
# )

# client = Client(TWILIO_SID, TWILIO_TOKEN)

# def call_number(to_number: str):
#     call = client.calls.create(
#         to=to_number,
#         from_=TWILIO_FROM_NUMBER,
#         url="https://web-production-c0d66.up.railway.app/voice",
#     )
#     print("📞 Outbound call SID:", call.sid)
#     return call.sid

# def play_audio(call_sid: str, audio_url: str):
#     client.calls(call_sid).update(
#         twiml=f"""
# <Response>
#   <Play>{audio_url}</Play>
#   <Pause length="60"/>
# </Response>
# """
#     )

# app/twilio_call.py
from twilio.rest import Client
from app.config import EXOTEL_SID, EXOTEL_TOKEN, EXOTEL_NUMBER
import requests


from app.config import (
    TWILIO_SID,
    TWILIO_TOKEN,
    TWILIO_FROM_NUMBER,
)

client = Client(TWILIO_SID, TWILIO_TOKEN)

# Maps call_sid → phone number for lookup during WebSocket session
_sid_to_number: dict[str, str] = {}


# def call_number(to_number: str) -> str:
#     call = client.calls.create(
#         to=to_number,
#         from_=TWILIO_FROM_NUMBER,
#         url="https://web-production-c0d66.up.railway.app/voice",
#     )
#     _sid_to_number[call.sid] = to_number
#     print(f"📞 Outbound call → {to_number} | SID: {call.sid}")
#     return call.sid

def call_number(number: str):

    url = f"https://api.exotel.com/v1/Accounts/{EXOTEL_SID}/Calls/connect"

    payload = {
        "From": EXOTEL_NUMBER,
        "To": number,
        "CallerId": EXOTEL_NUMBER,
        "Url": "https://web-production-c0d66.up.railway.app/exotel-voice"
    }

    res = requests.post(
        url,
        data=payload,
        auth=(EXOTEL_SID, EXOTEL_TOKEN)
    )

    print("📞 Exotel call triggered:", res.text)
    return res.text


def get_number_for_sid(call_sid: str) -> str | None:
    return _sid_to_number.get(call_sid)


def play_audio(call_sid: str, audio_url: str):
    client.calls(call_sid).update(
        twiml=f"""<Response>
  <Play>{audio_url}</Play>
  <Pause length="60"/>
</Response>"""
    )