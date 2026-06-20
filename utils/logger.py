"""
utils/logger.py
A tiny structured logger that ALSO captures the agent's reasoning trace
so the Streamlit UI can render a live "thinking" panel.
This is what makes the orchestration visible to judges -- the most
important thing for an Agent Intensive capstone.
"""

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraceEvent:
    timestamp: float
    actor: str          # which agent/component emitted this
    event_type: str      # "plan" | "tool_call" | "tool_result" | "thought" | "final"
    content: str
    meta: dict = field(default_factory=dict)


class AgentTrace:
    """
    Collects a running list of TraceEvents for one user turn.
    The orchestrator and every sub-agent write into the same trace
    so the UI can show a single, ordered timeline of what happened.
    """

    def __init__(self):
        self.events: list[TraceEvent] = []

    def log(self, actor: str, event_type: str, content: str, **meta: Any) -> None:
        self.events.append(
            TraceEvent(
                timestamp=time.time(),
                actor=actor,
                event_type=event_type,
                content=content,
                meta=meta,
            )
        )

    def as_markdown(self) -> str:
        lines = []
        icons = {
            "plan": "🧭",
            "tool_call": "🔧",
            "tool_result": "📥",
            "thought": "💭",
            "final": "✅",
            "error": "⚠️",
        }
        for e in self.events:
            icon = icons.get(e.event_type, "•")
            lines.append(f"{icon} **{e.actor}** — {e.content}")
        return "\n\n".join(lines)

    def clear(self) -> None:
        self.events = []
