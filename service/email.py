import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_password_reset_email(
        recipient: str,
        reset_link: str
    ) -> None:
    message = EmailMessage()
    message["Subject"] = "Password Reset"
    message["From"] = SMTP_USERNAME
    message["To"] = recipient
    message.set_content(
        f"""
        A password reset has been requested for your account.

        Click the link below to reset your password:

        {reset_link}

        This link will expire in 30 minutes.

        If you did not request a password reset, then you can ignore this email.
        """
    )
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(message)