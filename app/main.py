# app/main.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import Response
from app.twilio_ws import twilio_ws
from app.twilio_call import call_number
from app.models import CallTranscript
from app.analyzer import analyze_call

app = FastAPI()

@app.post("/voice")
def voice():
    # We use <Connect> for a robust bi-directional stream
    twiml = """
<Response>
    <Connect>
        <Stream url="wss://agrostographic-congenital-brook.ngrok-free.dev/ws" />
    </Connect>
</Response>
    """
    return Response(content=twiml, media_type="application/xml")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await twilio_ws(websocket)

@app.post("/call")
def make_call(number: str):
    sid = call_number(number)
    return {"call_sid": sid}

@app.get("/")
def health():
    return {"status": "AI Voice Agent running"}

@app.post("/analyze-call")
async def analyze(data: CallTranscript):

    result = analyze_call(data.transcript)

    return {
        "call_sid": data.call_sid,
        "number": data.phone_number,
        "duration": data.duration,
        "analysis": result
    }