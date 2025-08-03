import asyncio, logging, json
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import BackgroundTasks
from .settings import get_settings

settings = get_settings()
logger = logging.getLogger("events")

producer = AIOKafkaProducer(
    bootstrap_servers=settings.KAFKA_BROKERS,
    value_serializer=lambda v: json.dumps(v).encode()
)

def start_consumer(background: BackgroundTasks, topic: str):
    async def _consume():
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=settings.KAFKA_BROKERS,
            value_deserializer=lambda b: json.loads(b.decode()),
            auto_offset_reset="earliest",
            group_id="events-service"
        )
        await consumer.start()
        try:
            async for msg in consumer:
                logger.info("Consumed %s: %s", topic, msg.value)
        finally:
            await consumer.stop()
    background.add_task(_consume)
