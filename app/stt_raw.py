# app/stt_raw.py
import asyncio
import json
from typing import Callable, Optional

import websockets
from websockets.legacy.client import WebSocketClientProtocol
from app.config import DEEPGRAM_API_KEY

# ===== CONFIG =====
# DEEPGRAM_MODEL = "nova-3"   # nova-3 or nova-2
# LANGUAGE = "hi"
# SAMPLE_RATE = 8000          # Twilio μ-law default
# CONTENT_TYPE = f"audio/mulaw;rate={SAMPLE_RATE}"
DEEPGRAM_MODEL = "nova-2"   # faster than nova-3
LANGUAGE = "hi-IN"          # better locale handling
SAMPLE_RATE = 8000
CONTENT_TYPE = f"audio/mulaw;rate={SAMPLE_RATE}"

class DeepgramRaw:
    def __init__(self):
        self.ws: Optional[WebSocketClientProtocol] = None
        self.recv_task: Optional[asyncio.Task] = None

    async def connect(self, on_transcript: Callable[[str, dict], None]):
        # params = (
        #     f"model={DEEPGRAM_MODEL}"
        #     f"&language={LANGUAGE}"
        #     f"&punctuate=true"
        #     f"&encoding=mulaw"           
        #      f"&sample_rate={SAMPLE_RATE}"
        #     f"&interim_results=true"
        #     f"&endpointing=100"
        # )
        params = (
            f"model=nova-2"
            f"&encoding=mulaw"
            f"&sample_rate=8000"
            f"&interim_results=true"
            f"&endpointing=100"
        )
        uri = f"wss://api.deepgram.com/v1/listen?{params}"

        headers = [
            ("Authorization", f"Token {DEEPGRAM_API_KEY}"),
            ("Content-Type", CONTENT_TYPE),
        ]

        self.ws = await websockets.connect(uri, additional_headers=headers)
        print("✅ Deepgram RAW websocket connected")

        self.recv_task = asyncio.create_task(
            self._recv_loop(on_transcript)
        )

    async def _recv_loop(self, on_transcript):
        try:
            async for msg in self.ws:
                if not msg:
                    continue

                try:
                    data = json.loads(msg)
                except Exception:
                    continue

                # Primary transcript path
                if "channel" in data:
                    alts = data["channel"].get("alternatives", [])
                    if alts:
                        text = alts[0].get("transcript", "")
                        if text.strip():
                            on_transcript(text, data)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print("❌ Deepgram recv error:", e)

    async def send_audio(self, audio: bytes):
        if not self.ws:
            return
        await self.ws.send(audio)  # binary μ-law frames

    async def close(self):
        if self.recv_task:
            self.recv_task.cancel()
            try:
                await self.recv_task
            except Exception:
                pass

        if self.ws:
            await self.ws.close()

        print("✅ Deepgram RAW websocket closed")
