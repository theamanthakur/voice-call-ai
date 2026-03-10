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
from fastapi.middleware.cors import CORSMiddleware
from app.twilio_ws import twilio_ws
from app.twilio_call import call_number
from app.models import CallTranscript
from app.analyzer import analyze_call
from app.store import get_all_results
import asyncio


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RAILWAY_URL = "web-production-c0d66.up.railway.app"
# RAILWAY_URL = "https://agrostographic-congenital-brook.ngrok-free.dev"



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
        n.strip().replace(" ", "")
        for n in numbers_text.split("\n")
        if n.strip()
    ]

    tasks = [asyncio.to_thread(call_number, number) for number in numbers]
    await asyncio.gather(*tasks)

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