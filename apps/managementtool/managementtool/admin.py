from django.contrib import admin, messages
from django.db.models import OuterRef, Subquery
from django.shortcuts import redirect
from django.urls import path

from managementtool.models import Device, DeviceUpdate, Location, SIMCard
from managementtool.repositories.one_nce_repository import OneNCERepository
from managementtool.services.one_nce_service import OneNCEService


class DeviceUpdateInline(admin.TabularInline):
    model = DeviceUpdate
    extra = 0
    can_delete = False
    show_change_link = True

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in DeviceUpdate._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "miserend_id"]
    inlines = [DeviceUpdateInline]


@admin.register(SIMCard)
class SIMCardAdmin(admin.ModelAdmin):
    list_display = ["iccid", "imsi", "operator", "country", "end_date", "remaining_volume"]
    change_list_template = "admin/managementtool/simcard/change_list.html"

    def get_urls(self):
        return [
            path("refresh/", self.admin_site.admin_view(self._refresh_view), name="simcard-refresh"),
        ] + super().get_urls()

    def _refresh_view(self, request):
        try:
            created, updated = OneNCEService(OneNCERepository()).refresh()
            messages.success(request, f"Refresh done: {created} created, {updated} updated.")
        except Exception as e:
            messages.error(request, f"Refresh failed: {e}")
        return redirect("../")


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ["imei", "location", "last_seen", "battery", "signal", "remaining_volume", "end_date"]
    list_select_related = ["location", "sim_card"]
    inlines = [DeviceUpdateInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        latest = DeviceUpdate.objects.filter(device=OuterRef("pk")).order_by("-timestamp")
        return qs.annotate(
            _last_seen=Subquery(latest.values("timestamp")[:1]),
            _last_battery=Subquery(latest.values("battery")[:1]),
            _last_signal=Subquery(latest.values("signal")[:1]),
        )

    @admin.display(description="Last seen", ordering="_last_seen")
    def last_seen(self, obj):
        return obj._last_seen

    @admin.display(description="Battery (V)", ordering="_last_battery")
    def battery(self, obj):
        return obj._last_battery

    @admin.display(description="Signal", ordering="_last_signal")
    def signal(self, obj):
        return obj._last_signal

    @admin.display(description="Remaining (MB)", ordering="sim_card__remaining_volume")
    def remaining_volume(self, obj):
        return obj.sim_card.remaining_volume

    @admin.display(description="SIM expires", ordering="sim_card__end_date")
    def end_date(self, obj):
        return obj.sim_card.end_date


@admin.register(DeviceUpdate)
class DeviceUpdateAdmin(admin.ModelAdmin):
    list_display = ["device", "location", "device_type", "timestamp", "battery", "signal", "confession"]
    list_filter = ["device_type", "location"]
    list_select_related = ["device", "location"]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in DeviceUpdate._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
