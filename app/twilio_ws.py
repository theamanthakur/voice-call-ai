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

# from fastapi import WebSocket
# import json, base64, asyncio

# from app.stt_raw import DeepgramRaw
# from app.llm import generate_reply
# from app.tts import text_to_speech
# from app.analyzer import analyze_call
# from app.store import results_store
# from app.tts import text_to_speech_stream  # ← replace text_to_speech



# async def twilio_ws(websocket: WebSocket):

#     await websocket.accept()

#     dg = DeepgramRaw()

#     stream_sid: str | None = None
#     loop = asyncio.get_running_loop()

#     history: list[str] = []
#     transcript_log = []

#     user_speech_buffer = []
#     silence_timer: asyncio.Task | None = None

#     SILENCE_THRESHOLD = 0.4


#     async def send_audio(audio_bytes: bytes):

#         if not stream_sid or not audio_bytes:
#             return

#         await websocket.send_text(json.dumps({
#             "event": "media",
#             "streamSid": stream_sid,
#             "media": {
#                 "payload": base64.b64encode(audio_bytes).decode("utf-8")
#             }
#         }))


#     # async def process_user_input():

#     #     nonlocal user_speech_buffer

#     #     if not user_speech_buffer:
#     #         return

#     #     combined_text = " ".join(user_speech_buffer).strip()
#     #     user_speech_buffer = []

#     #     if not combined_text:
#     #         return

#     #     print(f"👤 User: {combined_text}")

#     #     history.append(combined_text)

#     #     transcript_log.append({
#     #         "speaker": "user",
#     #         "text": combined_text
#     #     })


#     #     reply = generate_reply(history)

#     #     print(f"🤖 Monika: {reply}")

#     #     history.append(reply)

#     #     transcript_log.append({
#     #         "speaker": "agent",
#     #         "text": reply
#     #     })


#     #     audio = text_to_speech(reply)

#     #     await send_audio(audio)
    
#     async def process_user_input(): nonlocal user_speech_buffer

#     if not user_speech_buffer:
#         return

#     combined_text = " ".join(user_speech_buffer).strip()
#     user_speech_buffer = []

#     if not combined_text:
#         return

#     print(f"👤 User: {combined_text}")
#     history.append(combined_text)
#     transcript_log.append({"speaker": "user", "text": combined_text})

#     # Non-blocking LLM call
#     reply = await loop.run_in_executor(None, generate_reply, history)

#     print(f"🤖 Ananya: {reply}")
#     history.append(reply)
#     transcript_log.append({"speaker": "agent", "text": reply})

#     # Stream TTS — collect in executor, send chunks as they arrive
#     def get_audio_chunks():
#         return list(text_to_speech_stream(reply))

#     chunks = await loop.run_in_executor(None, get_audio_chunks)

#     for chunk in chunks:
#         await send_audio(chunk)


#     def on_transcript(text: str, raw: dict):

#         nonlocal silence_timer

#         if stream_sid:
#             loop.create_task(websocket.send_text(json.dumps({
#                 "event": "clear",
#                 "streamSid": stream_sid
#             })))

#         if not raw.get("is_final"):
#             return

#         print(f"📝 Final: {text}")

#         user_speech_buffer.append(text)

#         if silence_timer:
#             silence_timer.cancel()

#         silence_timer = loop.create_task(wait_for_silence())


#     async def wait_for_silence():

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

#                 # welcome = "Namaste Sir! Main Monika bol rahi hoon SEAD Realty se."

#                 # history.append(welcome)

#                 # transcript_log.append({
#                 #     "speaker": "agent",
#                 #     "text": welcome
#                 # })

#                 # audio = text_to_speech(welcome)

#                 # await send_audio(audio)


#             elif data.get("event") == "media":

#                 await dg.send_audio(
#                     base64.b64decode(data["media"]["payload"])
#                 )


#             elif data.get("event") == "stop":

#                 print("📞 Call ended")

#                 break


#     except Exception as e:

#         print(f"❌ WS error: {e}")


#     finally:

#         await dg.close()

#         try:

#             full_transcript = "\n".join(
#                 [f"{x['speaker']}: {x['text']}" for x in transcript_log]
#             )

