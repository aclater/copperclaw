"""
OPERATION COPPERCLAW — Operator LLM
COSMIC INDIGO // REL KESTREL COALITION // EXERCISE

Routes to RamaLama (OpenAI-compatible, default) or Anthropic (opt-in).
"""

import os
import json
import anthropic
from openai import OpenAI
from config.operator_flavor import OPERATOR_EQUIPMENT_CONTEXT

LLM_BACKEND       = os.getenv("LLM_BACKEND", "ramalama")
LLM_MODEL         = os.getenv("LLM_MODEL", "qwen2.5:14b")
RAMALAMA_BASE_URL = os.getenv("RAMALAMA_BASE_URL", "http://localhost:8080/v1")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

OPERATOR_SYSTEM_PROMPT = f"""
You are the Operator interface for OPERATION COPPERCLAW,
a NATO F3EAD targeting cycle simulation running in
KESTREL Joint Task Force, AO HARROW.

You are the human-computer interface layer between a
real operator and the automated targeting cycle agents.
Speak as a competent targeting staff officer —
professional, precise, operationally literate.

{OPERATOR_EQUIPMENT_CONTEXT}

TOOL USE:
You have access to six tools:
- cycle_start: initiate a new F3EAD targeting cycle
- retask_isr: redirect a named ISR asset to a new PIR
- authorize_target: inject COMKJTF engagement authorization
- hold_target: place a target on hold with stated reason
- request_bda: request immediate BDA assessment
- inject_commander_guidance: inject COMKJTF guidance

Always reason from the current cycle state before
deciding on tool use. Keep responses concise and
operationally precise.

CLASSIFICATION: COSMIC INDIGO // REL KESTREL COALITION
EXERCISE — EXERCISE — EXERCISE
"""


def get_llm_response(messages: list,
                     tools: list,
                     cycle_state: dict) -> dict:
    system_with_state = (
        OPERATOR_SYSTEM_PROMPT +
        f"\n\nCURRENT CYCLE STATE:\n{cycle_state}"
    )
    if LLM_BACKEND == "anthropic":
        return _call_anthropic(messages, tools, system_with_state)
    return _call_ramalama(messages, tools, system_with_state)


def _call_ramalama(messages, tools, system_prompt):
    client = OpenAI(
        base_url=RAMALAMA_BASE_URL,
        api_key="ramalama"
    )
    oai_messages = [
        {"role": "system", "content": system_prompt}
    ] + messages

    kwargs = {
        "model": LLM_MODEL,
        "messages": oai_messages,
        "max_tokens": 1024,
    }
    if tools:
        kwargs["tools"] = _to_openai_tools(tools)
        kwargs["tool_choice"] = "auto"

    response = client.chat.completions.create(**kwargs)
    choice = response.choices[0]
    msg = choice.message

    tool_calls = []
    if msg.tool_calls:
        for tc in msg.tool_calls:
            tool_calls.append({
                "name": tc.function.name,
                "input": json.loads(tc.function.arguments)
            })

    return {
        "text": msg.content or "",
        "tool_calls": tool_calls
    }


def _call_anthropic(messages, tools, system_prompt):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    anthro_model = (
        LLM_MODEL
        if LLM_MODEL and "claude" in LLM_MODEL
        else "claude-sonnet-4-20250514"
    )
    response = client.messages.create(
        model=anthro_model,
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
        tools=tools if tools else []
    )
    text = ""
    tool_calls = []
    for block in response.content:
        if block.type == "text":
            text = block.text
        elif block.type == "tool_use":
            tool_calls.append({
                "name": block.name,
                "input": block.input
            })
    return {"text": text, "tool_calls": tool_calls}


def _to_openai_tools(anthropic_tools: list) -> list:
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("input_schema", {})
            }
        }
        for t in anthropic_tools
    ]


class OperatorLLM:
    def __init__(self):
        if LLM_BACKEND == "anthropic":
            self._client = anthropic.AsyncAnthropic(
                api_key=ANTHROPIC_API_KEY
            )
        else:
            self._client = None
        self.conversation_history: list[dict] = []

    async def process_message(
        self,
        user_message: str,
        cycle_state: str,
        kafka_client,
    ) -> dict:
        augmented_message = (
            f"CURRENT CYCLE STATE:\n{cycle_state}\n\n"
            f"OPERATOR MESSAGE:\n{user_message}"
        )
        self.conversation_history.append({
            "role": "user",
            "content": augmented_message,
        })

        tool_calls_made = []
        final_text = ""

        if LLM_BACKEND == "anthropic":
            final_text, tool_calls_made = await self._agentic_loop_anthropic(
                kafka_client
            )
        else:
            final_text, tool_calls_made = await self._agentic_loop_ramalama(
                kafka_client
            )

        return {
            "response": final_text,
            "tool_calls": tool_calls_made,
        }

    async def _agentic_loop_anthropic(self, kafka_client):
        import asyncio
        from tools import TOOLS
        tool_calls_made = []
        final_text = ""
        max_iterations = 5

        for _ in range(max_iterations):
            response = await self._client.messages.create(
                model=(
                    LLM_MODEL if LLM_MODEL and "claude" in LLM_MODEL
                    else "claude-sonnet-4-20250514"
                ),
                max_tokens=4096,
                system=OPERATOR_SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self.conversation_history,
            )
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = await kafka_client.execute_tool(
                            block.name, block.input
                        )
                        tool_calls_made.append({
                            "tool": block.name,
                            "input": block.input,
                            "result": result,
                        })
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result),
                        })
                self.conversation_history.append({
                    "role": "assistant", "content": response.content
                })
                self.conversation_history.append({
                    "role": "user", "content": tool_results
                })
            else:
                self.conversation_history.append({
                    "role": "assistant", "content": response.content
                })
                break

        return final_text, tool_calls_made

    async def _agentic_loop_ramalama(self, kafka_client):
        import asyncio
        from tools import TOOLS
        from openai import AsyncOpenAI
        tool_calls_made = []
        final_text = ""
        max_iterations = 5

        client = AsyncOpenAI(
            base_url=RAMALAMA_BASE_URL,
            api_key="ramalama"
        )
        oai_tools = _to_openai_tools(TOOLS)

        for _ in range(max_iterations):
            oai_messages = [
                {"role": "system", "content": OPERATOR_SYSTEM_PROMPT}
            ] + self.conversation_history

            response = await client.chat.completions.create(
                model=LLM_MODEL,
                messages=oai_messages,
                tools=oai_tools,
                tool_choice="auto",
                max_tokens=4096,
            )
            choice = response.choices[0]
            msg = choice.message

            if msg.content:
                final_text += msg.content

            if choice.finish_reason == "tool_calls" and msg.tool_calls:
                tool_results = []
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments)
                    result = await kafka_client.execute_tool(
                        tc.function.name, args
                    )
                    tool_calls_made.append({
                        "tool": tc.function.name,
                        "input": args,
                        "result": result,
                    })
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result),
                    })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                })
                self.conversation_history.extend(tool_results)
            else:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": msg.content or "",
                })
                break

        return final_text, tool_calls_made

    def clear_history(self):
        self.conversation_history = []
