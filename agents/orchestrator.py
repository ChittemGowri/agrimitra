"""
agents/orchestrator.py
The planning brain of AgriMitra.

Uses NVIDIA NIM's OpenAI-compatible tool-calling API to dynamically
decide which specialist agents to invoke (Diagnosis, Advisory, Market)
and in what order, then synthesises a single coherent answer.

Tool definitions match OpenAI function-calling schema — supported by
NVIDIA NIM's llama-3.3-70b-instruct endpoint.
"""

import json
from typing import Any, Dict, List

from openai import OpenAI

from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, TEXT_MODEL, DEFAULT_LOCATION
from utils.logger import AgentTrace
from utils.memory import get_memory, save_memory, append_turn, get_history_text
import agents.diagnosis_agent as diagnosis_agent
import agents.advisory_agent as advisory_agent
import agents.market_agent as market_agent


# ---------------------------------------------------------------------------
# Tool definitions (OpenAI function-calling schema)
# ---------------------------------------------------------------------------

TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "diagnose_crop_image",
            "description": (
                "Analyse a plant or leaf photograph to identify crop disease, "
                "pest damage, or nutrient deficiency. Call this whenever the "
                "farmer uploads an image or describes visible symptoms on a leaf."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Absolute or relative path to the image file on disk.",
                    },
                    "crop_hint": {
                        "type": "string",
                        "description": "Optional crop name to help the vision model (e.g. 'Tomato').",
                    },
                },
                "required": ["image_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_farming_advice",
            "description": (
                "Retrieve practical crop management advice from agricultural "
                "extension documents using RAG. Call this when the farmer asks "
                "about treatment, irrigation, fertilisation, pest control, or "
                "any agronomic practice question."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The farmer's question or the topic to look up.",
                    },
                    "diagnosis_context": {
                        "type": "string",
                        "description": (
                            "Optional: the diagnosis string from diagnose_crop_image "
                            "to make the advice more specific."
                        ),
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_market_and_weather",
            "description": (
                "Fetch the current mandi (wholesale) price for a crop and the "
                "live local weather, then give a sell/hold recommendation. "
                "Call this when the farmer asks about price, market, when to sell, "
                "or weather conditions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "crop": {
                        "type": "string",
                        "description": "The crop name to look up (e.g. 'Tomato', 'Groundnut').",
                    },
                },
                "required": ["crop"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------

def _dispatch(tool_name: str, args: Dict[str, Any],
              trace: AgentTrace) -> str:
    if tool_name == "diagnose_crop_image":
        return diagnosis_agent.run(
            image_path=args["image_path"],
            crop_hint=args.get("crop_hint", ""),
            trace=trace,
        )
    elif tool_name == "get_farming_advice":
        return advisory_agent.run(
            query=args["query"],
            diagnosis_context=args.get("diagnosis_context", ""),
            trace=trace,
        )
    elif tool_name == "check_market_and_weather":
        return market_agent.run(
            crop=args["crop"],
            trace=trace,
        )
    else:
        return f"[Unknown tool: {tool_name}]"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def handle_farmer_query(
    session_id: str,
    user_text: str,
    image_path: str | None,
    language: str,
    trace: AgentTrace,
) -> str:
    """
    Full agent loop:
      1. Build a context-aware prompt (memory + history + current query).
      2. Call the NVIDIA NIM model with tool definitions.
      3. Dispatch any tool calls the model requests.
      4. Feed tool results back and get the final synthesised answer.
      5. Persist the turn to memory.
    Returns the final answer string.
    """
    if not NVIDIA_API_KEY:
        return (
            "⚠️ **NVIDIA_API_KEY is not set.** "
            "Please add it to your .env file and restart the app."
        )

    client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)

    # -- Memory & history --
    memory = get_memory(session_id)
    history_text = get_history_text(session_id)

    # -- System prompt --
    system = (
        f"You are AgriMitra, a helpful AI farm advisor serving smallholder farmers "
        f"near {DEFAULT_LOCATION}. You have access to three specialist tools:\n"
        f"  • diagnose_crop_image — identify crop disease from a photo\n"
        f"  • get_farming_advice  — RAG-based agronomic advice\n"
        f"  • check_market_and_weather — live mandi prices + weather\n\n"
        f"Farmer profile:\n"
        f"  Crop: {memory.get('crop') or 'unknown'}\n"
        f"  Location: {memory.get('location') or DEFAULT_LOCATION}\n\n"
        f"Recent conversation:\n{history_text}\n\n"
        f"INSTRUCTIONS:\n"
        f"1. Analyse the farmer's query and decide which tools to call.\n"
        f"2. Call ALL relevant tools — do not skip tools when the question "
        f"   clearly requires them.\n"
        f"3. After receiving tool results, synthesise a single, clear, empathetic "
        f"   answer in {language}.\n"
        f"4. Keep the final answer practical and under 300 words.\n"
        f"5. If no tool is needed (e.g. greetings), answer directly."
    )

    # -- Build initial messages --
    user_content = user_text
    if image_path:
        user_content += f"\n[Image attached at path: {image_path}]"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]

    trace.add("plan", "Orchestrator — Initial Plan",
              f"Query received: _{user_text[:150]}_\n\n"
              f"Image: {'Yes' if image_path else 'No'} | "
              f"Language: {language}")

    # -- Agentic loop (max 5 iterations to prevent infinite loops) --
    tool_results_collected: List[str] = []

    for iteration in range(5):
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=800,
            temperature=0.2,
        )

        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # Append assistant message to conversation
        messages.append({"role": "assistant", "content": msg.content or "",
                         "tool_calls": [tc.model_dump() for tc in (msg.tool_calls or [])]})

        if finish_reason == "tool_calls" and msg.tool_calls:
            # Dispatch each tool call
            for tc in msg.tool_calls:
                fn_name = tc.function.name
                try:
                    fn_args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}

                # Auto-inject image_path for vision calls if not provided
                if fn_name == "diagnose_crop_image" and image_path:
                    fn_args.setdefault("image_path", image_path)

                trace.add("tool_call", f"Orchestrator calls → {fn_name}",
                          f"Arguments: `{json.dumps(fn_args, ensure_ascii=False)}`")

                result_text = _dispatch(fn_name, fn_args, trace)
                tool_results_collected.append(result_text)

                # Feed tool result back to model
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_text,
                })
        else:
            # Model is done calling tools — extract final answer
            final_answer = (msg.content or "").strip()
            if not final_answer and tool_results_collected:
                # Fallback: concatenate tool outputs directly
                final_answer = "\n\n".join(tool_results_collected)
            break
    else:
        final_answer = "\n\n".join(tool_results_collected) or "I was unable to generate a response."

    trace.add("synthesis", "Orchestrator — Final Synthesis",
              f"Combined {len(tool_results_collected)} tool result(s) into final answer.")

    # -- Persist memory --
    append_turn(session_id, "user", user_text)
    append_turn(session_id, "assistant", final_answer[:500])

    # Update crop in memory if we got a diagnosis
    for result in tool_results_collected:
        if "Crop detected:" in result and memory.get("crop") is None:
            for line in result.split("\n"):
                if "Crop detected:" in line:
                    crop_val = line.split(":", 1)[-1].strip(" *")
                    memory["crop"] = crop_val
                    save_memory(session_id, memory)
                    break

    return final_answer
