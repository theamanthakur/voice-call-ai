from deepgram import Deepgram
import asyncio
import json
import os

DEEPGRAM_API_KEY = "40dad36017064caf51d65254e4b649d121659071"

async def main():
    dg = Deepgram(DEEPGRAM_API_KEY)

    source = {
        "url": "https://static.deepgram.com/examples/Bueller-Life-moves-pretty-fast.wav"
    }

    response = await dg.transcription.prerecorded(
        source,
        {
            "model": "nova-2",
            "punctuate": True,
        },
    )

    print(json.dumps(response, indent=2))

asyncio.run(main())