#             print("\n📜 Transcript\n", full_transcript)

#             # 🔥 CALL ANALYZER DIRECTLY
#             analysis = analyze_call(full_transcript)
#             results_store.append({
#     "number": phone_number,   # pass this into twilio_ws()
#     "analysis": analysis
# })

#             print("\n📊 AI Analysis\n", analysis)

#         except Exception as e:

#             print("⚠️ Analyzer error:", e)


# from fastapi import WebSocket
# import json
# import base64
# import asyncio

# from app.stt_raw import DeepgramRaw
# from app.llm import generate_reply
# from app.tts import text_to_speech_stream
# from app.analyzer import analyze_call


# async def twilio_ws(websocket: WebSocket, phone_number: str | None = None):
#     await websocket.accept()

#     dg = DeepgramRaw()
#     loop = asyncio.get_running_loop()

#     stream_sid: str | None = None
#     history: list[str] = []
#     transcript_log: list[dict] = []

#     user_speech_buffer: list[str] = []
#     silence_timer: asyncio.Task | None = None
#     playback_task: asyncio.Task | None = None

#     SILENCE_THRESHOLD = 0.3
#     FRAME_SIZE = 160
#     FRAME_DELAY = 0.02

#     async def send_audio(audio_bytes: bytes):
#         if not stream_sid or not audio_bytes:
#             return

#         await websocket.send_text(json.dumps({
#             "event": "media",
#             "streamSid": stream_sid,
#             "media": {
#                 "payload": base64.b64encode(audio_bytes).decode("utf-8")
#             }
#         }))

#     async def clear_audio():
#         if not stream_sid:
#             return

#         await websocket.send_text(json.dumps({
#             "event": "clear",
#             "streamSid": stream_sid
#         }))

#     async def stream_audio_to_twilio(reply: str):
#         def collect_chunks():
#             return list(text_to_speech_stream(reply))


#         chunks = await loop.run_in_executor(None, collect_chunks)

#         buffer = b""
#         for chunk in chunks:
#             if not isinstance(chunk, bytes) or not chunk:
#                 continue

#             buffer += chunk

#             while len(buffer) >= FRAME_SIZE:
#                 frame = buffer[:FRAME_SIZE]
#                 buffer = buffer[FRAME_SIZE:]
#                 await send_audio(frame)
#                 await asyncio.sleep(FRAME_DELAY)

#         if buffer:
#             if len(buffer) < FRAME_SIZE:
#                 buffer += b"\xff" * (FRAME_SIZE - len(buffer))
#             await send_audio(buffer)

#     async def process_user_input():
#         nonlocal user_speech_buffer, playback_task

#         if not user_speech_buffer:
#             return

#         combined_text = " ".join(user_speech_buffer).strip()
#         user_speech_buffer = []

#         if not combined_text:
#             return

#         print(f"👤 User: {combined_text}")
#         history.append(combined_text)
#         transcript_log.append({
#             "speaker": "user",
#             "text": combined_text
#         })

#         reply = await loop.run_in_executor(None, generate_reply, history)

#         print(f"🤖 Ananya: {reply}")
#         history.append(reply)
#         transcript_log.append({
#             "speaker": "agent",
#             "text": reply
#         })

#         if playback_task and not playback_task.done():
#             playback_task.cancel()
#             try:
#                 await playback_task
#             except asyncio.CancelledError:
#                 pass

#         playback_task = asyncio.create_task(stream_audio_to_twilio(reply))

#     def on_transcript(text: str, raw: dict):
#         nonlocal silence_timer, playback_task

#         if not raw.get("is_final"):
#             return

#         print(f"📝 Final: {text}")
#         user_speech_buffer.append(text)

#         if playback_task and not playback_task.done():
#             playback_task.cancel()
#             loop.create_task(clear_audio())

#         if silence_timer:
#             silence_timer.cancel()

#         silence_timer = loop.create_task(wait_for_silence())

#     async def wait_for_silence():
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
#             event = data.get("event")

#             if event == "start":
#                 stream_sid = data["start"]["streamSid"]
#                 call_sid = data["start"].get("callSid")
#             if call_sid and phone_number is None:
#                 from app.twilio_call import get_number_for_sid
#                 phone_number = get_number_for_sid(call_sid)
#                 print(f"📞 Stream started | SID: {stream_sid} | Number: {phone_number}")

