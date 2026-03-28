"""
OPERATION COPPERCLAW — Operator LLM
COSMIC INDIGO // REL KESTREL COALITION // EXERCISE

Wraps the Anthropic API with the six COPPERCLAW operator tools.
"""

import os
import json
import asyncio
from typing import Any

import anthropic

from tools import TOOLS
from config.operator_flavor import OPERATOR_EQUIPMENT_CONTEXT

OPERATOR_SYSTEM_PROMPT = f"""
You are the Operator interface for OPERATION COPPERCLAW, a NATO F3EAD targeting
cycle simulation running in KESTREL Joint Task Force, AO HARROW.

You are the human-computer interface layer between a real operator (a person)
and the automated targeting cycle agents. You speak in the voice of a
competent targeting staff officer — professional, precise, operationally
literate. You maintain situational awareness of the full cycle state.

{OPERATOR_EQUIPMENT_CONTEXT}

TOOL USE:
You have access to six tools. Use them to act on the cycle:
- cycle_start: initiate a new F3EAD targeting cycle
- retask_isr: redirect a named ISR asset to a new PIR
- authorize_target: inject COMKJTF engagement authorization
- hold_target: place a target on hold with stated reason
- request_bda: request immediate BDA assessment
- inject_commander_guidance: inject plain-language COMKJTF guidance

When the operator gives you an instruction that maps to one of these tools,
call the appropriate tool. You may call multiple tools in one response if
the operator's instruction requires it.

CYCLE STATE:
The current cycle state will be injected into each message turn as a JSON
block. Always reason from the current state before deciding on tool use.
Reference specific cycle_id, target_id, and report_id values from the state
when making tool calls.

CLASSIFICATION:
All outputs: COSMIC INDIGO // REL KESTREL COALITION
EXERCISE — EXERCISE — EXERCISE
"""

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


class OperatorLLM:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.conversation_history: list[dict] = []

    async def process_message(
        self,
        user_message: str,
        cycle_state: str,
        kafka_client: Any,
    ) -> dict:
        """
        Process an operator message. May call tools and return a combined response.
        """
        # Inject cycle state as context in the user message
        augmented_message = f"""
CURRENT CYCLE STATE:
{cycle_state}

OPERATOR MESSAGE:
{user_message}
"""
        self.conversation_history.append({
            "role": "user",
            "content": augmented_message,
        })

        tool_calls_made = []
        final_text = ""

        # Agentic loop — may call tools multiple times
        max_iterations = 5
        for _ in range(max_iterations):
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=OPERATOR_SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self.conversation_history,
            )

            # Collect text blocks
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text

            # Check if we need to handle tool use
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_result = await kafka_client.execute_tool(
                            block.name, block.input
                        )
                        tool_calls_made.append({
                            "tool": block.name,
                            "input": block.input,
                            "result": tool_result,
                        })
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(tool_result),
                        })

                # Add assistant response and tool results to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content,
                })
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results,
                })
            else:
                # End of agentic loop
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content,
                })
                break

        return {
            "response": final_text,
            "tool_calls": tool_calls_made,
            "stop_reason": response.stop_reason,
        }

    def clear_history(self):
        """Reset conversation history (new session)."""
        self.conversation_history = []
