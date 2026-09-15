import asyncio
import logging
from typing import Any, Dict, Optional
import httpx

try:
    from models import DestinationConfig, TrackEventRequest, IdentifyRequest
    from store import store
except ImportError:
    from products.segmentlite.models import DestinationConfig, TrackEventRequest, IdentifyRequest
    from products.segmentlite.store import store

logger = logging.getLogger("segmentlite.router")

class EventRouter:
    """High-throughput async event fan-out engine."""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=6.0)
        return self._client

    async def dispatch_track(self, event_data: TrackEventRequest) -> int:
        destinations = store.get_destinations(enabled_only=True)
        eligible = []
        for dest in destinations:
            if dest.events_filter and event_data.event not in dest.events_filter:
                continue
            eligible.append(dest)

        if not eligible:
            return 0

        for dest in eligible:
            asyncio.create_task(self._forward_to_destination(dest, event_data.model_dump()))

        return len(eligible)

    async def dispatch_identify(self, identify_data: IdentifyRequest) -> int:
        destinations = store.get_destinations(enabled_only=True)
        if not destinations:
            return 0

        for dest in destinations:
            asyncio.create_task(self._forward_to_destination(dest, identify_data.model_dump()))

        return len(destinations)

    async def _forward_to_destination(self, dest: DestinationConfig, payload: Dict[str, Any]):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SegmentLite-Forwarder/1.0",
            **dest.headers
        }
        envelope = {
            "source": "segmentlite",
            "destination_id": dest.id,
            "destination_name": dest.name,
            **payload
        }
        try:
            client = await self.get_client()
            resp = await client.post(dest.url, json=envelope, headers=headers)
            if resp.status_code in (200, 201, 202, 204):
                store.record_forwarded(1)
            else:
                logger.warning(f"Destination '{dest.name}' returned status {resp.status_code}")
                store.record_failure()
        except Exception as e:
            logger.debug(f"Failed delivery to '{dest.name}': {e}")
            store.record_failure()

router = EventRouter()