#             elif event == "media":
#                 payload = data.get("media", {}).get("payload")
#                 if payload:
#                     await dg.send_audio(base64.b64decode(payload))

#             elif event == "stop":
#                 print("📞 Call ended")
#                 break

#     except Exception as e:
#         print(f"❌ WS error: {e}")

#     # finally:
#     #     if silence_timer and not silence_timer.done():
#     #         silence_timer.cancel()

#     #     if playback_task and not playback_task.done():
#     #         playback_task.cancel()
#     #         try:
#     #             await playback_task
#     #         except asyncio.CancelledError:
#     #             pass

#     #     await dg.close()

#     #     try:
#     #         full_transcript = "\n".join(
#     #             f"{x['speaker']}: {x['text']}" for x in transcript_log
#     #         )
#     #         print("\n📜 Transcript\n", full_transcript)

#     #         analysis = analyze_call(full_transcript)
#     #         print("\n📊 AI Analysis\n", analysis)

#     #         key = phone_number or stream_sid or f"call_{len(results_store) + 1}"
#     #         results_store[key] = {
#     #             "number": phone_number,
#     #             "stream_sid": stream_sid,
#     #             "transcript": full_transcript,
#     #             "analysis": analysis
#     #         }

#     #     except Exception as e:
#     #         print("⚠️ Analyzer error:", e)
#     finally:
#     # ... your existing cleanup code ...

#         await dg.close()

#     try:
#         full_transcript = "\n".join(
#             f"{x['speaker']}: {x['text']}" for x in transcript_log
#         )
#         print("\n📜 Transcript\n", full_transcript)

#         analysis_raw = analyze_call(full_transcript)
#         analysis = json.loads(analysis_raw)  # parse the JSON string

#         # Inject fields the LLM can't know
#         analysis["duration_seconds"] = len(transcript_log) * 15  # rough estimate
#         analysis["phone_number"] = phone_number
#         analysis["stream_sid"] = stream_sid

#         print("\n📊 Analysis\n", analysis)

#         from app.store import save_result
#         key = phone_number or stream_sid or f"call_{id(websocket)}"
#         save_result(key, {
#             "number": phone_number,
#             "stream_sid": stream_sid,
#             "transcript": full_transcript,
#             "analysis": analysis
#         })

#     except Exception as e:
#         print("⚠️ Analyzer error:", e)


# # app/twilio_ws.py
# from fastapi import WebSocket
# import json
# import base64
# import asyncio

# from app.stt_raw import DeepgramRaw
# from app.llm import generate_reply
# from app.tts import text_to_speech_stream
# from app.analyzer import analyze_call
# from app.store import save_result


# async def twilio_ws(websocket: WebSocket, phone_number: str | None = None):
#     await websocket.accept()

#     dg = DeepgramRaw()
#     loop = asyncio.get_running_loop()

#     stream_sid: str | None = None
#     history: list[str] = []
#     transcript_log: list[dict] = []

#     user_speech_buffer: list[str] = []
#     silence_timer: asyncio.Task | None = None
#     playback_task: asyncio.Task | None = None

#     SILENCE_THRESHOLD = 0.15
#     FRAME_SIZE = 160
#     FRAME_DELAY = 0.01

#     # ── Audio helpers ────────────────────────────────────────────────────────

#     async def send_audio(audio_bytes: bytes):
#         if not stream_sid or not audio_bytes:
#             return
#         await websocket.send_text(json.dumps({
#             "event": "media",
#             "streamSid": stream_sid,
#             "media": {"payload": base64.b64encode(audio_bytes).decode("utf-8")}
#         }))

#     async def clear_audio():
#         if not stream_sid:
#             return
#         await websocket.send_text(json.dumps({
#             "event": "clear",
#             "streamSid": stream_sid
#         }))
    
#     # async def stream_audio_to_twilio(reply: str):
#     #     try:
#     #         for chunk in text_to_speech_stream(reply):  # streaming, not list
#     #             if not isinstance(chunk, bytes) or not chunk:
#     #                 continue

#     #         await send_audio(chunk)

