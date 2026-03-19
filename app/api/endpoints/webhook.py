from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.core.database import get_db
from app.models.shop import Shop
from app.models.user import User
from app.models.estimate import Estimate, AILog
from app.schemas.estimate import ExtractedEstimateData
from app.services.ai_extractor import extract_estimate_data
from app.services.pricing_engine import calculate_and_create_estimate
from app.services.pdf_generator import generate_pdf_from_estimate
from app.services.telegram_bot import send_message, send_document, get_file_path, download_file_bytes
from app.services.voice_processor import transcribe_voice

router = APIRouter()
logger = logging.getLogger(__name__)

async def process_telegram_update(update: dict, db: Session):
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        from_id = str(message["from"]["id"])
        
        user = db.query(User).filter(User.telegram_id == from_id).first()
        if not user:
            # Автоматическое создание автосервиса и пользователя
            new_shop = Shop(name=f"Shop_{from_id}", currency="USD", markup_percentage=0.0)
            db.add(new_shop)
            db.commit()
            db.refresh(new_shop)
            
            user = User(shop_id=new_shop.id, telegram_id=from_id, role="admin")
            db.add(user)
            db.commit()
            db.refresh(user)
            await send_message(chat_id, "Welcome! A new shop and profile have been created for you automatically.")

        text_content = ""
        
        if "text" in message:
            text_content = message["text"]
        elif "voice" in message:
            await send_message(chat_id, "Processing voice message...")
            file_id = message["voice"]["file_id"]
            file_path = await get_file_path(file_id)
            voice_bytes = await download_file_bytes(file_path)
            text_content = await transcribe_voice(voice_bytes)
            await send_message(chat_id, f"Transcribed text: {text_content}")
        else:
            await send_message(chat_id, "Send text or a voice message.")
            return

        if text_content:
            existing_log = db.query(AILog).filter(AILog.raw_input == text_content).first()
            if existing_log and existing_log.extracted_json:
                await send_message(chat_id, "Found similar previous request, reusing extracted data... Please wait.")
                extracted_data = ExtractedEstimateData.model_validate_json(existing_log.extracted_json)
            else:
                await send_message(chat_id, "Extracting data and calculating estimate... Please wait.")
                extracted_data = await extract_estimate_data(text_content)
            
            estimate = calculate_and_create_estimate(db, user.shop_id, user.id, extracted_data)
            
            # Save AI Log for this new estimate
            new_log = AILog(
                estimate_id=estimate.id,
                raw_input=text_content,
                extracted_json=extracted_data.model_dump_json() if hasattr(extracted_data, 'model_dump_json') else extracted_data.json()
            )
            db.add(new_log)
            db.commit()
            
            # Format display message
            display_text = f"<b>Estimate #{estimate.id} Created</b>\n"
            display_text += f"Vehicle: {estimate.car_year or ''} {estimate.car_make or ''} {estimate.car_model or ''}\n"
            display_text += f"\nGrand Total: {estimate.grand_total:.2f}\n"
            
            if estimate.status == "needs_confirmation":
                display_text += "\n⚠️ Some items require manual pricing review.\n"
                
            reply_markup = {
                "inline_keyboard": [
                    [{"text": "✅ Confirm Estimate", "callback_data": f"confirm_{estimate.id}"}],
                    [{"text": "🔄 Regenerate", "callback_data": f"regen_{estimate.id}"}]
                ]
            }
            
            await send_message(chat_id, display_text, reply_markup=reply_markup)

    elif "callback_query" in update:
        cb = update["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        data = cb["data"]
        
        if data.startswith("confirm_"):
            est_id = int(data.split("_")[1])
            estimate = db.query(Estimate).filter(Estimate.id == est_id).first()
            if estimate:
                estimate.status = "approved"
                db.commit()
                
                # Generate PDF
                await send_message(chat_id, "Generating PDF...")
                pdf_bytes = generate_pdf_from_estimate(estimate, estimate.shop)
                
                filename = f"Estimate_{estimate.id}.pdf"
                await send_document(chat_id, pdf_bytes, filename, caption=f"Here is your approved estimate #{estimate.id}")
        
        elif data.startswith("regen_"):
            est_id = int(data.split("_")[1])
            await send_message(chat_id, f"Estimate #{est_id} regenerated (Not fully implemented yet). Send new details to override.")


@router.post("/{token}")
async def telegram_webhook(token: str, request: Request, x_telegram_bot_api_secret_token: str = Header(None), db: Session = Depends(get_db)):
    if token != settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid path token")
        
    if x_telegram_bot_api_secret_token != settings.SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid secret token")
        
    try:
        update = await request.json()
        logger.info(f"Incoming Telegram update: {update}")
        await process_telegram_update(update, db)
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)
        # Don't crash webhook loop for telegram
    return {"status": "ok"}
