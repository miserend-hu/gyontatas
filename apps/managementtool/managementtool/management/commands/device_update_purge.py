from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from managementtool.models import DeviceUpdate


class Command(BaseCommand):
    help = "Deletes DeviceUpdate records older than 1 year"

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=365)
        deleted, _ = DeviceUpdate.objects.filter(timestamp__lt=cutoff).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} DeviceUpdate records older than {cutoff.date()}."))
