from aiokafka import AIOKafkaConsumer
from config import settings
import json


async def get_consumer():
    return AIOKafkaConsumer(settings.kafka_consume_topic, bootstrap_servers=settings.kafka_url)


async def consume():
    consumer = await get_consumer()
    await consumer.start()
    try:
        async for msg in consumer:
            decoded_message = json.loads(msg.value)
            print(
                "consumed: ",
                decoded_message
            )
    finally:
        await consumer.stop()


async def stop_consumer():
    consumer = await broker.get_consumer()
    await consumer.stop()
