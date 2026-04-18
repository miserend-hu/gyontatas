from managementtool.models import SIMCard


class SIMCardRepository:
    def get_by_id(self, sim_card_id: int) -> SIMCard:
        return SIMCard.objects.get(pk=sim_card_id)

    def get_by_device(self, device_id: int) -> SIMCard:
        return SIMCard.objects.get(device__id=device_id)
