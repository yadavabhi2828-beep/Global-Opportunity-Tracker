import httpx
from loguru import logger
from app.config import settings

async def send_telegram_alert(chat_id: str, message: str):
    """Send text messages to Telegram chat group or channel."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.info(f"[Telegram Notification Mock] Chat: {chat_id} | Message: {message}")
        return
        
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            })
            res.raise_for_status()
            logger.info(f"Telegram alert successfully sent to chat {chat_id}.")
    except Exception as e:
        logger.error(f"Failed to post telegram alert: {e}")

async def notify_new_opportunities(chat_id: str, count: int):
    """Broadcast counts of newly scraped global items."""
    await send_telegram_alert(
        chat_id,
        f"🌐 *{count} new opportunities* discovered today!\n\nVisit your dashboard to explore them."
    )
