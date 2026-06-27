# # app/main.py
# from fastapi import FastAPI, WebSocket
# from fastapi.responses import Response
# from app.twilio_ws import twilio_ws
# from app.twilio_call import call_number
# from app.models import CallTranscript
# from app.analyzer import analyze_call
# from app.store import get_all_results
# from fastapi.middleware.cors import CORSMiddleware 

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.post("/voice")
# def voice():
#     # We use <Connect> for a robust bi-directional stream
#     railway_url = "web-production-c0d66.up.railway.app"
#     twiml = f"""<?xml version="1.0" encoding="UTF-8"?>

# <Response>
#     <Connect>
#         <Stream url="wss://{railway_url}/ws" />
#     </Connect>
# </Response>
#     """
#     return Response(content=twiml, media_type="application/xml")

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await twilio_ws(websocket)

# @app.post("/call")
# def make_call(number: str):
#     sid = call_number(number)
#     return {"call_sid": sid}

# @app.post("/call-batch")
# async def call_batch(data: dict):

#     numbers_text = data.get("numbers", "")

#     numbers = [
#         n.strip()
#         for n in numbers_text.split("\n")
#         if n.strip()
#     ]

#     for number in numbers:
#         call_number(number)

#     return {"status": "started", "count": len(numbers)}

# @app.get("/")
# def health():
#     return {"status": "AI Voice Agent running"}

# @app.post("/analyze-call")
# async def analyze(data: CallTranscript):

#     result = analyze_call(data.transcript)

#     return {
#         "call_sid": data.call_sid,
#         "number": data.phone_number,
#         "duration": data.duration,
#         "analysis": result
#     }

# @app.get("/results")
# def get_results():
#     return get_all_results()


# app/main.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import Response
from fastapi import (
FastAPI,
WebSocket,
Request,
UploadFile,
File
)

from fastapi.middleware.cors import CORSMiddleware
from app.twilio_ws import twilio_ws
from app.twilio_call import call_number
from app.models import CallTranscript
from app.analyzer import analyze_call
from app.store import get_all_results
from app.whatsapp_webhook import router as whatsapp_router
from app.lead_store import get_leads
from app.meta_service import (
    create_campaign,
    upload_image,
    create_ad_creative,
    create_adset,
    create_ad,
)
from app.whatsapp_campaign import send_template_message
from app.whatsapp_templates import get_templates
from app.kuber.wa_webhook import router as kuber_router



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(kuber_router)

# RAILWAY_URL = "web-production-c0d66.up.railway.app"
RAILWAY_URL = "web-production-c0d66.up.railway.app"
# https://agrostographic-congenital-brook.ngrok-free.dev


@app.get("/")
def health():
    return {"status": "AI Voice Agent running"}


@app.post("/voice")
def voice():
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://{RAILWAY_URL}/ws" />
    </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await twilio_ws(websocket)


@app.post("/call")
def make_call(number: str):
    sid = call_number(number)
    return {"call_sid": sid}


@app.post("/call-batch")
async def call_batch(data: dict):
    numbers_text = data.get("numbers", "")
    numbers = [
        n.strip().replace(" ", "")          # strip spaces: +91 98765 → +9198765
        for n in numbers_text.split("\n")
        if n.strip()
    ]
    for number in numbers:
        call_number(number)
    return {"status": "started", "count": len(numbers)}


@app.post("/analyze-call")
async def analyze(data: CallTranscript):
    result = analyze_call(data.transcript)
    return {
        "call_sid": data.call_sid,
        "number": data.phone_number,
        "duration": data.duration,
        "analysis": result,
    }


@app.get("/results")
def get_results():
    return get_all_results()


@app.get("/leads")
def leads():
    return get_leads()


# @app.post("/create-ad")
# async def create_ad_endpoint():

#     print("\n==============================")
#     print("🚀 FULL META FLOW STARTED")
#     print("==============================")

