"""Deliver first-seen device alerts through the internal SMTP relay."""

import smtplib


def send_device_notification(message, host="mail-relay-01",
                             port=25, smtp_factory=None):
    """Return only after SMTP accepts every recipient."""
    if smtp_factory is None:
        smtp_factory = smtplib.SMTP

    with smtp_factory(host, port, timeout=15) as smtp:
        refused = smtp.send_message(message)

    if refused:
        raise smtplib.SMTPRecipientsRefused(refused)

    return True


def deliver_next_notification(collector_path, profiles_path, lock_path,
                              sender, recipient, smtp_factory=None,
                              now=None, host="mail-relay-01", port=25):
    """Process one outstanding first-seen alert under the worker lock."""
    import json
    import time
    from pathlib import Path
    from device_mailer import build_device_message
    from notification_state import (
        claim_first_notification, finish_notification, next_unsent_device,
    )
    from worker_lock import exclusive_worker_lock
    from worker_state import load_state

    with exclusive_worker_lock(lock_path):
        now = time.time() if now is None else now
        collector = json.loads(Path(collector_path).read_text())
        state = load_state(profiles_path)
        candidate = next_unsent_device(collector, state, now)

        if candidate is None:
            return None

        mac = candidate["mac"]
        if not claim_first_notification(
            collector_path, profiles_path, mac, now
        ):
            return None

        try:
            message = build_device_message(
                mac, candidate["device"], candidate["record"],
                sender, recipient
            )
            send_device_notification(
                message, host=host, port=port, smtp_factory=smtp_factory
            )
        except smtplib.SMTPRecipientsRefused as exc:
            finish_notification(
                profiles_path, mac, now, accepted=False,
                definitely_rejected=True, error=str(exc)
            )
            return {"mac": mac, "notification": "retry"}
        except Exception as exc:
            finish_notification(
                profiles_path, mac, now, accepted=False,
                error=f"{type(exc).__name__}: {exc}"
            )
            return {"mac": mac, "notification": "uncertain"}

        finish_notification(
            profiles_path, mac, now, accepted=True
        )
        return {"mac": mac, "notification": "sent"}
