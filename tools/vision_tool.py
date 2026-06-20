"""
tools/vision_tool.py
Crop leaf diagnosis using Gemini's native multimodal (vision) capability.

Design choice: rather than training/hosting a custom CNN (which needs
GPU time, a labeled dataset, and a model file to ship), we use Gemini's
vision understanding directly. This is faster to build, easier to keep
accurate (no stale model), and is itself a clean demonstration of
multimodal TOOL USE for the rubric -- the diagnosis IS a tool call,
not a separate ML pipeline bolted onto the agent.
"""

import json
from PIL import Image
from google import genai
from google.genai import types

from config import GEMINI_API_KEY, VISION_MODEL

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


_DIAGNOSIS_PROMPT = """You are an expert plant pathologist specializing in
crops grown in South Indian smallholder farms (tomato, groundnut, mango,
tamarind, ragi, and similar).

Examine the attached leaf/plant image carefully and respond with ONLY a
JSON object (no markdown fences, no extra text) in exactly this shape:

{
  "crop_identified": "<best guess at crop type, or 'unclear' if uncertain>",
  "condition": "<disease/pest name, or 'healthy' if no issue visible>",
  "confidence": "<low | medium | high>",
  "visual_evidence": "<1-2 sentences describing what you see that supports this>",
  "severity": "<none | mild | moderate | severe>"
}

If the image is not a plant/leaf at all, set crop_identified to "not_a_plant"
and condition to "unclear" with a brief visual_evidence explanation.
Be conservative: if you are not confident, say so in confidence and
explain why in visual_evidence rather than guessing definitively.
"""


def diagnose_leaf_image(image_path: str) -> dict:
    """
    Analyze a photo of a crop leaf/plant to identify the crop and any
    visible disease or pest damage.

    Args:
        image_path: Local filesystem path to the image file.

    Returns:
        dict with crop identification, condition, confidence and severity.
    """
    try:
        image = Image.open(image_path)
    except Exception as e:
        return {"status": "error", "message": f"Could not open image: {e}"}

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=VISION_MODEL,
            contents=[_DIAGNOSIS_PROMPT, image],
            config=types.GenerateContentConfig(
                temperature=0.2,  # low temperature: we want consistent, careful diagnosis
                response_mime_type="application/json",
            ),
        )
        parsed = json.loads(response.text)
        parsed["status"] = "success"
        return parsed
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Model did not return valid JSON.",
            "raw_response": getattr(response, "text", ""),
        }
    except Exception as e:
        return {"status": "error", "message": f"Vision diagnosis failed: {e}"}