#     # CAMPAIGN
#     campaign = create_campaign(
#         "AI Outreach Campaign"
#     )

#     campaign_id = campaign["id"]

#     print("✅ Campaign ID:", campaign_id)

#     # IMAGE
#     image = upload_image(
#         "static/ad.jpg"
#     )

#     image_hash = list(
#         image["images"].values()
#     )[0]["hash"]

#     print("✅ Image Hash:", image_hash)

#     # CREATIVE
#     creative = create_ad_creative(
#         image_hash=image_hash,
#         message="Premium 2-3 BHK homes in Dwarka. Message now.",
#         whatsapp_number="9198XXXXXXX"
#     )

#     creative_id = creative["id"]

#     print("✅ Creative ID:", creative_id)

#     # ADSET
#     adset = create_adset(
#         campaign_id
#     )

#     adset_id = adset["id"]

#     print("✅ AdSet ID:", adset_id)

#     # FINAL AD
#     ad = create_ad(
#         creative_id=creative_id,
#         adset_id=adset_id
#     )

#     print("✅ AD CREATED")

#     return {
#         "campaign": campaign,
#         "creative": creative,
#         "adset": adset,
#         "ad": ad
#     }

@app.post("/create-ad")
async def create_ad_endpoint(
    request: Request,
    image: UploadFile = File(...),
):
    try:
        form = await request.form()

        campaign_name = form.get("campaign_name")
        message = form.get("message")
        whatsapp_number = form.get("whatsapp_number")

        print("\n==============================")
        print("🚀 FULL META FLOW STARTED")
        print("==============================")

        # SAVE IMAGE
        image_path = f"temp/{image.filename}"
        with open(image_path, "wb") as f:
            f.write(await image.read())

        # CAMPAIGN
        campaign = create_campaign(campaign_name)
        campaign_id = campaign["id"]
        print("✅ Campaign ID:", campaign_id)

        # IMAGE
        uploaded = upload_image(image_path)
        image_hash = list(uploaded["images"].values())[0]["hash"]
        print("✅ Image Hash:", image_hash)

        # CREATIVE
        creative = create_ad_creative(
            image_hash=image_hash,
            message=message,
            whatsapp_number=whatsapp_number,
        )
        creative_id = creative["id"]
        print("✅ Creative ID:", creative_id)

        # ADSET
        adset = create_adset(campaign_id)
        adset_id = adset["id"]
        print("✅ AdSet ID:", adset_id)

        # FINAL AD
        ad = create_ad(
            creative_id=creative_id,
            adset_id=adset_id,
        )
        print("✅ AD CREATED")

        return {
            "success": True,
            "campaign": campaign,
            "creative": creative,
            "adset": adset,
            "ad": ad,
        }

    except Exception as e:
        print("❌ CREATE AD ERROR:", str(e))
        return {
            "success": False,
            "error": str(e),
        }
    

@app.get("/debug-pages")
def debug_pages():

    import requests
    import os

    token = os.getenv("META_ACCESS_TOKEN")

    url = f"https://graph.facebook.com/v22.0/me/accounts?access_token={token}"

    response = requests.get(url)

    return response.json()

app.include_router(whatsapp_router)


# @app.post("/send-campaign")
# async def send_campaign(data: dict):

#     leads = data.get("leads", [])

#     for lead in leads:

#         send_template_message(
#             phone=lead["phone"],
#             customer_name=lead["name"]
#         )

#     return {
#         "status": "campaign sent",
#         "count": len(leads)
#     }

@app.post("/send-campaign")
async def send_campaign(data: dict):

    leads = data.get("leads", [])

    template_name = data.get(
        "template_name",
        "hello_world"
    )

    for lead in leads:

        send_template_message(
            phone=lead["phone"],
            customer_name=lead["name"],
            template_name=template_name
        )

    return {
        "status": "campaign sent",
        "count": len(leads)
    }

@app.get("/templates")
def templates():

    return get_templates()