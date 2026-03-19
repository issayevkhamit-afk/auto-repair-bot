import tempfile
import os
from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def transcribe_voice(voice_bytes: bytes) -> str:
    """
    Takes voice bytes (e.g. OGG file from Telegram), saves to a temporary file,
    and uses OpenAI Whisper to transcribe to text.
    """
    # Create a temporary file to hold the bytes since Whisper requires file-like object with name
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp.write(voice_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio_file:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="text"
            )
            return transcript
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
