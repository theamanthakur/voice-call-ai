# # app/twilio_ws.py
# from fastapi import WebSocket
# import json, base64, asyncio
# from app.stt_raw import DeepgramRaw
# from app.llm import generate_reply
# from app.tts import text_to_speech

# async def twilio_ws(websocket: WebSocket):
#     await websocket.accept()
#     dg = DeepgramRaw()
#     history: list[str] = []
#     stream_sid: str | None = None
#     loop = asyncio.get_running_loop()

#     # --- BUFFER LOGIC ---
#     user_speech_buffer = []
#     silence_timer: asyncio.Task | None = None
#     SILENCE_THRESHOLD = .4 # Seconds to wait after user stops speaking

#     async def send_audio(audio_bytes: bytes):
#         if not stream_sid or not audio_bytes: return
#         await websocket.send_text(json.dumps({
#             "event": "media",
#             "streamSid": stream_sid,
#             "media": {"payload": base64.b64encode(audio_bytes).decode("utf-8")}
#         }))

#     async def process_user_input():
#         """Aggregates buffer and triggers LLM once"""
#         nonlocal user_speech_buffer
#         if not user_speech_buffer: return

#         combined_text = " ".join(user_speech_buffer).strip()
#         user_speech_buffer = [] # Clear buffer
        
#         if not combined_text: return

#         print(f"👤 Guest (Final): {combined_text}")
#         history.append(combined_text)

#         # Get one single response
#         reply = generate_reply(history)
#         print(f"🤖 Monika: {reply}")
#         history.append(reply)

#         audio = text_to_speech(reply)
#         await send_audio(audio)

#     def on_transcript(text: str, raw: dict):
#         nonlocal silence_timer
        
#         # 1. Clear any pending "clear" events if user interrupts
#         # (This stops the AI if it was already speaking)
#         if stream_sid:
#             loop.create_task(websocket.send_text(json.dumps({
#                 "event": "clear", "streamSid": stream_sid
#             })))

#         if not raw.get("is_final"):
#             return

#         # 2. Add transcript to buffer
#         print(f"📝 Part: {text}")
#         user_speech_buffer.append(text)

#         # 3. Reset the "Silence Timer"
#         # If the user speaks again within 1.2s, the old timer is cancelled
#         if silence_timer:
#             silence_timer.cancel()
        
#         silence_timer = loop.create_task(wait_for_silence())

#     async def wait_for_silence():
#         """Waits for a pause before processing the full buffer"""
#         try:
#             await asyncio.sleep(SILENCE_THRESHOLD)
#             await process_user_input()
#         except asyncio.CancelledError:
#             pass

#     await dg.connect(on_transcript)

#     try:
#         while True:
#             msg = await websocket.receive_text()
#             data = json.loads(msg)
            
#             if data.get("event") == "start":
#                 stream_sid = data["start"]["streamSid"]
#                 welcome = (
#                     "Namaste Sir! Kya meri baat Aman se ho rahi hai... "
#                 )

#                 history.append(welcome)
#                 audio = text_to_speech(welcome)
#                 await send_audio(audio)

#             elif data.get("event") == "media":
#                 await dg.send_audio(base64.b64decode(data["media"]["payload"]))

#             elif data.get("event") == "stop": break
#     except Exception as e: print(f"❌ WS error: {e}")
#     finally: await dg.close()

from fastapi import WebSocket
import json, base64, asyncio

from app.stt_raw import DeepgramRaw
from app.llm import generate_reply
from app.tts import text_to_speech
from app.analyzer import analyze_call


async def twilio_ws(websocket: WebSocket):

    await websocket.accept()

    dg = DeepgramRaw()

    stream_sid: str | None = None
    loop = asyncio.get_running_loop()

    history: list[str] = []
    transcript_log = []

    user_speech_buffer = []
    silence_timer: asyncio.Task | None = None

    SILENCE_THRESHOLD = 0.4


    async def send_audio(audio_bytes: bytes):

        if not stream_sid or not audio_bytes:
            return

        await websocket.send_text(json.dumps({
            "event": "media",
            "streamSid": stream_sid,
            "media": {
                "payload": base64.b64encode(audio_bytes).decode("utf-8")
            }
        }))


    async def process_user_input():

        nonlocal user_speech_buffer

        if not user_speech_buffer:
            return

        combined_text = " ".join(user_speech_buffer).strip()
        user_speech_buffer = []

        if not combined_text:
            return

        print(f"👤 User: {combined_text}")

        history.append(combined_text)

        transcript_log.append({
            "speaker": "user",
            "text": combined_text
        })


        reply = generate_reply(history)

        print(f"🤖 Monika: {reply}")

        history.append(reply)

        transcript_log.append({
            "speaker": "agent",
            "text": reply
        })


        audio = text_to_speech(reply)

        await send_audio(audio)


    def on_transcript(text: str, raw: dict):

        nonlocal silence_timer

        if stream_sid:
            loop.create_task(websocket.send_text(json.dumps({
                "event": "clear",
                "streamSid": stream_sid
            })))

        if not raw.get("is_final"):
            return

        print(f"📝 Final: {text}")

        user_speech_buffer.append(text)

        if silence_timer:
            silence_timer.cancel()

        silence_timer = loop.create_task(wait_for_silence())


    async def wait_for_silence():

        try:
            await asyncio.sleep(SILENCE_THRESHOLD)
            await process_user_input()

        except asyncio.CancelledError:
            pass


    await dg.connect(on_transcript)


    try:

        while True:

            msg = await websocket.receive_text()
            data = json.loads(msg)

            if data.get("event") == "start":

                stream_sid = data["start"]["streamSid"]

                # welcome = "Namaste Sir! Main Monika bol rahi hoon SEAD Realty se."

                # history.append(welcome)

                # transcript_log.append({
                #     "speaker": "agent",
                #     "text": welcome
                # })

                # audio = text_to_speech(welcome)

                # await send_audio(audio)


            elif data.get("event") == "media":

                await dg.send_audio(
                    base64.b64decode(data["media"]["payload"])
                )


            elif data.get("event") == "stop":

                print("📞 Call ended")

                break


    except Exception as e:

        print(f"❌ WS error: {e}")


    finally:

        await dg.close()

        try:

            full_transcript = "\n".join(
                [f"{x['speaker']}: {x['text']}" for x in transcript_log]
            )

            print("\n📜 Transcript\n", full_transcript)

            # 🔥 CALL ANALYZER DIRECTLY
            analysis = analyze_call(full_transcript)

            print("\n📊 AI Analysis\n", analysis)

        except Exception as e:

            print("⚠️ Analyzer error:", e)