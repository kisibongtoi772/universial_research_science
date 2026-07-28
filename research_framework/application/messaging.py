import asyncio
from typing import Dict, Any, Callable, Awaitable
from pydantic import BaseModel, Field

class Message(BaseModel):
    topic: str
    sender_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class MessageBus:
    """
    A reactive message bus for agent communication and event handling.
    Allows agents to sleep and wake up when specific events occur.
    """
    def __init__(self):
        self._subscribers: Dict[str, list[Callable[[Message], Awaitable[None]]]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task = None

    def subscribe(self, topic: str, handler: Callable[[Message], Awaitable[None]]):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    async def publish(self, topic: str, sender_id: str, payload: Dict[str, Any] = None):
        msg = Message(topic=topic, sender_id=sender_id, payload=payload or {})
        await self._queue.put(msg)

    async def _process_events(self):
        while self._running:
            try:
                msg: Message = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                handlers = self._subscribers.get(msg.topic, [])
                for handler in handlers:
                    # In a real system, we might want to run these concurrently
                    await handler(msg)
                self._queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing message: {e}")

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._process_events())

    async def stop(self):
        self._running = False
        if self._task:
            await self._task
