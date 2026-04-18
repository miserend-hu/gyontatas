from django.db.models import QuerySet

from managementtool.models import Location


class LocationRepository:
    def get_all(self) -> QuerySet[Location]:
        return Location.objects.all()

    def get_by_id(self, location_id: int) -> Location:
        return Location.objects.get(pk=location_id)
