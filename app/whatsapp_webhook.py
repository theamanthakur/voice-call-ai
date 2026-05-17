# app/whatsapp_webhook.py

from fastapi import APIRouter, Request
import os
from app.whatsapp_agent import generate_whatsapp_reply
from app.whatsapp_service import send_whatsapp_message
from app.twilio_call import call_number

router = APIRouter()


VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")


@router.get("/webhook/whatsapp")
async def verify_webhook(request: Request):

    params = request.query_params

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))

    return {"error": "verification failed"}


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(payload: dict):

    try:
        entry = payload["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        messages = value.get("messages")

        if not messages:
            return {"status": "ignored"}

        msg = messages[0]

        phone = msg["from"]
        text = msg["text"]["body"]

        print(f"📩 {phone}: {text}")

        # AI reply
        ai_reply = generate_whatsapp_reply(text)

        send_whatsapp_message(phone, ai_reply)

        # trigger call condition
        trigger_words = [
            "call",
            "yes",
            "interested",
            "book",
        ]

        if any(word in text.lower() for word in trigger_words):

            call_number(f"+{phone}")

        return {"status": "success"}

    except Exception as e:
        print("❌ webhook error:", e)
        return {"error": str(e)}