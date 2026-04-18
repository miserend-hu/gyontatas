import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.1nce.com/management-api"


class OneNCERepository:
    def __init__(self):
        self._client_id = os.environ["ONENECE_CLIENT_ID"]
        self._client_secret = os.environ["ONENECE_CLIENT_SECRET"]
        self._token: str | None = None

    def get_all_sims(self) -> list[dict]:
        url = f"{_BASE_URL}/v2/sims"
        result = []
        page = 0
        while True:
            headers = self._headers()
            logger.info("GET %s page=%s headers=%s", url, page, headers)
            resp = requests.get(url, headers=headers, params={"pageSize": 100, "pageNumber": page}, timeout=30)
            logger.info("GET %s %s response_headers=%s body=%s", url, resp.status_code, dict(resp.headers), resp.text)
            resp.raise_for_status()
            batch = resp.json()
            result.extend(batch)
            if len(batch) < 100:
                break
            page += 1
            time.sleep(0.5)
        return result

    def get_sim_quota(self, iccid: str) -> dict:
        resp = requests.get(
            f"{_BASE_URL}/v2/sims/{iccid}/quota/data",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def _headers(self) -> dict:
        if not self._token:
            self._authenticate()
        return {"Authorization": f"Bearer {self._token}", "Accept": "application/json"}

    def _authenticate(self) -> None:
        resp = requests.post(
            f"{_BASE_URL}/oauth/token",
            json={"grant_type": "client_credentials"},
            auth=(self._client_id, self._client_secret),
            timeout=10,
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
