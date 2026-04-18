from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("managementtool", "0002_rename_core_content_types"),
    ]

    operations = [
        migrations.AlterField(
            model_name="simcard",
            name="end_date",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="simcard",
            name="remaining_volume",
            field=models.FloatField(null=True, blank=True, help_text="Fennmaradó adatmennyiség MB-ban"),
        ),
        migrations.AddField(
            model_name="simcard",
            name="operator",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="simcard",
            name="country",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
    ]
