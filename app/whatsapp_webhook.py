# app/whatsapp_webhook.py

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

import os
import json

from app.whatsapp_agent import generate_whatsapp_reply
from app.whatsapp_service import send_whatsapp_message
from app.twilio_call import call_number

router = APIRouter()

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")


@router.get("/webhook/whatsapp")
async def verify_webhook(request: Request):

    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    print("📩 META WEBHOOK VERIFY HIT")

    if mode == "subscribe" and token == VERIFY_TOKEN:

        print("✅ WEBHOOK VERIFIED")

        return PlainTextResponse(content=challenge)

    print("❌ WEBHOOK VERIFY FAILED")

    return {"error": "verification failed"}


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(payload: dict):

    try:

        print("\n==============================")
        print("🔥 WHATSAPP MESSAGE RECEIVED")
        print("==============================")

        print(json.dumps(payload, indent=2))

        entry = payload["entry"][0]

        changes = entry["changes"][0]

        value = changes["value"]

        messages = value.get("messages")

        if not messages:

            print("⚠ No messages found")

            return {"status": "ignored"}

        msg = messages[0]

        # ignore non-text messages
        if "text" not in msg:

            print("⚠ Non-text message ignored")

            return {"status": "non-text ignored"}

        phone = msg["from"]

        text = msg["text"]["body"].strip()

        lower_text = text.lower()

        print(f"📲 Phone: {phone}")
        print(f"💬 Message: {text}")

        # AI reply generation
        ai_reply = generate_whatsapp_reply(text)

        print(f"🤖 AI Reply: {ai_reply}")

        # send WhatsApp reply
        send_whatsapp_message(
            phone,
            ai_reply
        )

        print("✅ WhatsApp reply sent")

        # call trigger conditions
        trigger_words = [
            "call me",
            "yes call me",
            "interested",
            "book a call",
            "contact me",
            "callback",
        ]

        should_call = any(
            word in lower_text
            for word in trigger_words
        )

        if should_call:

            print(f"📞 Triggering AI call to +{phone}")

            # optional confirmation message
            send_whatsapp_message(
                phone,
                "Perfect sir 👍 Our AI advisor is calling you now."
            )

            # trigger Twilio voice AI call
            call_number(f"+{phone}")

            print("✅ AI Call Started")

        else:

            print("ℹ No call trigger matched")

        return {
            "status": "success"
        }

    except Exception as e:

        print("❌ WHATSAPP WEBHOOK ERROR")
        print(str(e))

        return {
            "error": str(e)
        }