#     #     except Exception as e:
#     #         print("❌ TTS ERROR:", e)
#     #     return list(text_to_speech_stream(reply))

#     #     chunks = await loop.run_in_executor(None, collect_chunks)

#     #     buffer = b""
#     #     for chunk in chunks:
#     #         if not isinstance(chunk, bytes) or not chunk:
#     #             continue
#     #         buffer += chunk
#     #         while len(buffer) >= FRAME_SIZE:
#     #             frame = buffer[:FRAME_SIZE]
#     #             buffer = buffer[FRAME_SIZE:]
#     #             await send_audio(frame)
#     #             await asyncio.sleep(FRAME_DELAY)

#     #     if buffer:
#     #         buffer += b"\xff" * (FRAME_SIZE - len(buffer))
#     #         await send_audio(buffer)

#     # # ── STT / LLM pipeline ───────────────────────────────────────────────────
#     async def stream_audio_to_twilio(reply: str):
#         try:
#             buffer = b""

#             for chunk in text_to_speech_stream(reply):
#                 if not isinstance(chunk, bytes) or not chunk:
#                     continue

#                 buffer += chunk

#                 while len(buffer) >= FRAME_SIZE:
#                     frame = buffer[:FRAME_SIZE]
#                     buffer = buffer[FRAME_SIZE:]

#                     await send_audio(frame)
#                     await asyncio.sleep(FRAME_DELAY)

#             # flush remaining audio
#             if buffer:
#                 buffer += b"\xff" * (FRAME_SIZE - len(buffer))
#                 await send_audio(buffer)

#         except Exception as e:
#             print("❌ TTS ERROR:", e)
        
#     async def process_user_input():
#         nonlocal user_speech_buffer, playback_task

#         if not user_speech_buffer:
#             return

#         combined_text = " ".join(user_speech_buffer).strip()
#         user_speech_buffer = []

#         if not combined_text:
#             return

#         print(f"👤 User: {combined_text}")
#         history.append(combined_text)
#         transcript_log.append({"speaker": "user", "text": combined_text})

#         reply = await loop.run_in_executor(None, generate_reply, history)

#         print(f"🤖 Ananya: {reply}")
#         history.append(reply)
#         transcript_log.append({"speaker": "agent", "text": reply})

#         if playback_task and not playback_task.done():
#             playback_task.cancel()
#             try:
#                 await playback_task
#             except asyncio.CancelledError:
#                 pass

#         async def safe_stream():
#             try:
#                 await stream_audio_to_twilio(reply)
#             except Exception as e:
#                 print("❌ STREAM ERROR:", e)

#         playback_task = asyncio.create_task(safe_stream())

#     def on_transcript(text: str, raw: dict):
#         nonlocal silence_timer, playback_task

#         if not raw.get("is_final") and len(text.split()) < 3:
#             return

#         print(f"📝 Final: {text}")
#         user_speech_buffer.append(text)

#         if playback_task and not playback_task.done():
#             playback_task.cancel()
#             loop.create_task(clear_audio())

#         if silence_timer:
#             silence_timer.cancel()

#         silence_timer = loop.create_task(wait_for_silence())

#     async def wait_for_silence():
#         try:
#             await asyncio.sleep(SILENCE_THRESHOLD)
#             await process_user_input()
#         except asyncio.CancelledError:
#             pass

#     # ── Connect Deepgram ─────────────────────────────────────────────────────

#     await dg.connect(on_transcript)

#     # ── Main WebSocket loop ──────────────────────────────────────────────────

#     try:
#         while True:
#             msg = await websocket.receive_text()
#             data = json.loads(msg)
#             event = data.get("event")

#             if event == "start":
#                 stream_sid = data["start"]["streamSid"]
#                 call_sid = data["start"].get("callSid")
#                 # Resolve phone number from the sid→number map
#                 if call_sid and phone_number is None:
#                     from app.twilio_call import get_number_for_sid
#                     phone_number = get_number_for_sid(call_sid)
#                 print(f"📞 Stream started | SID: {stream_sid} | Number: {phone_number}")
#                 greeting = "नमस्ते सर! मैं Bansal Estate से बोल रही हूँ—Dwarka Mor में 3 BHK फ्लैट है, क्या अभी बात करना सही रहेगा?"
#                 history.append(greeting)
#                 transcript_log.append({"speaker": "agent", "text": greeting})
#                 asyncio.create_task(stream_audio_to_twilio(greeting))

