import time
from datetime import datetime, timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs daily scheduled tasks (sim_card_refresh, device_update_purge)"

    def handle(self, *args, **options):
        self.stdout.write("Scheduler started.")
        while True:
            self._run_tasks()
            self._sleep_until_tomorrow()

    def _run_tasks(self):
        self.stdout.write(f"[{datetime.now().isoformat()}] Running scheduled tasks...")
        call_command("sim_card_refresh", stdout=self.stdout, stderr=self.stderr)
        call_command("device_update_purge", stdout=self.stdout, stderr=self.stderr)

    def _sleep_until_tomorrow(self):
        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds = (tomorrow - now).total_seconds()
        self.stdout.write(f"Next run at {tomorrow} (sleeping {seconds:.0f}s)")
        time.sleep(seconds)
