"""
agents/diagnosis_agent.py
Wraps tools/vision_tool.py and formats the result for the orchestrator.
"""

from tools.vision_tool import diagnose_leaf
from utils.logger import AgentTrace


def run(image_path: str, crop_hint: str = "", trace: AgentTrace | None = None) -> str:
    """
    Run the Diagnosis Agent and return a human-readable diagnosis string.
    Logs steps to the trace if provided.
    """
    if trace:
        trace.add("tool_call", "Diagnosis Agent → Vision Model",
                  f"Sending image to **{__import__('config').VISION_MODEL}** for analysis…")

    result = diagnose_leaf(image_path, crop_hint=crop_hint)

    if "error" in result:
        msg = f"⚠️ Diagnosis failed: {result['error']}"
        if trace:
            trace.add("tool_result", "Diagnosis Result", msg)
        return msg

    if trace:
        trace.add("tool_result", "Diagnosis Result",
                  f"Crop: **{result.get('crop')}** | "
                  f"Disease: **{result.get('disease')}** | "
                  f"Confidence: {result.get('confidence')} | "
                  f"Severity: {result.get('severity')}")

    return (
        f"🔬 **Diagnosis:**\n"
        f"- **Crop detected:** {result.get('crop', 'Unknown')}\n"
        f"- **Disease / Issue:** {result.get('disease', 'Unknown')}\n"
        f"- **Confidence:** {result.get('confidence', '—')}\n"
        f"- **Severity:** {result.get('severity', '—')}\n"
        f"- **Symptoms observed:** {result.get('symptoms', '—')}\n"
        f"- **Recommended treatment:** {result.get('treatment', '—')}\n"
    )
