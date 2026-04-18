import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("miserend_id", models.IntegerField(unique=True)),
            ],
            options={
                "verbose_name": "Helyszín",
                "verbose_name_plural": "Helyszínek",
            },
        ),
        migrations.CreateModel(
            name="SIMCard",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("iccid", models.CharField(max_length=22, unique=True)),
                ("imsi", models.CharField(max_length=15, unique=True)),
                ("end_date", models.DateField()),
                ("remaining_volume", models.FloatField(help_text="Fennmaradó adatmennyiség MB-ban")),
            ],
            options={
                "verbose_name": "SIM kártya",
                "verbose_name_plural": "SIM kártyák",
            },
        ),
        migrations.CreateModel(
            name="Device",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("serial_number", models.CharField(max_length=50, unique=True)),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="devices",
                        to="core.location",
                    ),
                ),
                (
                    "sim_card",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="device",
                        to="core.simcard",
                    ),
                ),
            ],
            options={
                "verbose_name": "Eszköz",
                "verbose_name_plural": "Eszközök",
            },
        ),
        migrations.CreateModel(
            name="DeviceUpdate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("timestamp", models.DateTimeField()),
                (
                    "device_type",
                    models.CharField(
                        choices=[("type1", "Type1"), ("type2", "Type2")],
                        max_length=10,
                    ),
                ),
                ("imei", models.CharField(blank=True, max_length=15, null=True)),
                ("imsi", models.CharField(blank=True, max_length=15, null=True)),
                ("version_product", models.IntegerField(blank=True, null=True)),
                ("version_code", models.IntegerField(blank=True, null=True)),
                ("battery", models.IntegerField(blank=True, help_text="mV", null=True)),
                ("signal", models.IntegerField(blank=True, null=True)),
                ("interrupt_1", models.IntegerField(blank=True, null=True)),
                ("interrupt_2", models.IntegerField(blank=True, null=True)),
                ("interrupt_3", models.IntegerField(blank=True, null=True)),
                ("input_1", models.IntegerField(blank=True, null=True)),
                ("input_2", models.IntegerField(blank=True, null=True)),
                ("input_3", models.IntegerField(blank=True, null=True)),
                ("confession", models.IntegerField(blank=True, null=True)),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="updates",
                        to="core.device",
                    ),
                ),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="updates",
                        to="core.location",
                    ),
                ),
            ],
            options={
                "verbose_name": "Eszköz frissítés",
                "verbose_name_plural": "Eszköz frissítések",
                "ordering": ["-timestamp"],
            },
        ),
    ]
