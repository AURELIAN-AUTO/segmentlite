# SegmentLite Python SDK

```python
from segmentlite import SegmentLite

client = SegmentLite(api_key="sgl_live_...", host="https://segmentlite-api-dfru.fly.dev")

# Send track event
client.track("Signed Up", user_id="usr_123", properties={"plan": "pro"})

# Identify user
client.identify("usr_123", traits={"email": "alice@example.com"})
```
