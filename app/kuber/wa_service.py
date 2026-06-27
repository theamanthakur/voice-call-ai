import os
import requests

PHONE_NUMBER_ID = os.getenv("KUBER_WA_PHONE_NUMBER_ID")
TOKEN = os.getenv("KUBER_WA_TOKEN")

def send_kuber_message(to, text):

    url = (
        f"https://graph.facebook.com/v22.0/"
        f"{PHONE_NUMBER_ID}/messages"
    )

    requests.post(
        url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": text
            }
        }
    )