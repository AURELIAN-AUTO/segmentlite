"""SegmentLite Python Client SDK.

Lightweight, zero-dependency drop-in client for SegmentLite.
"""

import json
import urllib.request
from typing import Any, Dict, List, Optional


class SegmentLite:
    """SegmentLite API Client."""

    def __init__(self, api_key: str, host: str = "https://segmentlite-api-dfru.fly.dev"):
        self.api_key = api_key
        self.host = host.rstrip("/")

    def track(
        self,
        event: str,
        user_id: Optional[str] = None,
        anonymous_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Ingests a track event and fans it out to configured destinations."""
        payload = {
            "event": event,
            "user_id": user_id,
            "anonymous_id": anonymous_id,
            "properties": properties or {},
            "context": context or {},
        }
        return self._request("/v1/track", payload)

    def identify(
        self,
        user_id: str,
        traits: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Associates user traits across destinations."""
        payload = {
            "user_id": user_id,
            "traits": traits or {},
            "context": context or {},
        }
        return self._request("/v1/identify", payload)

    def add_destination(
        self,
        name: str,
        url: str,
        dest_type: str = "webhook",
        headers: Optional[Dict[str, str]] = None,
        events_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Registers a new webhook fan-out destination."""
        payload = {
            "name": name,
            "type": dest_type,
            "url": url,
            "headers": headers or {},
            "events_filter": events_filter,
            "enabled": True,
        }
        return self._request("/v1/destinations", payload)

    def list_destinations(self) -> List[Dict[str, Any]]:
        """Lists all configured fan-out destinations."""
        return self._request("/v1/destinations", method="GET")

    def get_stats(self) -> Dict[str, Any]:
        """Retrieves event throughput and delivery metrics."""
        return self._request("/v1/stats", method="GET")

    def _request(self, endpoint: str, payload: Optional[dict] = None, method: str = "POST") -> Any:
        url = f"{self.host}{endpoint}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        req.add_header("X-API-Key", self.api_key)
        req.add_header("User-Agent", "SegmentLite-Python/1.0.0")

        with urllib.request.urlopen(req, timeout=10.0) as resp:
            return json.loads(resp.read().decode("utf-8"))
