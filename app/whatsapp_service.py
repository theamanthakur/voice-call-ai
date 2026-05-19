# app/whatsapp_service.py

import requests
import os
import json

PHONE_NUMBER_ID = os.getenv(
    "WA_PHONE_NUMBER_ID"
)

TOKEN = os.getenv(
    "WA_TOKEN"
)


def send_whatsapp_message(
    to: str,
    text: str
):

    url = (
        f"https://graph.facebook.com/v22.0/"
        f"{PHONE_NUMBER_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",

        "to": to,

        "type": "text",

        "text": {
            "body": text
        }
    }

    print("\n==============================")
    print("📤 SENDING WHATSAPP MESSAGE")
    print("==============================")

    print(json.dumps(payload, indent=2))

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print("\n📩 WHATSAPP RESPONSE")
    print(response.status_code)
    print(response.text)

    try:
        return response.json()

    except Exception:
        return {
            "error": response.text
        }