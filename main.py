import os
import uuid
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

try:
    from models import (
        TrackEventRequest,
        IdentifyRequest,
        DestinationConfig,
        EventResponse,
        StatsResponse,
        SignupRequest,
        SignupResponse,
    )
    from store import store
    from router import router
    from landing import render_comparison_page
except ImportError:
    from products.segmentlite.models import (
        TrackEventRequest,
        IdentifyRequest,
        DestinationConfig,
        EventResponse,
        StatsResponse,
        SignupRequest,
        SignupResponse,
    )
    from products.segmentlite.store import store
    from products.segmentlite.router import router
    from products.segmentlite.landing import render_comparison_page

app = FastAPI(
    title="SegmentLite API",
    description="High-throughput, unbundled event routing and webhook fan-out API for modern SaaS startups.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RAPIDAPI_SECRET = os.getenv("RAPIDAPI_PROXY_SECRET", "")
STANDALONE_KEY = os.getenv("SEGMENTLITE_API_KEY", "")

try:
    from config.settings import settings
    default_stripe = settings.stripe_link_segmentlite_pro
except Exception:
    default_stripe = ""

STRIPE_PRO_URL = (
    default_stripe
    or os.getenv("STRIPE_LINK_SEGMENTLITE_PRO")
    or os.getenv("STRIPE_SEGMENTLITE_PRO_URL")
    or "https://buy.stripe.com/test_segmentlite_pro"
)

def verify_auth(
    x_rapidapi_proxy_secret: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
):
    token = x_api_key
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()

    if token:
        if STANDALONE_KEY and token == STANDALONE_KEY:
            return True
        valid, msg, rec = store.verify_and_meter_key(token, units=1)
        if valid:
            return True
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=msg)

    if RAPIDAPI_SECRET and x_rapidapi_proxy_secret == RAPIDAPI_SECRET:
        return True

    if not RAPIDAPI_SECRET and not STANDALONE_KEY and not store.api_keys:
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid API key. Pass 'X-API-Key' header or register at /v1/auth/signup"
    )

@app.get("/", response_class=HTMLResponse, tags=["Public"])
async def root():
    return render_comparison_page(stripe_pro_url=STRIPE_PRO_URL)

@app.get("/health", tags=["Public"])
async def health_check():
    return {"status": "ok", "service": "SegmentLite API", "version": "1.0.0"}

@app.post("/v1/auth/signup", response_model=SignupResponse, tags=["Authentication & Billing"])
async def signup_developer(req: SignupRequest):
    if not req.email or "@" not in req.email:
        raise HTTPException(status_code=400, detail="Valid developer email required.")

    api_key, record = store.provision_api_key(req.email, plan="free")
    curl_snippet = (
        f'curl -X POST "https://segmentlite-api-dfru.fly.dev/v1/track" '
        f'-H "X-API-Key: {api_key}" '
        f'-H "Content-Type: application/json" '
        f'-d '{{"event": "User Signed Up", "user_id": "usr_dev_01", "properties": {{"plan": "starter"}}}}''
    )

    return SignupResponse(
        success=True,
        email=record["email"],
        api_key=api_key,
        plan=record["plan"],
        quota_limit=record["quota_limit"],
        quota_used=record["quota_used"],
        stripe_upgrade_url=STRIPE_PRO_URL,
        curl_example=curl_snippet
    )

@app.post("/v1/webhooks/stripe", tags=["Authentication & Billing"])
async def stripe_webhook(payload: dict):
    event_type = payload.get("type", "")
    data_object = payload.get("data", {}).get("object", {})
    if event_type in ("checkout.session.completed", "customer.subscription.created"):
        customer_email = data_object.get("customer_details", {}).get("email") or data_object.get("customer_email")
        if customer_email:
            upgraded = store.upgrade_key_to_pro(customer_email)
            return {"status": "upgraded", "email": customer_email, "success": upgraded}
    return {"status": "ignored", "type": event_type}

@app.post("/v1/track", response_model=EventResponse, tags=["Events"])
async def track_event(event_data: TrackEventRequest, authorized: bool = True):
    verify_auth()
    store.record_ingested(1)
    dispatched_count = await router.dispatch_track(event_data)
    return EventResponse(
        success=True,
        event_id=f"evt_{uuid.uuid4().hex[:12]}",
        destinations_queued=dispatched_count,
        message=f"Event '{event_data.event}' received and queued for {dispatched_count} destination(s)."
    )

@app.post("/v1/identify", response_model=EventResponse, tags=["Events"])
async def identify_user(identify_data: IdentifyRequest, authorized: bool = True):
    verify_auth()
    store.record_ingested(1)
    dispatched_count = await router.dispatch_identify(identify_data)
    return EventResponse(
        success=True,
        event_id=f"ide_{uuid.uuid4().hex[:12]}",
        destinations_queued=dispatched_count,
        message=f"Traits for user '{identify_data.user_id}' queued for {dispatched_count} destination(s)."
    )

@app.post("/v1/destinations", response_model=DestinationConfig, tags=["Destinations"])
async def add_destination(dest: DestinationConfig, authorized: bool = True):
    verify_auth()
    return store.add_destination(dest)

@app.get("/v1/destinations", response_model=List[DestinationConfig], tags=["Destinations"])
async def list_destinations(authorized: bool = True):
    verify_auth()
    return store.get_destinations()

@app.delete("/v1/destinations/{destination_id}", tags=["Destinations"])
async def remove_destination(destination_id: str, authorized: bool = True):
    verify_auth()
    deleted = store.delete_destination(destination_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Destination not found")
    return {"success": True, "message": f"Destination {destination_id} deleted"}

@app.get("/v1/stats", response_model=StatsResponse, tags=["Monitoring"])
async def get_stats():
    m = store.get_metrics()
    return StatsResponse(
        total_events_ingested=m["ingested"],
        total_events_forwarded=m["forwarded"],
        total_failures=m["failures"],
        active_destinations_count=m["active_destinations"],
        uptime_seconds=m["uptime_seconds"]
    )
