from django.core.management.base import BaseCommand
from scraper.scripts import run_scraper


class Command(BaseCommand):
    help = "Run the scraper to fetch and store app and comment data."

    def handle(self, *args, **kwargs):
        run_scraper()
