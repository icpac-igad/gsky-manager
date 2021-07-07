import logging
from datetime import date

from django.core.management import call_command
from django.core.management.base import BaseCommand

from dataingestion.cds import fetch_tcco

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # process layers
        logger.info(f"[INGEST COMMAND]: Starting Processing")

        today = date.today().strftime("%Y-%m-%d")

        # fetch carbon monoxide forecast
        processed = fetch_tcco(today)

        if processed:
            call_command('gskyingest')
