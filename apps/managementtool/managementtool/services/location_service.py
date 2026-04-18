from django.db.models import QuerySet

from managementtool.models import Location
from managementtool.repositories.location_repository import LocationRepository


class LocationService:
    def __init__(self, location_repository: LocationRepository):
        self.location_repository = location_repository

    def list_locations(self) -> QuerySet[Location]:
        return self.location_repository.get_all()
