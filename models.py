from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TrackEventRequest(BaseModel):
    event: str = Field(..., description="Name of the event, e.g. 'Signed Up', 'Checkout Completed'")
    user_id: Optional[str] = Field(None, description="Unique identifier for the user in your database")
    anonymous_id: Optional[str] = Field(None, description="Anonymous session/device identifier")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Event metadata and parameters")
    context: Dict[str, Any] = Field(default_factory=dict, description="Device, IP, user-agent, or locale context")
    timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of event occurrence"
    )

class IdentifyRequest(BaseModel):
    user_id: str = Field(..., description="Unique user ID to associate traits with")
    traits: Dict[str, Any] = Field(default_factory=dict, description="User attributes e.g. email, name, company, plan")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual device/client data")
    timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

class DestinationConfig(BaseModel):
    id: Optional[str] = Field(None, description="Unique ID of destination, generated automatically if omitted")
    name: str = Field(..., description="Human-readable label, e.g. 'Production Mixpanel Webhook'")
    type: str = Field("webhook", description="Destination type: 'webhook', 'slack', or 'http_relay'")
    url: str = Field(..., description="Target webhook URL to forward events to")
    headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers e.g. Authorization")
    enabled: bool = Field(True, description="Whether this destination actively receives traffic")
    events_filter: Optional[List[str]] = Field(None, description="Optional whitelist of event names to forward. None forwards all.")

class EventResponse(BaseModel):
    success: bool
    event_id: str
    destinations_queued: int
    message: str

class StatsResponse(BaseModel):
    total_events_ingested: int
    total_events_forwarded: int
    total_failures: int
    active_destinations_count: int
    uptime_seconds: float

class SignupRequest(BaseModel):
    email: str = Field(..., description="Developer email address for API key provisioning")

class SignupResponse(BaseModel):
    success: bool
    email: str
    api_key: str
    plan: str
    quota_limit: int
    quota_used: int
    stripe_upgrade_url: str
    curl_example: str

