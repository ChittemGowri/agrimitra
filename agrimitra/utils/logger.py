"""
utils/logger.py
Lightweight agent reasoning-trace collector.
Each event is a dict: {type, label, content}.
The UI renders the trace in the right-hand panel.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class AgentTrace:
    events: List[Dict[str, Any]] = field(default_factory=list)

    def add(self, event_type: str, label: str, content: str) -> None:
        """
        event_type: 'plan' | 'tool_call' | 'tool_result' | 'synthesis' | 'info'
        label:      short heading shown in the UI
        content:    freeform text / markdown body
        """
        self.events.append({
            "type": event_type,
            "label": label,
            "content": content,
        })

    def as_markdown(self) -> str:
        """Render all trace events as a markdown string for the UI panel."""
        icons = {
            "plan":        "📋",
            "tool_call":   "🔧",
            "tool_result": "📊",
            "synthesis":   "🧩",
            "info":        "ℹ️",
        }
        lines = []
        for ev in self.events:
            icon = icons.get(ev["type"], "•")
            lines.append(f"**{icon} {ev['label']}**\n\n{ev['content']}\n\n---\n")
        return "\n".join(lines)
