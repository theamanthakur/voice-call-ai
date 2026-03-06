# app/twilio_call.py
from twilio.rest import Client
from app.config import (
    TWILIO_SID,
    TWILIO_TOKEN,
    TWILIO_FROM_NUMBER,
)

client = Client(TWILIO_SID, TWILIO_TOKEN)

def call_number(to_number: str):
    call = client.calls.create(
        to=to_number,
        from_=TWILIO_FROM_NUMBER,
        url="https://web-production-c0d66.up.railway.app/voice",
    )
    print("📞 Outbound call SID:", call.sid)
    return call.sid

def play_audio(call_sid: str, audio_url: str):
    client.calls(call_sid).update(
        twiml=f"""
<Response>
  <Play>{audio_url}</Play>
  <Pause length="60"/>
</Response>
"""
    )