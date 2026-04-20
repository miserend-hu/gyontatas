import os
import time
from datetime import datetime, timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs daily scheduled tasks (sim_card_refresh, device_update_purge)"

    def handle(self, *args, **options):
        run_time = os.environ.get("SCHEDULER_RUN_TIME", "00:00")
        hour, minute = map(int, run_time.split(":"))
        self.stdout.write(f"Scheduler started. Daily run time: {run_time}")
        while True:
            self._run_tasks()
            self._sleep_until_next_run(hour, minute)

    def _run_tasks(self):
        self.stdout.write(f"[{datetime.now().isoformat()}] Running scheduled tasks...")
        call_command("sim_card_refresh", stdout=self.stdout, stderr=self.stderr)
        call_command("device_update_purge", stdout=self.stdout, stderr=self.stderr)

    def _sleep_until_next_run(self, hour, minute):
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        seconds = (next_run - now).total_seconds()
        self.stdout.write(f"Next run at {next_run} (sleeping {seconds:.0f}s)")
        time.sleep(seconds)
