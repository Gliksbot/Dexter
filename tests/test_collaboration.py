import asyncio
from backend.collaboration import CollaborationHub


def test_broadcast_collects_events():
    hub = CollaborationHub()
    events = []

    async def listener(event_type, payload):
        events.append((event_type, payload))

    hub.subscribe(listener)
    asyncio.run(hub.broadcast("test", {"value": 1}))

    assert events == [("test", {"value": 1})]
