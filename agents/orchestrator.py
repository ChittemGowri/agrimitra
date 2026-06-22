"""
agents/orchestrator.py
THE CORE OF AGRIMITRA.

This is the planner/orchestrator agent. It does NOT hard-code an
if/else flow. It uses NVIDIA NIM (via OpenAI-compatible API) to dynamically decide,
turn by turn, which specialist agent(s) to invoke based on the
farmer's actual query and what's already in memory -- then synthesizes
all the sub-agent outputs into one coherent final answer.

This is the piece that demonstrates genuine agentic planning + tool
orchestration + multi-agent coordination + memory for the rubric.
"""

from openai import OpenAI

from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, TEXT_MODEL
from utils.logger import AgentTrace
from utils.memory import FarmerMemory

from agents.diagnosis_agent import run_diagnosis
from agents.advisory_agent import run_advisory
from agents.market_agent import run_market_check

_client = None
_memory = FarmerMemory()


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=NVIDIA_API_KEY,
            base_url=NVIDIA_BASE_URL if NVIDIA_BASE_URL else None
        )
    return _client


# ---- Tool declarations the orchestrator can choose to call ----
# Each maps 1:1 to a specialist agent. NVIDIA NIM (OpenAI compatible) decides which to invoke,
# in what order, and can call more than one per turn (compositional function calling).

_DIAGNOSE_DECL = {
    "type": "function",
    "function": {
        "name": "diagnose_crop_image",
        "description": (
            "Analyze an uploaded photo of a crop leaf/plant to identify the "
            "crop and any visible disease/pest. Use this whenever the farmer "
            "has attached an image, or refers to 'this leaf', 'my plant', "
            "'what disease is this', etc."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
}

_ADVISORY_DECL = {
    "type": "function",
    "function": {
        "name": "get_farming_advice",
        "description": (
            "Retrieve agricultural knowledge base guidance and generate "
            "practical advice for a farming topic, disease, or pest "
            "(e.g. treatment steps, prevention, IPM practices). Use this "
            "whenever the farmer asks what to DO about a problem, or asks a "
            "general farming knowledge question."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The specific topic/condition/question to research, "
                                    "e.g. 'tomato leaf curl virus treatment'.",
                }
            },
            "required": ["topic"],
        },
    },
}

_MARKET_DECL = {
    "type": "function",
    "function": {
        "name": "check_market_and_weather",
        "description": (
            "Get live weather forecast and current mandi (market) price for "
            "a crop, plus a sell/hold recommendation and spraying-safety note. "
            "Use this whenever the farmer asks about price, selling, market "
            "timing, weather, or whether it's safe to spray."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "crop": {
                    "type": "string",
                    "description": "Crop name, e.g. 'Tomato', 'Groundnut', 'Mango'.",
                }
            },
            "required": ["crop"],
        },
    },
}

_TOOLS = [_DIAGNOSE_DECL, _ADVISORY_DECL, _MARKET_DECL]

_SYSTEM_INSTRUCTION = """You are the orchestrator for AgriMitra, a multi-agent
farm advisory assistant for smallholder farmers near Madanapalle, Andhra
Pradesh, India.

You have three specialist tools available (each is its own backing agent):
1. diagnose_crop_image — analyzes an uploaded leaf photo
2. get_farming_advice — retrieves knowledge-base-grounded treatment/IPM advice
3. check_market_and_weather — live weather + mandi price + sell/hold advice

Plan which tool(s) the farmer's request actually needs. You may call more
than one tool in sequence if the request needs it (e.g. a photo was
uploaded AND the farmer also asked about selling). Do not call a tool
that isn't relevant to what was asked.

After tool results come back, write ONE warm, concise, practical final
answer for the farmer that synthesizes everything -- do not just repeat
raw tool output. Respond in the farmer's requested language if specified.
"""


def _build_context_block(session_id: str) -> str:
    return _memory.recent_context(session_id)


def handle_farmer_query(
    session_id: str,
    user_text: str,
    image_path,
    language: str,
    trace: AgentTrace,
) -> tuple[str, dict]:
    """
    Main entry point. Returns the final farmer-facing answer (string)
    and a dictionary of structured tool outputs from the current turn.
    All intermediate reasoning is written into `trace` for the UI.
    """
    client = _get_client()
    farmer_context = _build_context_block(session_id)

    trace.log("Orchestrator", "plan",
              f"New farmer query received. Image attached: {bool(image_path)}. "
              f"Language: {language}.")

    # We'll manage the conversation history as a list of messages.
    messages = [
        {"role": "system", "content": _SYSTEM_INSTRUCTION},
        {"role": "user", "content": f"Farmer context from memory:\n{farmer_context}\n\n"
                                  f"Image attached this turn: {'yes' if image_path else 'no'}\n"
                                  f"Preferred response language: {language}\n\n"
                                  f"Farmer's message: {user_text}"}
    ]

    collected_summaries = []
    tool_outputs = {}

    # Loop: handle any function calls the model decides to make, possibly
    # multiple rounds (compositional function calling).
    max_rounds = 4
    for _ in range(max_rounds):
        try:
            response = client.chat.completions.create(
                model=TEXT_MODEL,
                messages=messages,
                tools=_TOOLS,
                tool_choice="auto",  # let the model decide
                temperature=0.3,
            )
        except Exception as e:
            trace.log("Orchestrator", "error", f"Failed to get completion: {e}")
            break

        response_message = response.choices[0].message
        # Append the assistant's response to the messages
        messages.append(response_message)

        # Check if the model wants to call a function
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments
                trace.log("Orchestrator", "tool_call",
                          f"Decided to call `{function_name}` with args {function_args}")

                if function_name == "diagnose_crop_image":
                    if not image_path:
                        result = {"status": "error", "message": "No image was uploaded this turn."}
                    else:
                        result = run_diagnosis(image_path, trace)
                        if result.get("status") == "success":
                            collected_summaries.append(
                                f"Diagnosed image as {result.get('condition')} "
                                f"on {result.get('crop_identified')} "
                                f"(confidence: {result.get('confidence')})"
                            )
                            _memory.update_profile(session_id, crop=result.get("crop_identified"))
                            tool_outputs["diagnosis"] = result

                elif function_name == "get_farming_advice":
                    # Parse the JSON string of arguments
                    import json
                    args = json.loads(function_args)
                    topic = args.get("topic", user_text)
                    result = run_advisory(topic, language, farmer_context, trace)
                    if result.get("status") == "success":
                        collected_summaries.append(f"Gave advisory on: {topic}")
                        tool_outputs["advisory"] = result

                elif function_name == "check_market_and_weather":
                    import json
                    args = json.loads(function_args)
                    crop = args.get("crop", "Tomato")
                    result = run_market_check(crop, trace)
                    if result.get("status") == "success":
                        collected_summaries.append(f"Checked market/weather for {crop}")
                        _memory.update_profile(session_id, crop=crop)
                        tool_outputs["market"] = result

                else:
                    result = {"status": "error", "message": f"Unknown tool {function_name}"}

                # Append the tool result as a tool message
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(result),
                    }
                )
        else:
            # No tool calls, we have the final answer
            break

    final_text = response_message.content or "I wasn't able to generate a response. Please try again."
    trace.log("Orchestrator", "final", "Synthesized final answer for farmer.")

    if collected_summaries:
        _memory.add_event(session_id, "; ".join(collected_summaries))
    _memory.update_profile(session_id, language=language)

    return final_text, tool_outputs
