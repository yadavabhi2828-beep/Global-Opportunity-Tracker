import sendgrid
from sendgrid.helpers.mail import Mail
from loguru import logger
from app.config import settings

sg = None
if settings.SENDGRID_API_KEY:
    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize SendGrid client: {e}")

async def send_deadline_reminder(user_email: str, opportunity_name: str, deadline: str):
    """Sends a deadline reminder email via SendGrid or fallbacks to console logging."""
    if not sg:
        logger.info(f"[Email Notification Mock] To: {user_email} | Subject: Deadline Reminder: {opportunity_name} | Deadline: {deadline}")
        return
        
    try:
        message = Mail(
            from_email="noreply@globalopportunitytracker.com",
            to_emails=user_email,
            subject=f"⏰ Deadline Reminder: {opportunity_name}",
            html_content=f"""
                <h2>Don't miss your opportunity!</h2>
                <p><strong>{opportunity_name}</strong> closes on <strong>{deadline}</strong>.</p>
                <p>Visit your tracker board to view details and notes.</p>
                <a href="http://localhost:3001/tracker">Go to Application Board →</a>
            """
        )
        response = sg.send(message)
        logger.info(f"Email reminder sent to {user_email}. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send email via SendGrid: {e}")
