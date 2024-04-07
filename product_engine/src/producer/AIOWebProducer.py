from aiokafka import AIOKafkaProducer
from config import settings
import asyncio


class AIOWebProducer(object):
    def __init__(self, loop):
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_url,
            loop=loop
        )

    async def start(self) -> None:
        await self.__producer.start()

    async def stop(self) -> None:
        await self.__producer.stop()

    async def send(self, topic: str, value: bytes) -> None:
        await self.start()
        try:
            await self.__producer.send(
                topic=topic,
                value=value,
            )
        finally:
            await self.stop()


async def get_producer() -> AIOWebProducer:
    return AIOWebProducer(asyncio.get_event_loop())
