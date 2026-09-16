import os
import uuid
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import HTMLResponse

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

# Optional RapidAPI / API Key Security Dependency
RAPIDAPI_SECRET = os.getenv("RAPIDAPI_PROXY_SECRET", "")
STANDALONE_KEY = os.getenv("SEGMENTLITE_API_KEY", "")

from config.settings import settings
STRIPE_PRO_URL = settings.stripe_link_segmentlite_pro or os.getenv("STRIPE_LINK_SEGMENTLITE_PRO") or os.getenv("STRIPE_SEGMENTLITE_PRO_URL") or "https://buy.stripe.com/test_segmentlite_pro"

def verify_auth(
    x_rapidapi_proxy_secret: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
):
    """Enforces authentication and meters usage against store and billing engine."""
    token = x_api_key
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()

    if token:
        if STANDALONE_KEY and token == STANDALONE_KEY:
            return True
        # Check store first
        valid, msg, rec = store.verify_and_meter_key(token, units=1)
        if valid:
            return True
        if "Quota exceeded" in msg:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=msg)

        # Check core.billing engine
        try:
            from core.billing import billing
            allowed, reason = billing.check_and_increment_quota(token, units=1)
            if allowed:
                return True
            if "Quota exceeded" in reason:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=reason)
        except Exception:
            pass

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    if RAPIDAPI_SECRET and x_rapidapi_proxy_secret == RAPIDAPI_SECRET:
        return True
    if not RAPIDAPI_SECRET and not STANDALONE_KEY:
        # Development / open sandbox mode
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized. Missing or invalid X-RapidAPI-Proxy-Secret or X-API-Key.",
    )

@app.get("/", response_class=HTMLResponse, tags=["Web"])
async def index_page():
    """Inbound comparison and developer landing page."""
    return render_comparison_page(stripe_pro_url=STRIPE_PRO_URL)

@app.get("/compare/segment", response_class=HTMLResponse, tags=["Web"])
async def compare_segment_page():
    """SEO comparison page: Twilio Segment vs SegmentLite."""
    return render_comparison_page(stripe_pro_url=STRIPE_PRO_URL)

@app.get("/health", tags=["System"])
@app.get("/v1/health", tags=["System"])
async def health_check():
    """Uptime and health check monitor."""
    return {"status": "healthy", "service": "SegmentLite API", "version": "1.0.0"}

@app.get("/privacy", response_class=HTMLResponse, tags=["Web"])
async def privacy_policy_page():
    """Privacy policy page."""
    return HTMLResponse("""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <title>Privacy Policy - SegmentLite</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-200 font-sans p-8 max-w-4xl mx-auto leading-relaxed">
  <h1 class="text-3xl font-extrabold text-white mb-6">SegmentLite Privacy Policy</h1>
  <p class="text-xs text-slate-400 mb-8">Last Updated: September 16, 2026</p>
  
  <h2 class="text-xl font-bold text-white mb-3">1. Data Ownership & Protection</h2>
  <p class="mb-6 text-slate-300">SegmentLite does not sell, rent, monetize, or train AI models on customer event data. All telemetry ingested via <code>/v1/track</code> and <code>/v1/identify</code> is routed directly to your configured webhook endpoints in memory.</p>

  <h2 class="text-xl font-bold text-white mb-3">2. Ingestion & Retention</h2>
  <p class="mb-6 text-slate-300">Transient event logs are held only long enough to confirm successful HTTP 200 delivery to your destinations. Ephemeral delivery logs are retained for delivery metrics and debugging, then pruned.</p>

  <h2 class="text-xl font-bold text-white mb-3">3. Developer Contact</h2>
  <p class="mb-8 text-slate-300">For privacy inquiries or account deletion, email <a href="mailto:aurelian.dfru@gmail.com" class="text-sky-400 underline">aurelian.dfru@gmail.com</a>.</p>
  
  <p><a href="/" class="text-sky-400 hover:text-sky-300 underline text-sm">← Back to SegmentLite</a></p>
</body>
</html>""")

