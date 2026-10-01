"""Official Python client for ChinaCarAPI: Chinese used-car data (Dongchedi and Che168)."""
from __future__ import annotations

import os
from typing import Any, Dict, Iterable, Optional

import requests

__all__ = ["ChinaCarAPI", "ChinaCarAPIError", "MissingApiKeyError"]

DEFAULT_BASE_URL = "https://api.chinacarapi.com"
SIGNUP_URL = "https://chinacarapi.com"


class ChinaCarAPIError(Exception):
    """Raised when ChinaCarAPI returns an error response."""

    def __init__(self, message: str, status: Optional[int] = None, body: Optional[str] = None) -> None:
        super().__init__(message)
        self.status = status
        self.body = body


class MissingApiKeyError(ChinaCarAPIError):
    """Raised when no API key is provided."""


class ChinaCarAPI:
    """Client for ChinaCarAPI, the Chinese used-car data API (Dongchedi + Che168, in English).

    A ChinaCarAPI key is **required** (EnCarAPI keys with the China add-on work too).
    Get one (5-day trial available) at https://chinacarapi.com. The data is not free.

        from chinacarapi import ChinaCarAPI

        client = ChinaCarAPI("YOUR_API_KEY")   # or set CHINACARAPI_KEY in the environment
        cars = client.catalog(make="BYD", export_ready=True, limit=25)
        car = client.vehicle(cars["results"][0]["id"])
    """

    def __init__(self, api_key: Optional[str] = None, *, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0) -> None:
        api_key = api_key or os.environ.get("CHINACARAPI_KEY")
        if not api_key:
            raise MissingApiKeyError(
                "A ChinaCarAPI key is required. Pass it as ChinaCarAPI('YOUR_KEY') or set the "
                f"CHINACARAPI_KEY environment variable. Get a key at {SIGNUP_URL}"
            )
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"x-api-key": api_key, "Accept": "application/json"})

    # -- low level -------------------------------------------------------
    @staticmethod
    def _clean(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not params:
            return None
        out = {}
        for k, v in params.items():
            if v is None:
                continue
            out[k] = ("true" if v else "false") if isinstance(v, bool) else v
        return out

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, json: Any = None, text: bool = False) -> Any:
        resp = self._session.request(method, f"{self.base_url}{path}", params=self._clean(params), json=json, timeout=self.timeout)
        if resp.status_code in (401, 403):
            raise ChinaCarAPIError(
                f"ChinaCarAPI rejected the request ({resp.status_code}). Check your key or plan at {SIGNUP_URL}. Body: {resp.text[:300]}",
                resp.status_code, resp.text,
            )
        if not resp.ok:
            raise ChinaCarAPIError(f"ChinaCarAPI error {resp.status_code}: {resp.text[:300]}", resp.status_code, resp.text)
        return resp.text if text else resp.json()

    # -- endpoints -------------------------------------------------------
    def catalog(self, **params: Any) -> Any:
        """Search the catalog. Filters: source, duplicates, make, model, year_min/max,
        reg_year_min/max, price_min/max (CNY), mileage_max, city, fuel, has_report,
        export_ready, updated_since, sort, page, limit, lang ('zh' = original Chinese)."""
        return self._request("GET", "/api/catalog", params)

    def vehicle(self, vehicle_id: str, **params: Any) -> Any:
        """Full record for one car (price history, photos, seller, export status, alsoListedOn)."""
        return self._request("GET", f"/api/vehicle/{vehicle_id}", params)

    def inspection(self, vehicle_id: str, **params: Any) -> Any:
        """Inspection report: accident, flood and fire checks, battery data for EVs."""
        return self._request("GET", f"/api/inspection/{vehicle_id}", params)

    def bulk(self, ids: Iterable[str], **params: Any) -> Any:
        """Up to 500 full records in one call (Business and Scale plans, trial)."""
        return self._request("POST", "/api/vehicle/bulk", params, json={"ids": list(ids)})

    def changes(self, **params: Any) -> Any:
        """Change feed: call with since=ISO timestamp once, then cursor=nextCursor."""
        return self._request("GET", "/api/catalog/changes", params)

    def export_csv(self) -> str:
        """Full catalog as CSV text (Business and Scale plans)."""
        return self._request("GET", "/api/catalog/export", text=True)

    def enums(self, **params: Any) -> Any:
        """Filter values with counts: makes, fuels, cities, sources, sorts."""
        return self._request("GET", "/api/enums", params)

    def models(self, make: str) -> Any:
        """Models of one make (id or English name) with counts."""
        return self._request("GET", "/api/models", {"make": make})
