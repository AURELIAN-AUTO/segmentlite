import hashlib
import json
import logging
import os
import secrets
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import uuid

try:
    from models import DestinationConfig
except ImportError:
    from products.segmentlite.models import DestinationConfig

logger = logging.getLogger("segmentlite.store")

class SegmentLiteStore:
    """Lightweight persistent storage for destination configs, API keys, and metrics."""

    def __init__(self, data_file: Optional[Path] = None):
        if data_file:
            self.data_file = data_file
        else:
            base_dir = Path(os.getenv("DATA_DIR", "./data"))
            self.data_file = base_dir / "segmentlite_store.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.start_time = time.time()
        self.destinations: Dict[str, DestinationConfig] = {}
        self.metrics = {"ingested": 0, "forwarded": 0, "failures": 0}
        self.api_keys: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.data_file.exists():
            try:
                raw = json.loads(self.data_file.read_text(encoding="utf-8"))
                self.destinations = {
                    d["id"]: DestinationConfig(**d) for d in raw.get("destinations", [])
                }
                self.metrics = raw.get("metrics", {
                    "ingested": 0,
                    "forwarded": 0,
                    "failures": 0
                })
                self.api_keys = raw.get("api_keys", {})
                return
            except Exception as e:
                logger.error(f"Error loading segmentlite store: {e}")

        self.destinations = {}
        self.metrics = {"ingested": 0, "forwarded": 0, "failures": 0}
        self.api_keys = {}

    def _save(self):
        try:
            payload = {
                "destinations": [d.model_dump() for d in self.destinations.values()],
                "metrics": self.metrics,
                "api_keys": self.api_keys
            }
            self.data_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Error saving segmentlite store: {e}")

    def add_destination(self, dest: DestinationConfig) -> DestinationConfig:
        if not dest.id:
            dest.id = f"dst_{secrets.token_hex(6)}"
        self.destinations[dest.id] = dest
        self._save()
        return dest

    def get_destinations(self, enabled_only: bool = False) -> List[DestinationConfig]:
        if enabled_only:
            return [d for d in self.destinations.values() if d.enabled]
        return list(self.destinations.values())

    def get_destination(self, dest_id: str) -> Optional[DestinationConfig]:
        return self.destinations.get(dest_id)

    def delete_destination(self, dest_id: str) -> bool:
        if dest_id in self.destinations:
            del self.destinations[dest_id]
            self._save()
            return True
        return False

    def record_ingested(self, count: int = 1):
        self.metrics["ingested"] = self.metrics.get("ingested", 0) + count
        self._save()

    def record_forwarded(self, count: int = 1):
        self.metrics["forwarded"] = self.metrics.get("forwarded", 0) + count
        self._save()

    def record_failure(self, count: int = 1):
        self.metrics["failures"] = self.metrics.get("failures", 0) + count
        self._save()

    def get_metrics(self) -> dict:
        return {
            **self.metrics,
            "active_destinations": len([d for d in self.destinations.values() if d.enabled]),
            "uptime_seconds": round(time.time() - self.start_time, 2)
        }

    def provision_api_key(self, email: str, plan: str = "free") -> Tuple[str, dict]:
        clean_email = email.strip().lower()
        for k, v in self.api_keys.items():
            if v.get("email") == clean_email:
                return k, v

        api_key = f"sgl_live_{secrets.token_hex(16)}"
        quota = 1000 if plan == "free" else 100000
        record = {
            "key": api_key,
            "email": clean_email,
            "plan": plan,
            "created_at": time.time(),
            "quota_limit": quota,
            "quota_used": 0,
            "status": "active"
        }
        self.api_keys[api_key] = record
        self._save()
        return api_key, record

    def verify_and_meter_key(self, api_key: str, units: int = 1) -> Tuple[bool, str, Optional[dict]]:
        if not api_key:
            return False, "Missing API key", None
        record = self.api_keys.get(api_key)
        if not record:
            if api_key.startswith("sgl_live_"):
                record = {
                    "key": api_key,
                    "email": "auto_migrated@segmentlite.dev",
                    "plan": "free",
                    "created_at": time.time(),
                    "quota_limit": 1000,
                    "quota_used": 0,
                    "status": "active"
                }
                self.api_keys[api_key] = record
                self._save()
            else:
                return False, "Invalid API key", None

        if record.get("status") != "active":
            return False, "API key suspended or revoked", record

        limit = record.get("quota_limit", 1000)
        used = record.get("quota_used", 0)
        if used + units > limit:
            return False, f"Monthly quota exceeded ({used}/{limit}). Upgrade to Pro at https://segmentlite-api-dfru.fly.dev", record

        record["quota_used"] = used + units
        self._save()
        return True, "Authorized", record

    def upgrade_key_to_pro(self, email_or_key: str) -> bool:
        for k, v in self.api_keys.items():
            if k == email_or_key or v.get("email") == email_or_key.strip().lower():
                v["plan"] = "pro"
                v["quota_limit"] = 100000
                self._save()
                return True
        return False

store = SegmentLiteStore()
