"""
OPERATION COPPERCLAW — Operator Service
COSMIC INDIGO // REL KESTREL COALITION // EXERCISE

FastAPI application providing:
  POST /api/operator/message  — operator LLM conversation turn
  GET  /api/operator/stream   — SSE stream proxied from sse-bridge-service
  POST /api/operator/tool     — direct tool call injection (bypass LLM)
  GET  /api/operator/state    — current CycleState from state-service
"""

import os
import json
import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

from operator_llm import OperatorLLM
from kafka_client import KafkaClient

app = FastAPI(
    title="COPPERCLAW Operator Service",
    description="COSMIC INDIGO // REL KESTREL COALITION // EXERCISE",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE_SERVICE_URL = os.getenv("STATE_SERVICE_URL", "http://localhost:8089")
SSE_BRIDGE_URL = os.getenv("SSE_BRIDGE_URL", "http://localhost:8090")

operator_llm = OperatorLLM()
kafka_client = KafkaClient()


class MessageRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ToolRequest(BaseModel):
    tool_name: str
    tool_input: dict


@app.get("/health")
async def health():
    return {"status": "UP", "service": "operator-service"}


@app.post("/api/operator/message")
async def operator_message(request: MessageRequest):
    """
    Process an operator message through the LLM.
    The LLM may call tools (publish to Kafka topics) as part of its response.
    Returns the LLM's text response and any tool calls made.
    """
    try:
        # Fetch current cycle state to inject as context
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                state_resp = await client.get(f"{STATE_SERVICE_URL}/api/state/current")
                cycle_state = state_resp.text if state_resp.status_code == 200 else "{}"
            except Exception:
                cycle_state = "{}"

        result = await operator_llm.process_message(
            user_message=request.message,
            cycle_state=cycle_state,
            kafka_client=kafka_client,
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/operator/stream")
async def operator_stream():
    """
    Proxy the SSE stream from sse-bridge-service to the frontend.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                async with client.stream("GET", f"{SSE_BRIDGE_URL}/api/stream") as response:
                    async for line in response.aiter_lines():
                        if line:
                            yield f"{line}\n\n"
            except Exception as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/operator/tool")
async def operator_tool(request: ToolRequest):
    """
    Direct tool call injection — bypasses LLM, publishes directly to Kafka.
    Used for operator automation or testing.
    """
    try:
        result = await kafka_client.execute_tool(request.tool_name, request.tool_input)
        return {"status": "published", "tool": request.tool_name, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/operator/state")
async def get_state():
    """
    Fetch current CycleState from state-service.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{STATE_SERVICE_URL}/api/state/current")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"State service unavailable: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
