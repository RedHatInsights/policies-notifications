import json
import asyncio
import logging
from typing import Mapping

from aiokafka import AIOKafkaConsumer
from prometheus_client import Counter

from .models import Notification
from ..email.process import EmailProcessor
from ..core.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_QUEUE_EMAIL

logger = logging.getLogger(__name__)


class EmailSubscriptionConsumer:
    consumer_restarts = Counter('email_consumer_restarts', 'Restart count of Email consumer')

    def __init__(self):
        loop = asyncio.get_event_loop()
        self.consumer = AIOKafkaConsumer(
            KAFKA_QUEUE_EMAIL, loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')), group_id='notifications',
            enable_auto_commit=False, retry_backoff_ms=2000)
        self._running = False
        self.processor = EmailProcessor()

    async def start(self):
        logger.info('EmailSubscriptionConsumer starting')
        await self.consumer.start()
        loop = asyncio.get_event_loop()
        loop.create_task(self.consume())
        self._running = True

    async def shutdown(self):
        logger.info('EmailSubscriptionConsumer shutting down')
        self._running = False
        await self.consumer.stop()
        self.processor.shutdown()

    async def restart(self):
        logger.info('Rolling back the Kafka seek position after 10 second sleep')
        self.consumer_restarts.inc()
        await asyncio.sleep(10)
        await self.consumer.seek_to_committed()

    async def consume(self):
        try:
            async for msg in self.consumer:
                try:
                    msg_dict = msg.value
                    if not isinstance(msg_dict['tags'], Mapping):
                        msg_dict['tags'] = {}
                        await self.consumer.commit()
                        continue

                    for k, v in msg_dict['tags'].iteritems():
                        if v is None or not isinstance(v, str):
                            msg_dict['tags'].pop(k, None)

                    notification: Notification = Notification(**msg_dict)
                    await self.processor.process(notification)
                    await self.consumer.commit()
                except Exception as e:
                    logger.error('Received error while trying to send email: %s', e)
                    await self.restart()

        finally:
            pass
