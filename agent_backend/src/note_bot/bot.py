from __future__ import annotations

import logging
import os
from typing import List, Optional

from agents import (
    ItemHelpers,
    Runner,
    TResponseInputItem,
    gen_trace_id,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
    trace,
)
from fastapi import WebSocket
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent

from .agent.agent import notes_agent
from .agent.tools.notes_client import JWTTokenManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("OPENAI_API_KEY", "")

client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)
set_default_openai_client(client=client, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)


class Bot:
    async def run(
        self,
        input_messages: List[TResponseInputItem],
        token: str,
        websocket: Optional[WebSocket] = None,
    ) -> None:
        trace_id = gen_trace_id()
        with trace("Notes trace", trace_id=trace_id):
            with JWTTokenManager(token):
                if websocket is not None:
                    await self._websocket_stream(input_messages, websocket)

    async def _websocket_stream(
        self, input_messages: List[TResponseInputItem], websocket: WebSocket
    ) -> None:
        """Handles WebSocket streaming."""
        response = Runner.run_streamed(notes_agent, input_messages)
        logger.info("=== Run starting ===")
        async for event in response.stream_events():
            await self._handle_event(event, websocket)

    async def _handle_event(self, event, websocket: WebSocket) -> None:
        """Processes different event types from the agent."""
        try:
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                await websocket.send_json(
                    {"type": "message_response", "message": event.data.delta}
                )
            elif event.type == "agent_updated_stream_event":
                logger.info(f"Agent updated: {event.new_agent.name}")
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    logger.info("-- Tool was called")
                elif event.item.type == "tool_call_output_item":
                    logger.info(f"-- Tool output: {event.item.output}")
                    await websocket.send_json(
                        {"type": "tool_call_output", "message": event.item.output}
                    )
                elif event.item.type == "message_output_item":
                    logger.info(
                        f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}"
                    )
                    await websocket.send_json({"type": "final_output", "message": None})
        except Exception as e:
            logger.error(f"Error processing event: {e}")
