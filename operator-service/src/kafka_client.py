"""
OPERATION COPPERCLAW — Kafka Client
COSMIC INDIGO // REL KESTREL COALITION // EXERCISE

Async Kafka producer for publishing operator tool calls to Kafka topics.
"""

import os
import json
import uuid
from datetime import datetime, timezone

from aiokafka import AIOKafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Map tool names to Kafka topics
TOOL_TOPIC_MAP = {
    "cycle_start": "copperclaw.operator-commands",
    "retask_isr": "copperclaw.operator-commands",
    "authorize_target": "copperclaw.operator-commands",
    "hold_target": "copperclaw.operator-commands",
    "request_bda": "copperclaw.operator-commands",
    "inject_commander_guidance": "copperclaw.operator-commands",
}


class KafkaClient:
    def __init__(self):
        self._producer: AIOKafkaProducer | None = None

    async def _get_producer(self) -> AIOKafkaProducer:
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await self._producer.start()
        return self._producer

    async def publish(self, topic: str, message: dict) -> None:
        """Publish a message to a Kafka topic."""
        producer = await self._get_producer()
        await producer.send_and_wait(topic, message)

    async def execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """
        Execute a tool call by publishing a structured message to the appropriate
        Kafka topic. Returns a result dict describing what was published.
        """
        topic = TOOL_TOPIC_MAP.get(tool_name, "copperclaw.operator-commands")

        message = {
            "message_id": str(uuid.uuid4()),
            "tool_name": tool_name,
            "input": tool_input,
            "timestamp_zulu": datetime.now(timezone.utc).isoformat(),
            "source": "operator-service",
            "classification": "COSMIC INDIGO // REL KESTREL COALITION",
            "exercise_serial": "COPPERCLAW-SIM-001",
        }

        await self.publish(topic, message)

        return {
            "published": True,
            "topic": topic,
            "message_id": message["message_id"],
            "tool": tool_name,
        }

    async def close(self):
        if self._producer:
            await self._producer.stop()
            self._producer = None
