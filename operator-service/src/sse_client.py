"""
OPERATION COPPERCLAW — SSE Client
COSMIC INDIGO // REL KESTREL COALITION // EXERCISE

Utility for consuming SSE events from the sse-bridge-service.
Used internally by the operator service for state polling.
"""

import os
from typing import AsyncGenerator

import httpx

SSE_BRIDGE_URL = os.getenv("SSE_BRIDGE_URL", "http://localhost:8090")


async def stream_events() -> AsyncGenerator[str, None]:
    """
    Async generator that yields SSE event data strings from the sse-bridge-service.
    """
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("GET", f"{SSE_BRIDGE_URL}/api/stream") as response:
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    yield line[5:].strip()
                elif line and not line.startswith(":"):
                    yield line


async def get_recent_state() -> str:
    """
    Fetch the current cycle state snapshot from the sse-bridge-service health endpoint.
    Returns raw JSON string.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{SSE_BRIDGE_URL}/api/stream/health")
            return response.text
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
