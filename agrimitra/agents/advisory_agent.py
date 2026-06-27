"""
agents/advisory_agent.py
Retrieves relevant chunks from the knowledge base and synthesises
practical farming advice using the NVIDIA NIM text model.
"""

from openai import OpenAI

from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, TEXT_MODEL
from tools.retrieval_tool import retrieve
from utils.logger import AgentTrace


def run(query: str, diagnosis_context: str = "", trace: AgentTrace | None = None) -> str:
    """
    Retrieve knowledge-base chunks relevant to the query + diagnosis,
    then synthesise actionable advice.
    Returns a formatted advice string.
    """
    if not NVIDIA_API_KEY:
        return "⚠️ NVIDIA_API_KEY not set — Advisory Agent cannot run."

    # Build a richer search query combining user question and diagnosis
    search_q = query
    if diagnosis_context:
        search_q = f"{diagnosis_context} {query}"

    if trace:
        trace.add("tool_call", "Advisory Agent → RAG Retrieval",
                  f"Searching knowledge base for: _{search_q[:120]}_")

    chunks = retrieve(search_q, top_k=4)

    if trace:
        snippet = chunks[0][:200] + "…" if chunks else "(none)"
        trace.add("tool_result", "RAG — Top Retrieved Chunk", f"```\n{snippet}\n```")

    context_text = "\n\n---\n\n".join(chunks)

    system_prompt = (
        "You are AgriMitra, a knowledgeable and empathetic farm advisor for "
        "smallholder farmers in the Madanapalle region of Andhra Pradesh, India. "
        "You always give practical, step-by-step advice grounded in the provided "
        "agricultural extension documents. "
        "Keep answers concise (under 200 words), use simple English, "
        "and end with one clear action item."
    )

    user_prompt = (
        f"Farmer's question: {query}\n\n"
        + (f"Disease/issue context: {diagnosis_context}\n\n" if diagnosis_context else "")
        + f"Relevant knowledge-base excerpts:\n{context_text}\n\n"
        + "Based only on the above documents and your agronomic expertise, "
          "give practical advice to the farmer."
    )

    client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)

    if trace:
        trace.add("tool_call", "Advisory Agent → LLM Synthesis",
                  f"Synthesising advice with **{TEXT_MODEL}**…")

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=350,
            temperature=0.3,
        )
        advice = response.choices[0].message.content.strip()
        if trace:
            trace.add("tool_result", "Advisory Agent — Output",
                      advice[:300] + ("…" if len(advice) > 300 else ""))
        return f"📚 **Advisory Guidance:**\n{advice}"
    except Exception as e:
        return f"⚠️ Advisory Agent error: {e}"
