import asyncio, logging, json, os
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from .settings import get_settings

st = get_settings()

BOOTSTRAP = os.getenv("KAFKA_BROKERS", "kafka:9092")
WAIT_TIMEOUT = int(os.getenv("KAFKA_WAIT_TIMEOUT", "120"))
log = logging.getLogger("kafka-bus")

producer: AIOKafkaProducer | None = None
consumer: AIOKafkaConsumer | None = None
consumer_task: asyncio.Task | None = None

async def start_consumer():
    global consumer
    consumer = AIOKafkaConsumer(
        st.TOPIC_MOVIES, st.TOPIC_USERS, st.TOPIC_PAYMENTS,
        bootstrap_servers=BOOTSTRAP,
        value_deserializer=lambda v: json.loads(v.decode()),
        group_id="events-service",
        auto_offset_reset="earliest",
    )
    await consumer.start()

    async for msg in consumer:
        log.info("Received %s: %s", msg.topic, msg.value)

async def wait_kafka(timeout: int = WAIT_TIMEOUT):
    """Блокируем запуск приложения, пока Kafka не примет соединение."""
    global producer
    global consumer_task
    producer = AIOKafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v, default=str).encode(),
    )
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        try:
            await producer.start()
            consumer_task = asyncio.create_task(start_consumer())
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
        await producer.flush()
        await producer.stop()
    if consumer:
        await consumer.stop()
    if consumer_task:
        consumer_task.cancel()
