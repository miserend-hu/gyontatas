from django.db import migrations


def rename_content_types(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    db_alias = schema_editor.connection.alias
    for model_name in ("location", "simcard", "device", "deviceupdate"):
        ContentType.objects.using(db_alias).filter(
            app_label="core", model=model_name
        ).update(app_label="managementtool")


class Migration(migrations.Migration):
    dependencies = [
        ("managementtool", "0001_initial"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(rename_content_types, migrations.RunPython.noop),
    ]
