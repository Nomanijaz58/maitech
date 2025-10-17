from fastapi_mail import ConnectionConfig
from fastapi_mail import FastMail, MessageSchema, MessageType
from app.core.config import settings

mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,

    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_FROM=settings.MAIL_FROM
)
fm = FastMail(mail_conf)


async def send_html_mail(subject: str, html_str: str, recipients: list[str]):
    """
    Sends an HTML email to the given list of recipients.

    Parameters:
    - html_str: str — The HTML content of the email
    - subject: str — The subject of the email
    - recipients: list[str] — List of email addresses
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,  # noqa
        body=html_str,
        subtype=MessageType.html,
    )

    await fm.send_message(message)


async def send_text_mail(subject: str, body: str, recipients: list[str]):
    """
    Sends a plain text email to the given list of recipients.

    Parameters:
    - body: str — The plain text content of the email
    - subject: str — The subject of the email
    - recipients: list[str] — List of email addresses
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,  # noqa
        body=body,
        subtype=MessageType.plain,
    )

    await fm.send_message(message)