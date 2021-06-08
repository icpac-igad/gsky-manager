import hashlib
import hmac

from django.conf import settings

WEBHOOK_SECRET = getattr(settings, 'WEBHOOK_SECRET')


def generate_hmac_signature(request_body):
    if WEBHOOK_SECRET:
        signature = hmac.new(WEBHOOK_SECRET, request_body.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        return signature
    return None
