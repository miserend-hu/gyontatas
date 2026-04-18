from django.core.management.base import BaseCommand

from managementtool.repositories.one_nce_repository import OneNCERepository
from managementtool.services.one_nce_service import OneNCEService


class Command(BaseCommand):
    help = "Refreshes SIM card data from 1NCE API"

    def handle(self, *args, **options):
        created, updated = OneNCEService(OneNCERepository()).refresh()
        self.stdout.write(self.style.SUCCESS(f"Done: {created} created, {updated} updated."))