#             elif event == "media":
#                 payload = data.get("media", {}).get("payload")
#                 if payload:
#                     await dg.send_audio(base64.b64decode(payload))

#             elif event == "stop":
#                 print("📞 Call ended")
#                 break

#     except Exception as e:
#         print(f"❌ WS error: {e}")

#     # ── Cleanup + Analysis ───────────────────────────────────────────────────

#     finally:
#         # Cancel pending tasks
#         if silence_timer and not silence_timer.done():
#             silence_timer.cancel()

#         if playback_task and not playback_task.done():
#             playback_task.cancel()
#             try:
#                 await playback_task
#             except asyncio.CancelledError:
#                 pass

#         await dg.close()

#         # Run post-call analysis and persist result
#         try:
#             if not transcript_log:
#                 print("⚠️ No transcript — skipping analysis")
#                 return

#             full_transcript = "\n".join(
#                 f"{x['speaker']}: {x['text']}" for x in transcript_log
#             )
#             print("\n📜 Transcript\n", full_transcript)

#             analysis_raw = analyze_call(full_transcript)
#             analysis = json.loads(analysis_raw)

#             # Inject fields the LLM can't know
#             analysis["duration_seconds"] = len(transcript_log) * 15
#             analysis["phone_number"] = phone_number
#             analysis["stream_sid"] = stream_sid

#             print("\n📊 Analysis\n", analysis)

#             key = phone_number or stream_sid or f"call_{id(websocket)}"
#             save_result(key, {
#                 "number": phone_number,
#                 "stream_sid": stream_sid,
#                 "transcript": full_transcript,
#                 "analysis": analysis
#             })

#         except Exception as e:
#             print(f"⚠️ Analyzer error: {e}")



# app/twilio_ws.py
from fastapi import WebSocket
import json
import base64
import asyncio

from app.stt_raw import DeepgramRaw
from app.llm import generate_reply
from app.tts import text_to_speech_stream
from app.analyzer import analyze_call
from app.store import save_result, set_call_active, set_call_inactive

SILENCE_THRESHOLD = 0.15
FRAME_SIZE = 160
FRAME_DELAY = 0.01


