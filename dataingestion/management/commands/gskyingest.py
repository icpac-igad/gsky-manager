import codecs
import hashlib
import hmac
import logging
import time

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

GSKY_CONFIG = getattr(settings, 'GSKY_CONFIG', {})
WEBHOOK_SECRET = getattr(settings, 'WEBHOOK_SECRET')
GSKY_INGEST_WEBHOOK_URL = GSKY_CONFIG.get("GSKY_INGEST_WEBHOOK_URL")


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        if GSKY_INGEST_WEBHOOK_URL and WEBHOOK_SECRET:
            logger.info(f"[INGEST COMMAND]: Sending gsky ingest command ")
            payload = {"now": time.time()}
            request = requests.Request(
                'POST', GSKY_INGEST_WEBHOOK_URL,
                data=payload, headers={})

            prepped = request.prepare()
            signature = hmac.new(codecs.encode(WEBHOOK_SECRET), prepped.body, digestmod=hashlib.sha256)
            prepped.headers['X-Gsky-Signature'] = signature.hexdigest()

            with requests.Session() as session:
                response = session.send(prepped)
                logger.info(response.text)
