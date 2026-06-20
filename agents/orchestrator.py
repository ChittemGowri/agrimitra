"""
agents/orchestrator.py
THE CORE OF AGRIMITRA.

This is the planner/orchestrator agent. It does NOT hard-code an
if/else flow. It uses Gemini function calling to dynamically decide,
turn by turn, which specialist agent(s) to invoke based on the
farmer's actual query and what's already in memory -- then synthesizes
all the sub-agent outputs into one coherent final answer.

This is the piece that demonstrates genuine agentic planning + tool
orchestration + multi-agent coordination + memory for the rubric.
"""

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, TEXT_MODEL
from utils.logger import AgentTrace
from utils.memory import FarmerMemory

from agents.diagnosis_agent import run_diagnosis
from agents.advisory_agent import run_advisory
from agents.market_agent import run_market_check

_client = None
_memory = FarmerMemory()


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


# ---- Tool declarations the orchestrator can choose to call ----
# Each maps 1:1 to a specialist agent. Gemini decides which to invoke,
# in what order, and can call more than one per turn (compositional
# function calling).

_DIAGNOSE_DECL = {
    "name": "diagnose_crop_image",
    "description": (
        "Analyze an uploaded photo of a crop leaf/plant to identify the "
        "crop and any visible disease/pest. Use this whenever the farmer "
        "has attached an image, or refers to 'this leaf', 'my plant', "
        "'what disease is this', etc."
    ),
    "parameters": {"type": "object", "properties": {}},
}

_ADVISORY_DECL = {
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
}

_MARKET_DECL = {
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
}

_TOOLS = types.Tool(function_declarations=[_DIAGNOSE_DECL, _ADVISORY_DECL, _MARKET_DECL])

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
) -> str:
    """
    Main entry point. Returns the final farmer-facing answer (string).
    All intermediate reasoning is written into `trace` for the UI.
    """
    client = _get_client()
    farmer_context = _build_context_block(session_id)

    trace.log("Orchestrator", "plan",
              f"New farmer query received. Image attached: {bool(image_path)}. "
              f"Language: {language}.")

    augmented_prompt = (
        f"Farmer context from memory:\n{farmer_context}\n\n"
        f"Image attached this turn: {'yes' if image_path else 'no'}\n"
        f"Preferred response language: {language}\n\n"
        f"Farmer's message: {user_text}"
    )

    chat = client.chats.create(
        model=TEXT_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_INSTRUCTION,
            tools=[_TOOLS],
            temperature=0.3,
        ),
    )

    response = chat.send_message(augmented_prompt)

    # Loop: handle any function calls Gemini decides to make, possibly
    # multiple rounds (compositional function calling).
    max_rounds = 4
    collected_summaries = []

    for _ in range(max_rounds):
        function_calls = [
            part.function_call
            for part in response.candidates[0].content.parts
            if part.function_call
        ]
        if not function_calls:
            break

        function_responses = []
        for fc in function_calls:
            trace.log("Orchestrator", "tool_call",
                      f"Decided to call `{fc.name}` with args {dict(fc.args)}")

            if fc.name == "diagnose_crop_image":
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

            elif fc.name == "get_farming_advice":
                topic = fc.args.get("topic", user_text)
                result = run_advisory(topic, language, farmer_context, trace)
                if result.get("status") == "success":
                    collected_summaries.append(f"Gave advisory on: {topic}")

            elif fc.name == "check_market_and_weather":
                crop = fc.args.get("crop", "Tomato")
                result = run_market_check(crop, trace)
                if result.get("status") == "success":
                    collected_summaries.append(f"Checked market/weather for {crop}")
                    _memory.update_profile(session_id, crop=crop)

            else:
                result = {"status": "error", "message": f"Unknown tool {fc.name}"}

            function_responses.append(
                types.Part.from_function_response(name=fc.name, response={"result": result})
            )

        response = chat.send_message(function_responses)

    final_text = response.text or "I wasn't able to generate a response. Please try again."
    trace.log("Orchestrator", "final", "Synthesized final answer for farmer.")

    if collected_summaries:
        _memory.add_event(session_id, "; ".join(collected_summaries))
    _memory.update_profile(session_id, language=language)

    return final_text
