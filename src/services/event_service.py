from __future__ import annotations

from collections import defaultdict
from src.models.events import RuntimeEvent, EventType


class EventService:
    def __init__(self, max_events: int = 2000):
        self._events: dict[str, list[RuntimeEvent]] = defaultdict(list)
        self.max_events = max_events

    def emit(self, event: RuntimeEvent) -> None:
        bucket = self._events[event.session_id]
        bucket.append(event)
        if len(bucket) > self.max_events:
            self._events[event.session_id] = bucket[-self.max_events :]

    def list_events(
        self,
        session_id: str,
        event_type: EventType | None = None,
        agent_id: str | None = None,
        limit: int = 200,
    ) -> list[RuntimeEvent]:
        events = self._events.get(session_id, [])
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if agent_id:
            events = [e for e in events if e.agent_id == agent_id]
        return events[-limit:]

    def clear(self, session_id: str) -> None:
        self._events.pop(session_id, None)
