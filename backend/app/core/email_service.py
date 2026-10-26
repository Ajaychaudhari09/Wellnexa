"""SMTP email sender. No health data in body."""
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from app.core.config import settings


def _cfg():
    return settings.model_dump(include={"SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "SMTP_USE_TLS", "EMAIL_SECURE", "EMAIL_FROM_NAME"})


def send_email(to: str, subject: str, body: str) -> bool:
    cfg = _cfg()
    msg = EmailMessage()
    msg["From"] = formataddr((cfg["EMAIL_FROM_NAME"], cfg["SMTP_FROM"]))
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        use_ssl = cfg["EMAIL_SECURE"] is True
        smtp_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
        with smtp_class(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=20) as server:
            use_starttls = not use_ssl and (
                cfg["SMTP_USE_TLS"] or cfg["EMAIL_SECURE"] is False or cfg["SMTP_PORT"] == 587
            )
            if use_starttls:
                if not server.has_extn("starttls"):
                    raise RuntimeError("Configured SMTP server does not offer STARTTLS")
                server.starttls()
            if cfg["SMTP_USER"]:
                server.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
            server.send_message(msg)
        return True
    except Exception:
        return False
