import httpx
from app.core.config import settings

API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}"

async def send_message(chat_id: int, text: str, reply_markup: dict = None):
    async with httpx.AsyncClient() as client:
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if reply_markup:
            payload["reply_markup"] = reply_markup
            
        response = await client.post(f"{API_URL}/sendMessage", json=payload)
        response.raise_for_status()
        return response.json()

async def send_document(chat_id: int, document_bytes: bytes, filename: str, caption: str = None):
    async with httpx.AsyncClient() as client:
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
            
        files = {"document": (filename, document_bytes, "application/pdf")}
        response = await client.post(f"{API_URL}/sendDocument", data=data, files=files)
        response.raise_for_status()
        return response.json()

async def get_file_path(file_id: str) -> str:
    """Gets the path of a file from Telegram servers."""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/getFile", json={"file_id": file_id})
        response.raise_for_status()
        data = response.json()
        if data.get("ok"):
            return data["result"]["file_path"]
        raise ValueError("Failed to get file path from Telegram")

async def download_file_bytes(file_path: str) -> bytes:
    """Downloads previously identified file from Telegram servers."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FILE_URL}/{file_path}")
        response.raise_for_status()
        return response.content
