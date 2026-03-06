from pydantic import BaseModel

class CallTranscript(BaseModel):
    call_sid: str
    phone_number: str
    duration: int
    transcript: str
