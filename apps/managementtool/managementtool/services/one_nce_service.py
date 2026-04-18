import logging
from datetime import date

from managementtool.models import SIMCard
from managementtool.repositories.one_nce_repository import OneNCERepository

logger = logging.getLogger(__name__)


class OneNCEService:
    def __init__(self, repository: OneNCERepository):
        self.repository = repository

    def refresh(self) -> tuple[int, int]:
        """Syncs SIM cards from 1NCE. Returns (created, updated)."""
        all_sims = self.repository.get_all_sims()
        sims_by_iccid = {s["iccid"]: s for s in all_sims}

        known_iccids = set(SIMCard.objects.values_list("iccid", flat=True))
        created = 0
        for iccid, sim in sims_by_iccid.items():
            if iccid not in known_iccids:
                imsi = sim.get("current_imsi") or sim.get("imsi", "")
                SIMCard.objects.create(iccid=iccid, imsi=imsi)
                logger.info("Created SIMCard for ICCID %s", iccid)
                created += 1

        updated = 0
        for sim_card in SIMCard.objects.all():
            try:
                self._update_sim_card(sim_card, sims_by_iccid.get(sim_card.iccid, {}))
                updated += 1
            except Exception:
                logger.exception("Failed to update SIMCard %s", sim_card.iccid)

        return created, updated

    def _update_sim_card(self, sim_card: SIMCard, sim_data: dict) -> None:
        quota = self.repository.get_sim_quota(sim_card.iccid)

        sim_card.imsi = sim_data.get("current_imsi") or sim_data.get("imsi") or sim_card.imsi
        sim_card.remaining_volume = quota.get("volume")
        sim_card.end_date = _parse_date(quota.get("expiry_date"))
        sim_card.save()


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None
