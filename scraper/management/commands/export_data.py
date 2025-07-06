from django.core.management.base import BaseCommand
from scraper.exporters import run_exporter

class Command(BaseCommand):
    help = "Export app, comment, and User data to an Excel file."

    def handle(self, *args, **kwargs):
        run_exporter()
