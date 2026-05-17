# app/meta_service.py

import requests
import os

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID")
PAGE_ID = os.getenv("META_PAGE_ID")


BASE_URL = "https://graph.facebook.com/v22.0"


def create_campaign(name: str):

    print("🚀 Creating Meta campaign...")

    url = f"{BASE_URL}/act_{AD_ACCOUNT_ID}/campaigns"

    payload = {
    "name": name,
    "objective": "OUTCOME_ENGAGEMENT",
    "status": "PAUSED",
    "special_ad_categories": "[]",
    "is_adset_budget_sharing_enabled": False,
    "access_token": ACCESS_TOKEN
}

    response = requests.post(url, data=payload)

    print("📊 Campaign Response:", response.text)

    return response.json()


def upload_image(image_path: str):

    print("🖼 Uploading image to Meta...")

    url = f"{BASE_URL}/act_{AD_ACCOUNT_ID}/adimages"

    with open(image_path, "rb") as image_file:

        files = {
            "filename": image_file
        }

        data = {
            "access_token": ACCESS_TOKEN
        }

        response = requests.post(
            url,
            files=files,
            data=data
        )

    print("📸 Image Upload Response:", response.text)

    return response.json()


def create_ad_creative(
    image_hash: str,
    message: str,
    whatsapp_number: str
):

    print("🎨 Creating ad creative...")

    url = f"{BASE_URL}/act_{AD_ACCOUNT_ID}/adcreatives"

    payload = {
        "name": "AI Creative",
        "object_story_spec": {
            "page_id": PAGE_ID,
            "link_data": {
                "message": message,
                "image_hash": image_hash,
                "link": f"https://wa.me/{whatsapp_number}",
                "call_to_action": {
                    "type": "WHATSAPP_MESSAGE"
                }
            }
        },
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(
        url,
        json=payload
    )

    print("🎯 Creative Response:", response.text)

    return response.json()


# def create_adset(campaign_id: str):

#     print("📦 Creating ad set...")

#     url = f"{BASE_URL}/act_{AD_ACCOUNT_ID}/adsets"

#     payload = {
#         "name": "AI Outreach AdSet",

#         "campaign_id": campaign_id,

#         "billing_event": "IMPRESSIONS",
#         "destination_type": "WHATSAPP",

#         "optimization_goal": "CONVERSATIONS",

#         "daily_budget": "5000",

#         "bid_strategy": "LOWEST_COST_WITHOUT_CAP",

#         "targeting": {
#             "geo_locations": {
#                 "countries": ["IN"]
#             }
#         },

#         "status": "PAUSED",

#         "promoted_object": {
#             "page_id": PAGE_ID
#         },

#         "access_token": ACCESS_TOKEN
#     }

#     response = requests.post(
#         url,
#         json=payload
#     )

#     print("📊 AdSet Response:", response.text)

#     return response.json()

def create_adset(campaign_id: str):

    print("📦 Creating ad set...")

    url = f"{BASE_URL}/act_{AD_ACCOUNT_ID}/adsets"

    payload = {
        "name": "AI Outreach AdSet",

        "campaign_id": campaign_id,

        "billing_event": "IMPRESSIONS",

        "optimization_goal": "CONVERSATIONS",

        "destination_type": "WHATSAPP",

        "daily_budget": "10000",

        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",

        "targeting": {
            "geo_locations": {
                "countries": ["IN"]
            }
        },

        "status": "PAUSED",

        "promoted_object": {
            "page_id": PAGE_ID
        },

        "access_token": ACCESS_TOKEN
    }

    response = requests.post(
        url,
        json=payload
    )

    print("📊 AdSet Response:", response.text)

    return response.json()


def create_ad(
    creative_id: str,
    adset_id: str
):

    print("📢 Creating final ad...")

    url = f"{BASE_URL}/act_{AD_ACCOUNT_ID}/ads"

    payload = {
        "name": "AI WhatsApp Ad",

        "adset_id": adset_id,

        "creative": {
            "creative_id": creative_id
        },

        "status": "PAUSED",

        "access_token": ACCESS_TOKEN
    }

    response = requests.post(
        url,
        json=payload
    )

    print("🎯 Final Ad Response:", response.text)

    return response.json()