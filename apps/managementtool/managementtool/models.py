from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=255)
    miserend_id = models.IntegerField(unique=True)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return self.name


class SIMCard(models.Model):
    iccid = models.CharField(max_length=22, unique=True)
    imsi = models.CharField(max_length=15, unique=True)
    end_date = models.DateField()
    remaining_volume = models.FloatField(help_text="Fennmaradó adatmennyiség MB-ban")

    class Meta:
        verbose_name = "SIM Card"
        verbose_name_plural = "SIM Cards"

    def __str__(self):
        return self.iccid


class Device(models.Model):
    imei = models.CharField(max_length=15, unique=True)
    location = models.ForeignKey(
        Location, on_delete=models.PROTECT, related_name="devices"
    )
    sim_card = models.OneToOneField(
        SIMCard, on_delete=models.PROTECT, related_name="device"
    )

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"

    def __str__(self):
        return self.imei


class DeviceUpdate(models.Model):
    TYPE1 = "type1"
    TYPE2 = "type2"
    DEVICE_TYPE_CHOICES = [
        (TYPE1, "Type1"),
        (TYPE2, "Type2"),
    ]

    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="updates"
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="updates"
    )
    timestamp = models.DateTimeField()
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE_CHOICES)

    # Type1 fields
    imei = models.CharField(max_length=15, null=True, blank=True)
    imsi = models.CharField(max_length=15, null=True, blank=True)
    version_product = models.IntegerField(null=True, blank=True)
    version_code = models.IntegerField(null=True, blank=True)
    battery = models.FloatField(null=True, blank=True, help_text="V (battery_mv / 1000)")
    signal = models.IntegerField(null=True, blank=True)
    interrupt_1 = models.IntegerField(null=True, blank=True)
    interrupt_2 = models.IntegerField(null=True, blank=True)
    interrupt_3 = models.IntegerField(null=True, blank=True)
    input_1 = models.IntegerField(null=True, blank=True)
    input_2 = models.IntegerField(null=True, blank=True)
    input_3 = models.IntegerField(null=True, blank=True)
    confession = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Device Update"
        verbose_name_plural = "Device Updates"

    def __str__(self):
        return f"{self.device} @ {self.timestamp}"
