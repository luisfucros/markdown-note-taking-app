import os

from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from .prompts import notes_agent_prompt, grammar_agent_prompt
from .tools.notes_client import create_note, get_note, get_notes

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini-2024-07-18")

notes_agent = Agent(
    name="Notes Agent",
    handoff_description="A helpful agent that can use a notes crud app",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
   {notes_agent_prompt}""",
    tools=[get_note, get_notes, create_note],
    model=MODEL_NAME,
)
