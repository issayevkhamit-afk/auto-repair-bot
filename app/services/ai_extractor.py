import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.estimate import ExtractedEstimateData

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def extract_estimate_data(text_input: str) -> ExtractedEstimateData:
    """
    Extracts structured data from mechanic notes using OpenAI's structured outputs.
    """
    system_prompt = (
        "You are an expert automotive assistant. Extract the car make, car model, "
        "car year, labor items, part items, and any general notes from the text."
    )
    
    response = await client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text_input}
        ],
        response_format=ExtractedEstimateData,
    )
    
    return response.choices[0].message.parsed
