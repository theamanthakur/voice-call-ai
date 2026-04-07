import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM_NUMBER = "+15857284367" 
EXOTEL_SID = "codeintelailabs1"
EXOTEL_TOKEN = "5c2ccc7dbe40de00c829b009e6523907db6f1075c888401f"
EXOTEL_NUMBER = "09513886363"

missing = []

if not OPENAI_API_KEY:
    missing.append("OPENAI_API_KEY")
if not ELEVENLABS_API_KEY:
    missing.append("ELEVENLABS_API_KEY")
if not ELEVENLABS_VOICE_ID:
    missing.append("ELEVENLABS_VOICE_ID")
if not DEEPGRAM_API_KEY:
    missing.append("DEEPGRAM_API_KEY")

if missing:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
