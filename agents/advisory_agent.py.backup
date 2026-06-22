"""
agents/advisory_agent.py
The Advisory Agent: takes a topic/condition (e.g. a diagnosed disease,
or a direct farmer question), retrieves relevant passages from the
local agricultural knowledge base (RAG), then asks Gemini to synthesize
a clear, actionable, farmer-friendly answer -- in English or Telugu.
"""

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, TEXT_MODEL
from tools.retrieval_tool import retrieve_agri_knowledge
from utils.logger import AgentTrace

AGENT_NAME = "AdvisoryAgent"

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


_SYNTHESIS_PROMPT_TEMPLATE = """You are AgriMitra, a friendly and practical
farm advisor for smallholder farmers in Madanapalle, Andhra Pradesh.

Farmer's question/topic: {query}

Relevant agricultural knowledge base passages:
{context}

Farmer context (from memory): {farmer_context}

Write a clear, actionable answer in {language}.
Rules:
- Keep it practical: what to DO, in what order, this week.
- Mention both a low-cost/organic option and a chemical option if the
  knowledge base provides both.
- Keep it to 4-6 short sentences or a short bulleted list -- farmers
  reading this on a phone need it scannable, not a long essay.
- If the knowledge base doesn't fully cover the question, say so
  honestly rather than inventing specifics.
- Do not include any preamble like "Based on the knowledge base" --
  just give the advice directly, as if speaking to the farmer.
"""


def run_advisory(query: str, language: str, farmer_context: str, trace: AgentTrace) -> dict:
    trace.log(AGENT_NAME, "plan", f"Retrieving knowledge base passages for: '{query}'")
    trace.log(AGENT_NAME, "tool_call", "retrieve_agri_knowledge(query)")

    retrieval = retrieve_agri_knowledge(query)
    if retrieval.get("status") != "success":
        trace.log(AGENT_NAME, "error", retrieval.get("message", "Retrieval failed."))
        return retrieval

    sources = retrieval["results"]
    trace.log(
        AGENT_NAME,
        "tool_result",
        f"Retrieved {len(sources)} passage(s) from: "
        f"{', '.join(sorted(set(s['source'] for s in sources)))}",
    )

    context_str = "\n\n".join(f"[{s['source']}]\n{s['text']}" for s in sources)

    prompt = _SYNTHESIS_PROMPT_TEMPLATE.format(
        query=query,
        context=context_str,
        farmer_context=farmer_context,
        language=language,
    )

    trace.log(AGENT_NAME, "tool_call", f"Synthesizing advisory response in {language} via Gemini")

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4),
        )
        advice_text = response.text.strip()
    except Exception as e:
        trace.log(AGENT_NAME, "error", f"Synthesis failed: {e}")
        return {"status": "error", "message": str(e)}

    trace.log(AGENT_NAME, "final", "Advisory response generated.")
    return {
        "status": "success",
        "advice": advice_text,
        "sources_used": sorted(set(s["source"] for s in sources)),
    }
