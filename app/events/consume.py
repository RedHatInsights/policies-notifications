import json
import asyncio

from aiokafka import AIOKafkaConsumer

from .models import Action
from ..core.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_QUEUE_HOOK


class EventConsumer:

    def __init__(self):
        loop = asyncio.get_event_loop()
        self.consumer = AIOKafkaConsumer(
            KAFKA_QUEUE_HOOK, loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id="notifications", value_deserializer=lambda m: json.loads(m.decode('utf-8')))
        self._running = False

    async def start(self):
        await self.consumer.start()

        self._running = True
        # Start consumer here

    async def shutdown(self):
        self._running = False
        await self.consumer.stop()

    async def consume(self):
        while self._running:
            async for msg in self.consumer:
                action: Action = Action(**msg.value["action"])  # JSON
                # Do something with the message
                pass
