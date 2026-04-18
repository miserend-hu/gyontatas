from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=255)
    miserend_id = models.IntegerField(unique=True)

    class Meta:
        verbose_name = "Helyszín"
        verbose_name_plural = "Helyszínek"

    def __str__(self):
        return self.name


class SIMCard(models.Model):
    iccid = models.CharField(max_length=22, unique=True)
    imsi = models.CharField(max_length=15, unique=True)
    end_date = models.DateField()
    remaining_volume = models.FloatField(help_text="Fennmaradó adatmennyiség MB-ban")

    class Meta:
        verbose_name = "SIM kártya"
        verbose_name_plural = "SIM kártyák"

    def __str__(self):
        return self.iccid


class Device(models.Model):
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=50, unique=True)
    location = models.ForeignKey(
        Location, on_delete=models.PROTECT, related_name="devices"
    )
    sim_card = models.OneToOneField(
        SIMCard, on_delete=models.PROTECT, related_name="device"
    )

    class Meta:
        verbose_name = "Eszköz"
        verbose_name_plural = "Eszközök"

    def __str__(self):
        return self.name


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
    battery = models.IntegerField(null=True, blank=True, help_text="mV")
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
        verbose_name = "Eszköz frissítés"
        verbose_name_plural = "Eszköz frissítések"

    def __str__(self):
        return f"{self.device} @ {self.timestamp}"
