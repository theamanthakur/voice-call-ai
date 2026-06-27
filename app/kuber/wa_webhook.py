# app/kuber_whatsapp_webhook.py

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

import os
import json

from app.kuber_whatsapp_agent import generate_kuber_reply
from app.kuber_whatsapp_service import send_kuber_message
from app.twilio_call import call_number

router = APIRouter()

VERIFY_TOKEN = os.getenv("KUBER_META_VERIFY_TOKEN")


@router.get("/webhook/kuber-whatsapp")
async def verify_webhook(request: Request):

    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    print("📩 KUBER WEBHOOK VERIFY HIT")

    if mode == "subscribe" and token == VERIFY_TOKEN:

        print("✅ KUBER WEBHOOK VERIFIED")

        return PlainTextResponse(content=challenge)

    print("❌ KUBER WEBHOOK VERIFY FAILED")

    return {"error": "verification failed"}


@router.post("/webhook/kuber-whatsapp")
async def kuber_webhook(payload: dict):

    try:

        print("\n==============================")
        print("🏠 KUBER WHATSAPP MESSAGE RECEIVED")
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

        # Ignore non-text messages
        if "text" not in msg:

            print("⚠ Non-text message ignored")

            return {"status": "non-text ignored"}

        phone = msg["from"]

        text = msg["text"]["body"].strip()

        lower_text = text.lower()

        print(f"📲 Phone: {phone}")
        print(f"💬 Message: {text}")

        # AI reply generation
        ai_reply = generate_kuber_reply(text)

        print(f"🤖 AI Reply: {ai_reply}")

        # Send WhatsApp reply
        send_kuber_message(
            phone,
            ai_reply
        )

        print("✅ WhatsApp reply sent")

        # Call trigger conditions
        trigger_words = [
            "call me",
            "yes call me",
            "interested",
            "book a call",
            "contact me",
            "callback",
            "site visit",
            "schedule visit",
            "property details",
        ]

        should_call = any(
            word in lower_text
            for word in trigger_words
        )

        if should_call:

            print(f"📞 Triggering AI call to +{phone}")

            send_kuber_message(
                phone,
                "Thank you 👍 Our property advisor is calling you now."
            )

            call_number(f"+{phone}")

            print("✅ AI Call Started")

        else:

            print("ℹ No call trigger matched")

        return {
            "status": "success"
        }

    except Exception as e:

        print("❌ KUBER WHATSAPP WEBHOOK ERROR")
        print(str(e))

        return {
            "error": str(e)
        }