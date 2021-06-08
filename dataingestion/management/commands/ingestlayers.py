import logging

from django.core.management.base import BaseCommand

from dataingestion.utils import process_layers

from django.core.management import call_command

logger = logging.getLogger(__name__)


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

        if processed_some:
            call_command('gskyingest')
