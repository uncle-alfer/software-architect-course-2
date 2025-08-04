import asyncio, logging, json, os
from aiokafka import AIOKafkaProducer

BOOTSTRAP = os.getenv("KAFKA_BROKERS", "kafka:9092")
log = logging.getLogger("kafka-bus")

producer: AIOKafkaProducer | None = None


async def wait_kafka(timeout: int = 30):
    """Блокируем запуск приложения, пока Kafka не примет соединение."""
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        try:
            await producer.start()
            log.info("Kafka connected")
            return
        except Exception as exc:
            if asyncio.get_event_loop().time() > deadline:
                log.error("Kafka unavailable: %s", exc)
                raise
            log.warning("Kafka not ready, retry in 2 s")
            await asyncio.sleep(2)


async def stop_kafka():
    if producer:
        await producer.stop()
