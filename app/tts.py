# # app/tts.py
# from elevenlabs.client import ElevenLabs
# from app.config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

# client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# def text_to_speech(text: str) -> bytes:
#     """
#     Returns raw μ-law 8kHz bytes for Twilio Media Streams
#     """

#     audio_stream = client.text_to_speech.convert(
#         voice_id=ELEVENLABS_VOICE_ID,
#         model_id="eleven_turbo_v2_5",
#         text=text,
#         output_format="ulaw_8000",
#         voice_settings={
#         "stability": 0.35,           # 🔥 lower = more human
#         "similarity_boost": 0.55,    # keeps voice identity
#         "style": 0.65,               # adds emotion
#         "use_speaker_boost": True
#     }
#     )

#     audio_bytes = b""

#     for chunk in audio_stream:
#         if not chunk:
#             continue

#         # 🔥 CRITICAL FIX
#         if isinstance(chunk, str):
#             chunk = chunk.encode("utf-8")

#         audio_bytes += chunk

#     return audio_bytes

# app/tts.py
# from elevenlabs import VoiceSettings
# from elevenlabs.client import ElevenLabs
# from app.config import ELEVENLABS_API_KEY 
# # You can remove ELEVENLABS_VOICE_ID from imports if you hardcode it, 
# # or simply update its value in your .env / config file to "h0PQcMN6mspBJVBNyUcD"

# client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# def text_to_speech(text: str) -> bytes:
#     """
#     Generates high-quality Indian accent audio for Twilio.
#     """
#     audio_generator = client.text_to_speech.convert(
#         voice_id="Zjj2iX3aHYDcJSG4mMzk", # Your newly added voice ID
#         model_id="eleven_turbo_v2_5",    # Recommended model for speed and multilingual support
#         text=text,
#         output_format="ulaw_8000",       # Required format for Twilio telephony
#         voice_settings=VoiceSettings(    # Updated to use the VoiceSettings Pydantic object
#             stability=0.30, 
#             similarity_boost=0.80, 
#             style=0.70, 
#             use_speaker_boost=True
#         )
#     )

#     # Efficiently collect the generator into a single bytes object
#     return b"".join(list(audio_generator))

# def text_to_speech_stream(text: str):
#     """Returns a generator of audio chunks."""
#     return client.text_to_speech.convert(
#         voice_id="Zjj2iX3aHYDcJSG4mMzk",
#         model_id="eleven_turbo_v2_5",
#         text=text,
#         output_format="ulaw_8000",
#         voice_settings=VoiceSettings(
#             stability=0.30,
#             similarity_boost=0.80,
#             style=0.70,
#             use_speaker_boost=True
#         )
#     )


#STREAM SOLUTION

# app/tts.py
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from app.config import ELEVENLABS_API_KEY

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

VOICE_ID = "Zjj2iX3aHYDcJSG4mMzk"
MODEL_ID = "eleven_turbo_v2_5"
VOICE_SETTINGS = VoiceSettings(
    stability=0.30,
    similarity_boost=0.80,
    style=0.80,
    use_speaker_boost=True
)


def text_to_speech(text: str) -> bytes:
    audio_generator = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        text=text,
        output_format="ulaw_8000",
        voice_settings=VOICE_SETTINGS
    )

    chunks = []
    for chunk in audio_generator:
        if isinstance(chunk, bytes) and chunk:
            chunks.append(chunk)

    return b"".join(chunks)


def text_to_speech_stream(text: str):
    """
    SDK-safe pseudo-streaming using convert().
    Your installed SDK does not support .stream().
    """
    audio_generator = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        text=text,
        output_format="ulaw_8000",
        voice_settings=VOICE_SETTINGS
    )

    for chunk in audio_generator:
        if isinstance(chunk, bytes) and chunk:
            yield chunk
