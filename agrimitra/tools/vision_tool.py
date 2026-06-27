"""
tools/vision_tool.py
Uses NVIDIA's vision model (llama-3.2-90b-vision-instruct via NIM)
to analyse a plant/leaf image and return a structured diagnosis.

NVIDIA NIM is fully OpenAI-SDK-compatible, so we use the openai package
with a custom base_url + api_key.
"""

import base64
import json
from pathlib import Path

from openai import OpenAI

from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, VISION_MODEL


def _encode_image(image_path: str) -> str:
    """Return a base-64 encoded string of the image bytes."""
    return base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")


def diagnose_leaf(image_path: str, crop_hint: str = "") -> dict:
    """
    Analyse the plant image and return a dict:
      {
        "crop":        str,
        "disease":     str,
        "confidence":  str,   # "High" / "Medium" / "Low"
        "symptoms":    str,
        "treatment":   str,
        "severity":    str,   # "Mild" / "Moderate" / "Severe"
      }
    Returns {"error": "..."} on failure.
    """
    if not NVIDIA_API_KEY:
        return {"error": "NVIDIA_API_KEY not set."}
    if not Path(image_path).exists():
        return {"error": f"Image not found: {image_path}"}

    client = OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=NVIDIA_API_KEY,
    )

    b64 = _encode_image(image_path)
    # NVIDIA NIM vision: image via data URI in the content array
    image_url = f"data:image/jpeg;base64,{b64}"

    hint_text = f" The crop is likely {crop_hint}." if crop_hint else ""

    prompt = (
        "You are an expert agricultural plant pathologist.{hint} "
        "Analyse the leaf/plant in the image carefully and respond ONLY with "
        "a valid JSON object (no markdown fences, no extra text) with exactly "
        "these keys:\n"
        "  crop, disease, confidence, symptoms, treatment, severity\n\n"
        "Guidelines:\n"
        "- confidence: one of High / Medium / Low\n"
        "- severity:   one of Mild / Moderate / Severe\n"
        "- treatment:  2-3 concrete actionable sentences\n"
        "- If the image is not a plant, set disease to 'Not a plant image' "
        "and all other fields to 'N/A'."
    ).format(hint=hint_text)

    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            max_tokens=600,
            temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown fences if model still adds them
        raw = raw.strip("```json").strip("```").strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}", "raw": raw}
    except Exception as e:
        return {"error": str(e)}