@app.post("/v1/auth/signup", response_model=SignupResponse, tags=["Auth"])
async def signup_for_api_key(req: SignupRequest):
    """Generates an instant free developer API key (1,000 free events/month)."""
    if not req.email or "@" not in req.email:
        raise HTTPException(status_code=400, detail="A valid developer email is required.")

    clean_email = req.email.strip().lower()
    key_data = store.create_api_key(clean_email, plan_id="free")
    raw_key = key_data["raw_key"]
    try:
        from core.billing import billing
        billing.generate_api_key(clean_email, "segmentlite_free")
    except Exception:
        pass

    curl_ex = (
        f'curl -X POST "https://segmentlite-api-dfru.fly.dev/v1/track" \\\n'
        f'  -H "Content-Type: application/json" \\\n'
        f'  -H "X-API-Key: {raw_key}" \\\n'
        f'  -d \'{{"event": "User Signed Up", "user_id": "usr_1001", "properties": {{"plan": "Pro"}}}}\''
    )
    return SignupResponse(
        success=True,
        email=clean_email,
        api_key=raw_key,
        plan="free",
        quota_limit=key_data["quota_limit"],
        quota_used=key_data["quota_used"],
        stripe_upgrade_url=STRIPE_PRO_URL,
        curl_example=curl_ex,
    )

@app.post("/v1/billing/webhook", tags=["Billing"])
async def billing_webhook(payload: dict):
    """Handles Stripe checkout and subscription upgrade webhooks."""
    event_type = payload.get("type") or payload.get("event") or "checkout.session.completed"
    email = (
        payload.get("customer_email") or
        payload.get("email") or
        payload.get("data", {}).get("object", {}).get("customer_details", {}).get("email") or
        payload.get("data", {}).get("object", {}).get("email")
    )
    if not email:
        return {"status": "ignored", "reason": "No customer email found in webhook payload"}

    store.upgrade_to_pro(email)
    try:
        from core.billing import billing
        billing.handle_webhook_event("checkout.session.completed", {"customer_email": email, "plan_id": "segmentlite_pro", "amount_paid": 19.0})
    except Exception:
        pass

    return {
        "status": "success",
        "event": event_type,
        "email": email,
        "plan": "pro",
        "quota_limit": 1000000,
    }

@app.post("/v1/track", response_model=EventResponse, tags=["Events"])
async def track_event(
    event: TrackEventRequest,
    x_rapidapi_proxy_secret: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
):
    """Ingests an event and asynchronously fans it out to all configured destinations."""
    verify_auth(x_rapidapi_proxy_secret, x_api_key, authorization)
    event_id = f"evt_{uuid.uuid4().hex[:12]}"
    store.record_ingested()
    
    queued = await router.dispatch_track(event)

    return EventResponse(
        success=True,
        event_id=event_id,
        destinations_queued=queued,
        message=f"Event '{event.event}' queued for delivery to {queued} destination(s)."
    )

@app.post("/v1/identify", response_model=EventResponse, tags=["Identity"])
async def identify_user(
    data: IdentifyRequest,
    x_rapidapi_proxy_secret: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
):
    """Associates attributes and traits with a unique user profile across all destinations."""
    verify_auth(x_rapidapi_proxy_secret, x_api_key, authorization)
    event_id = f"ident_{uuid.uuid4().hex[:12]}"
    store.record_ingested()

    queued = await router.dispatch_identify(data)

    return EventResponse(
        success=True,
        event_id=event_id,
        destinations_queued=queued,
        message=f"Identify traits for user '{data.user_id}' queued to {queued} destination(s)."
    )


@app.post("/v1/destinations", response_model=DestinationConfig, tags=["Destinations"])
async def create_destination(dest: DestinationConfig):
    """Configures a new target destination webhook to receive forwarded events."""
    created = store.add_destination(dest)
    return created

@app.get("/v1/destinations", response_model=List[DestinationConfig], tags=["Destinations"])
async def list_destinations():
    """Returns all currently registered webhook destinations."""
    return store.get_destinations()

@app.delete("/v1/destinations/{dest_id}", tags=["Destinations"])
async def delete_destination(dest_id: str):
    """Removes a destination webhook from routing."""
    success = store.remove_destination(dest_id)
    if not success:
        raise HTTPException(status_code=404, detail="Destination not found.")
    return {"success": True, "deleted_id": dest_id}

@app.get("/v1/stats", response_model=StatsResponse, tags=["Telemetry"])
async def get_metrics():
    """Returns real-time event throughput, delivery success counts, and active connections."""
    return store.get_stats()
