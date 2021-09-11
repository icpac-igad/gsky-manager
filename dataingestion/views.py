from django.http import HttpResponse

from django.core.management import call_command


def ingest_data(request):
    call_command('ingestlayers', '/data_source', "-s")
    return HttpResponse("COMMAND SENT")
