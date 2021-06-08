import hashlib
import hmac
import logging

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from dataingestion.utils import process_layers

logger = logging.getLogger(__name__)

GSKY_CONFIG = getattr(settings, 'GSKY_CONFIG', {})
WEBHOOK_SECRET = getattr(settings, 'WEBHOOK_SECRET')
GSKY_INGEST_WEBHOOK_URL = GSKY_CONFIG.get("GSKY_INGEST_WEBHOOK_URL")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('data_path', type=str, help='Path to data files')
        parser.add_argument('-s', '--skip', action='store_true', help='Skip existing')

    def handle(self, *args, **kwargs):
        data_path = kwargs['data_path']
        skip_existing = kwargs['skip']

        # process layers
        logger.info(f"[INGEST COMMAND]: Starting Processing")

        processed_some = process_layers(data_path, skip_existing)

        if processed_some and GSKY_INGEST_WEBHOOK_URL and WEBHOOK_SECRET:
            logger.info(f"[INGEST COMMAND]: sending gsky ingest command ")

            payload = {}
            request = requests.Request(
                'POST', GSKY_INGEST_WEBHOOK_URL,
                data=payload, headers={})

            prepped = request.prepare()
            signature = hmac.new(WEBHOOK_SECRET, prepped.body, digestmod=hashlib.sha512)
            prepped.headers['X-Gsky-Signature'] = signature.hexdigest()

            with requests.Session() as session:
                response = session.send(prepped)
                logger.info(response.text)
