import logging
from datetime import date, datetime

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from dataingestion.cds import fetch_tcco

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-d', '--date', help='Date')

    def handle(self, *args, **kwargs):
        data_date = kwargs['date']

        # process layers
        logger.info(f"[INGEST COMMAND]: Starting Processing")

        if not data_date:
            data_date = date.today().strftime("%Y-%m-%d")
        else:
            try:
                data_date = datetime.strptime(data_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                raise CommandError(f"Incorrect date '{data_date}'. Expected Y-M-D")

        # fetch carbon monoxide forecast
        processed = fetch_tcco(data_date, to_float=True)

        if processed:
            call_command('gskyingest')
