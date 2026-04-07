import json
import base64
import asyncio
from fastapi import WebSocket

from app.stt_raw import DeepgramRaw
from app.llm import generate_reply
from app.tts import text_to_speech_stream

async def exotel_ws(websocket: WebSocket):
    await websocket.accept()

    dg = DeepgramRaw()
    loop = asyncio.get_running_loop()

    history = []
    user_buffer = []

    playback_task = None
    silence_timer = None

    FRAME_SIZE = 160
    FRAME_DELAY = 0.015  # faster than Twilio
    SILENCE_THRESHOLD = 0.25  # faster response

    async def send_audio(audio_bytes: bytes):
        await websocket.send_text(json.dumps({
            "event": "audio",
            "data": base64.b64encode(audio_bytes).decode()
        }))

    async def stream_reply(reply: str):
        def collect():
            return list(text_to_speech_stream(reply))

        chunks = await loop.run_in_executor(None, collect)

        buffer = b""
        for chunk in chunks:
            buffer += chunk

            while len(buffer) >= FRAME_SIZE:
                frame = buffer[:FRAME_SIZE]
                buffer = buffer[FRAME_SIZE:]

                await send_audio(frame)
                await asyncio.sleep(FRAME_DELAY)

    async def process():
        nonlocal user_buffer, playback_task

        if not user_buffer:
            return

        text = " ".join(user_buffer).strip()
        user_buffer = []

        if not text:
            return

        history.append(text)

        # 🔥 parallel LLM call
        reply = await loop.run_in_executor(None, generate_reply, history)
        history.append(reply)

        # 🔥 interrupt previous playback
        if playback_task and not playback_task.done():
            playback_task.cancel()

        playback_task = asyncio.create_task(stream_reply(reply))

    def on_transcript(text: str, raw: dict):
        nonlocal silence_timer, playback_task

        if not raw.get("is_final"):
            return

        user_buffer.append(text)

        # 🔥 interruption logic (no clear event)
        if playback_task and not playback_task.done():
            playback_task.cancel()

        if silence_timer:
            silence_timer.cancel()

        silence_timer = loop.create_task(wait())

    async def wait():
        try:
            await asyncio.sleep(SILENCE_THRESHOLD)
            await process()
        except asyncio.CancelledError:
            pass

    await dg.connect(on_transcript)

    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)

            event = data.get("event")

            if event == "start":
                print("📞 Exotel stream started")

            elif event == "media":
                audio = base64.b64decode(data["media"])
                await dg.send_audio(audio)

            elif event == "stop":
                break

    finally:
        await dg.close()