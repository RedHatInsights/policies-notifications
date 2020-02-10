import json
import asyncio
import logging

from aiokafka import AIOKafkaConsumer

from .models import Notification
from ..email.process import EmailProcessor
from ..core.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_QUEUE_EMAIL

logger = logging.getLogger(__name__)


class EmailSubscriptionConsumer:
    def __init__(self):
        loop = asyncio.get_event_loop()
        self.consumer = AIOKafkaConsumer(
            KAFKA_QUEUE_EMAIL, loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')), group_id='notifications',
            enable_auto_commit=False)
        self._running = False
        logger.info('Created EmailSubscriptionConsumer')
        self.processor = EmailProcessor()

    async def start(self):
        logger.info('EmailSubscriptionConsumer start called')
        await self.consumer.start()
        loop = asyncio.get_event_loop()
        loop.create_task(self.consume())
        self._running = True

    async def shutdown(self):
        logger.info('EmailSubscriptionConsumer shutdown called')
        self._running = False
        await self.consumer.stop()

    async def restart(self):
        logger.info('Restarting consumer after 3 second timeout')
        await asyncio.sleep(3)
        logger.info('Restarting..')
        await self.consumer.seek_to_committed()
        loop = asyncio.get_event_loop()
        loop.create_task(self.consume())

    async def consume(self):
        logger.info('Started consuming messages..')
        # TODO Surround with try / finally, otherwise errors will crash the consumer
        # TODO What to do with errors? Such as when BOP service is down. Not commit and simply ignore a while?
        #      What about other type of errors, such as theoretical broken JSON? Or missing values otherwise
        try:
            async for msg in self.consumer:
                try:
                    notification: Notification = Notification(**msg.value)
                    await self.processor.process(notification)
                    await self.consumer.commit()
                except Exception as e:
                    logger.error('Received error while trying to send email: %s', e)
                    await self.restart()

        finally:
            logger.info('Stopped consuming messages')
