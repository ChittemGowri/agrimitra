"""
agents/diagnosis_agent.py
The Diagnosis Agent: given a leaf photo, calls the vision tool and
returns a structured, farmer-readable diagnosis. Logs its reasoning
into the shared AgentTrace so the orchestrator's full plan is visible.
"""

from tools.vision_tool import diagnose_leaf_image
from utils.logger import AgentTrace

AGENT_NAME = "DiagnosisAgent"


def run_diagnosis(image_path: str, trace: AgentTrace) -> dict:
    trace.log(AGENT_NAME, "plan", f"Analyzing uploaded image with Gemini Vision: {image_path}")
    trace.log(AGENT_NAME, "tool_call", "diagnose_leaf_image(image_path)")

    result = diagnose_leaf_image(image_path)

    if result.get("status") != "success":
        trace.log(AGENT_NAME, "error", result.get("message", "Diagnosis failed."))
        return result

    summary = (
        f"crop={result.get('crop_identified')}, "
        f"condition={result.get('condition')}, "
        f"confidence={result.get('confidence')}, "
        f"severity={result.get('severity')}"
    )
    trace.log(AGENT_NAME, "tool_result", f"Diagnosis complete: {summary}")
    return result
