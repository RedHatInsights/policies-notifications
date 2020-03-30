import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from .models import Action
from ..core.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_QUEUE_HOOK
from ..webhooks.process import WebhookProcessor

logger = logging.getLogger(__name__)


class EventConsumer:

    def __init__(self):
        loop = asyncio.get_event_loop()
        self.consumer = AIOKafkaConsumer(
            KAFKA_QUEUE_HOOK, loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id="notifications", value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=False)
        self._running = False
        self.processor = WebhookProcessor()

    async def start(self):
        await self.consumer.start()
        loop = asyncio.get_event_loop()
        loop.create_task(self.consume())
        self._running = True

    async def shutdown(self):
        self._running = False
        await self.consumer.stop()

    async def consume(self):
        try:
            async for msg in self.consumer:
                try:
                    notification: Action = Action(**msg.value)
                    logger.info('Received msg from Kafka: %s', notification.dict())
                    await self.processor.process(notification)
                    self.consumer.raise_commit()
                except Exception as e:
                    logger.error('Received error while trying to process webhook: %s', e)
                    # await self.restart()

        finally:
            logger.info('Stopped consuming messages')
