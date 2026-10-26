from app.core import email_service


def test_gmail_submission_uses_starttls_before_authentication(monkeypatch):
    events = []

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            events.append(("connect", host, port, timeout))

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def has_extn(self, name):
            return name == "starttls"

        def starttls(self):
            events.append(("starttls",))

        def login(self, username, password):
            events.append(("login", username, password))

        def send_message(self, message):
            events.append(("send", message["To"], message["Subject"]))

    monkeypatch.setattr(email_service, "_cfg", lambda: {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": 587,
        "SMTP_USER": "sender@example.com",
        "SMTP_PASSWORD": "test-only-password",
        "SMTP_FROM": "sender@example.com",
        "SMTP_USE_TLS": False,
        "EMAIL_SECURE": False,
        "EMAIL_FROM_NAME": "Test Support",
    })
    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

    assert email_service.send_email("recipient@example.com", "Test subject", "Test body") is True
    assert [event[0] for event in events] == ["connect", "starttls", "login", "send"]


def test_email_auth_is_blocked_if_starttls_is_missing(monkeypatch):
    events = []

    class FakeSMTP:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def has_extn(self, _name):
            return False

        def login(self, *_args):
            events.append("login")

    monkeypatch.setattr(email_service, "_cfg", lambda: {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": 587,
        "SMTP_USER": "sender@example.com",
        "SMTP_PASSWORD": "test-only-password",
        "SMTP_FROM": "sender@example.com",
        "SMTP_USE_TLS": False,
        "EMAIL_SECURE": False,
        "EMAIL_FROM_NAME": "Test Support",
    })
    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

    assert email_service.send_email("recipient@example.com", "Test subject", "Test body") is False
    assert "login" not in events
