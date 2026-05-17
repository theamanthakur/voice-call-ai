# app/whatsapp_service.py

import requests
import os

PHONE_NUMBER_ID = os.getenv("WA_PHONE_NUMBER_ID")
TOKEN = os.getenv("WA_TOKEN")


def send_whatsapp_message(to: str, text: str):

    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

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

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print(response.text)