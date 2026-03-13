"""
In-memory broadcaster for tournament SSE.
При обновлении матча или раунда вызывается publish — все подписчики потока этого турнира получают событие.
"""

import asyncio
import json
from collections import defaultdict
from typing import Any

from sse_starlette.sse import ServerSentEvent


class TournamentEventBroadcaster:
    """Один общий экземпляр: подписки по tournament_id, рассылка при publish."""

    def __init__(self) -> None:
        self._queues: dict[int, list[asyncio.Queue]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, tournament_id: int):
        """Подписка на события турнира. Использовать как async generator: async for event in broadcaster.subscribe(tid)."""
        queue: asyncio.Queue = asyncio.Queue()
        async with self._lock:
            self._queues[tournament_id].append(queue)
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=30.0)
                except TimeoutError:
                    yield ServerSentEvent(data=json.dumps({"type": "ping"}), event="ping")
                    continue
                if msg is None:
                    break
                yield msg
        finally:
            async with self._lock:
                if tournament_id in self._queues:
                    try:
                        self._queues[tournament_id].remove(queue)
                    except ValueError:
                        pass
                    if not self._queues[tournament_id]:
                        del self._queues[tournament_id]

    async def publish(
        self, tournament_id: int, event_type: str, data: dict[str, Any] | None = None
    ) -> None:
        """Разослать событие всем подписчикам турнира."""
        payload = {"type": event_type, **(data or {})}
        event = ServerSentEvent(data=json.dumps(payload), event=event_type)
        async with self._lock:
            queues = list(self._queues.get(tournament_id, []))
        for q in queues:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass


# Глобальный экземпляр (инфраструктура)
broadcaster = TournamentEventBroadcaster()
