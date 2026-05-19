# app/whatsapp_campaign.py

import requests
import os
import json

WA_TOKEN = os.getenv("WA_TOKEN")

WA_PHONE_NUMBER_ID = os.getenv("WA_PHONE_NUMBER_ID")

BASE_URL = (
    f"https://graph.facebook.com/v22.0/"
    f"{WA_PHONE_NUMBER_ID}/messages"
)


def send_template_message(
    phone: str,
    customer_name: str,
    template_name: str = "hello_world"
):

    print("\n==============================")
    print("🚀 SENDING WHATSAPP CAMPAIGN")
    print("==============================")

    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",

        "to": phone,

        "type": "template",

        "template": {
            "name": template_name,

            "language": {
                "code": "en_US"
            }
        }
    }

    print("📤 Payload:")
    print(json.dumps(payload, indent=2))

    response = requests.post(
        BASE_URL,
        headers=headers,
        json=payload
    )

    print("📥 Meta Response:")
    print(response.text)

    return response.json()