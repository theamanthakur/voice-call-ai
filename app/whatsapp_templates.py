# app/whatsapp_templates.py

import requests
import os

ACCESS_TOKEN = os.getenv("WA_TOKEN")
WABA_ID = os.getenv("WA_BUSINESS_ACCOUNT_ID")


def get_templates():

    url = (
        f"https://graph.facebook.com/v22.0/"
        f"{WABA_ID}/message_templates"
    )

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    response = requests.get(
        url,
        headers=headers
    )

    return response.json()