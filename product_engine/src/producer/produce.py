import schemas
import json
from producer.AIOWebProducer import AIOWebProducer


async def kafka_produce(msg: schemas.ProducerMessage, topic_name: str,
                        producer: AIOWebProducer) -> None:
    message_to_produce = json.dumps(msg.model_dump()).encode(encoding="utf-8")
    await producer.send(topic=topic_name, value=message_to_produce)