async def twilio_ws(websocket: WebSocket, phone_number: str | None = None):
    await websocket.accept()

    dg = DeepgramRaw()
    loop = asyncio.get_running_loop()

    stream_sid: str | None = None
    history: list[str] = []
    transcript_log: list[dict] = []

    user_speech_buffer: list[str] = []
    silence_timer: asyncio.Task | None = None
    playback_task: asyncio.Task | None = None

    # ── Audio helpers ────────────────────────────────────────────────────────

    async def send_audio(audio_bytes: bytes):
        if not stream_sid or not audio_bytes:
            return
        await websocket.send_text(json.dumps({
            "event": "media",
            "streamSid": stream_sid,
            "media": {"payload": base64.b64encode(audio_bytes).decode("utf-8")}
        }))

    async def clear_audio():
        if not stream_sid:
            return
        await websocket.send_text(json.dumps({
            "event": "clear",
            "streamSid": stream_sid
        }))

    async def stream_audio_to_twilio(reply: str):
        try:
            buffer = b""
            for chunk in text_to_speech_stream(reply):
                if not isinstance(chunk, bytes) or not chunk:
                    continue
                buffer += chunk
                while len(buffer) >= FRAME_SIZE:
                    frame = buffer[:FRAME_SIZE]
                    buffer = buffer[FRAME_SIZE:]
                    await send_audio(frame)
                    await asyncio.sleep(FRAME_DELAY)
            if buffer:
                buffer += b"\xff" * (FRAME_SIZE - len(buffer))
                await send_audio(buffer)
        except Exception as e:
            print("❌ TTS ERROR:", e)

    # ── STT / LLM pipeline ───────────────────────────────────────────────────

    async def process_user_input():
        nonlocal user_speech_buffer, playback_task

        if not user_speech_buffer:
            return

        combined_text = " ".join(user_speech_buffer).strip()
        user_speech_buffer = []

        if not combined_text:
            return

        print(f"👤 User: {combined_text}")
        history.append(combined_text)
        transcript_log.append({"speaker": "user", "text": combined_text})

        reply = await loop.run_in_executor(None, generate_reply, history)

        print(f"🤖 Ananya: {reply}")
        history.append(reply)
        transcript_log.append({"speaker": "agent", "text": reply})

        if playback_task and not playback_task.done():
            playback_task.cancel()
            try:
                await playback_task
            except asyncio.CancelledError:
                pass

        async def safe_stream():
            try:
                await stream_audio_to_twilio(reply)
            except Exception as e:
                print("❌ STREAM ERROR:", e)

        playback_task = asyncio.create_task(safe_stream())

    def on_transcript(text: str, raw: dict):
        nonlocal silence_timer, playback_task

        if not raw.get("is_final") and len(text.split()) < 3:
            return

        print(f"📝 Final: {text}")
        user_speech_buffer.append(text)

        if playback_task and not playback_task.done():
            playback_task.cancel()
            loop.create_task(clear_audio())

        if silence_timer:
            silence_timer.cancel()

        silence_timer = loop.create_task(wait_for_silence())

    async def wait_for_silence():
        try:
            await asyncio.sleep(SILENCE_THRESHOLD)
            await process_user_input()
        except asyncio.CancelledError:
            pass

    # ── Connect Deepgram ─────────────────────────────────────────────────────

    await dg.connect(on_transcript)

    # ── Main WebSocket loop ──────────────────────────────────────────────────

    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)
            event = data.get("event")

            if event == "start":
                stream_sid = data["start"]["streamSid"]
                call_sid = data["start"].get("callSid")

                if call_sid and phone_number is None:
                    from app.twilio_call import get_number_for_sid
                    phone_number = get_number_for_sid(call_sid)

                print(f"📞 Stream started | SID: {stream_sid} | Number: {phone_number}")

                # 🔒 Mark call as active — blocks /results from returning data
                key = phone_number or stream_sid or f"call_{id(websocket)}"
                set_call_active(key)

                greeting = "नमस्ते सर! मैं Bansal Estate से बोल रही हूँ—Dwarka Mor में 3 BHK फ्लैट है, क्या अभी बात करना सही रहेगा?"
                history.append(greeting)
                transcript_log.append({"speaker": "agent", "text": greeting})
                asyncio.create_task(stream_audio_to_twilio(greeting))

            elif event == "media":
                payload = data.get("media", {}).get("payload")
                if payload:
                    await dg.send_audio(base64.b64decode(payload))

            elif event == "stop":
                print("📞 Call ended")
                break

    except Exception as e:
        print(f"❌ WS error: {e}")

    # ── Cleanup + Analysis ───────────────────────────────────────────────────

    finally:
        if silence_timer and not silence_timer.done():
            silence_timer.cancel()

        if playback_task and not playback_task.done():
            playback_task.cancel()
            try:
                await playback_task
            except asyncio.CancelledError:
                pass

        await dg.close()

        try:
            if not transcript_log:
                print("⚠️ No transcript — skipping analysis")
                key = phone_number or stream_sid or f"call_{id(websocket)}"
                set_call_inactive(key)  # unblock even on empty transcript
                return

            full_transcript = "\n".join(
                f"{x['speaker']}: {x['text']}" for x in transcript_log
            )
            print("\n📜 Transcript\n", full_transcript)

            analysis_raw = analyze_call(full_transcript)
            analysis = json.loads(analysis_raw)

            analysis["duration_seconds"] = len(transcript_log) * 15
            analysis["phone_number"] = phone_number
            analysis["stream_sid"] = stream_sid

            print("\n📊 Analysis\n", analysis)

            key = phone_number or stream_sid or f"call_{id(websocket)}"

            save_result(key, {
                "number": phone_number,
                "stream_sid": stream_sid,
                "transcript": full_transcript,
                "analysis": analysis
            })

        except Exception as e:
            print(f"⚠️ Analyzer error: {e}")

        finally:
            # ✅ Always unblock /results AFTER save is complete
            key = phone_number or stream_sid or f"call_{id(websocket)}"
            set_call_inactive(key)