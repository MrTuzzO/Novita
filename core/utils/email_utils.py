from threading import Thread

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def _send_email_task(subject, message, from_email, recipients, html_message=None, reply_to=None):
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipients,
            reply_to=reply_to or None,
        )
        if html_message:
            email.attach_alternative(html_message, 'text/html')
        email.send(fail_silently=True)
    except Exception:
        # Do not break user flows for email issues.
        return


def send_email_async(subject, message, recipient_list, html_message=None, from_email=None, reply_to=None):
    recipients = [email for email in (recipient_list or []) if email]
    if not recipients:
        return

    sender = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@novita.local')
    thread = Thread(
        target=_send_email_task,
        args=(subject, message, sender, recipients, html_message, reply_to),
        daemon=True,
    )
    thread.start()
