import yaml
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from managementtool.models import Device, Location, SIMCard

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database from a YAML file"

    def add_arguments(self, parser):
        parser.add_argument(
            "yaml_file",
            nargs="?",
            default="seed.yml",
            help="Path to the YAML seed file (default: seed.yml)",
        )

    def handle(self, *args, **options):
        path = options["yaml_file"]
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            raise CommandError(f"Seed file not found: {path}")

        self._seed_users(data.get("users", []))
        self._seed_locations(data.get("locations", []))
        self._seed_sim_cards(data.get("sim_cards", []))
        self._seed_devices(data.get("devices", []))

    def _seed_users(self, users):
        for entry in users:
            user, created = User.objects.get_or_create(username=entry["username"])
            user.set_password(entry["password"])
            user.is_superuser = entry.get("is_superuser", False)
            user.is_staff = entry.get("is_staff", False)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"{'Created' if created else 'Updated'} user: {user.username}")
            )

    def _seed_locations(self, locations):
        for entry in locations:
            location, created = Location.objects.update_or_create(
                miserend_id=entry["miserend_id"],
                defaults={"name": entry["name"]},
            )
            self.stdout.write(
                self.style.SUCCESS(f"{'Created' if created else 'Updated'} location: {location.name}")
            )

    def _seed_sim_cards(self, sim_cards):
        for entry in sim_cards:
            sim_card, created = SIMCard.objects.update_or_create(
                iccid=entry["iccid"],
                defaults={
                    "imsi": entry["imsi"],
                    "end_date": entry["end_date"],
                    "remaining_volume": entry["remaining_volume"],
                },
            )
            self.stdout.write(
                self.style.SUCCESS(f"{'Created' if created else 'Updated'} SIM card: {sim_card.iccid}")
            )

    def _seed_devices(self, devices):
        for entry in devices:
            try:
                location = Location.objects.get(miserend_id=entry["location_miserend_id"])
            except Location.DoesNotExist:
                raise CommandError(
                    f"Location with miserend_id={entry['location_miserend_id']} not found. "
                    "Make sure locations are seeded first."
                )
            try:
                sim_card = SIMCard.objects.get(iccid=entry["sim_card_iccid"])
            except SIMCard.DoesNotExist:
                raise CommandError(
                    f"SIMCard with iccid={entry['sim_card_iccid']} not found. "
                    "Make sure sim_cards are seeded first."
                )
            device, created = Device.objects.update_or_create(
                imei=entry["imei"],
                defaults={
                    "location": location,
                    "sim_card": sim_card,
                },
            )
            self.stdout.write(
                self.style.SUCCESS(f"{'Created' if created else 'Updated'} device: {device.imei}")
            )
