# Demo Video Script (2-3 minutes)

You asked for a video -- I can't generate one for you, but here's an
exact script + shot list so you can record it yourself in one take
using your phone screen recorder or OBS/SimpleScreenRecorder on Linux.

Recording on Linux: `sudo apt install simplescreenrecorder` or use
the built-in screen recorder in GNOME (Settings -> Keyboard ->
Ctrl+Shift+Alt+R to start/stop a quick recording).

---

## Shot list

**[0:00-0:15] Hook + problem statement**

Show your face or just voiceover over the AgriMitra UI.

> "Farmers near Madanapalle face three disconnected problems every
> season: identifying crop disease early, knowing what to actually do
> about it, and knowing when to sell. I built AgriMitra -- a
> multi-agent AI system that solves all three in one conversation."

**[0:15-0:30] Architecture (30 seconds, show README diagram or sidebar)**

> "AgriMitra isn't one model -- it's an Orchestrator agent that uses
> Gemini function calling to dynamically plan which of three specialist
> agents to call: a Diagnosis Agent using Gemini Vision, an Advisory
> Agent doing RAG retrieval over real agricultural guides, and a
> Market Agent combining live weather and mandi prices."

Point at the sidebar architecture summary while saying this.

**[0:30-1:15] Live demo 1: image diagnosis**

1. Upload a tomato leaf photo (use one from `data/sample_images/`,
   or take a real photo of a plant -- even a healthy one works)
2. Type: "What's wrong with this leaf and what should I do?"
3. Click "Ask AgriMitra"
4. **While it loads, narrate:** "Watch the reasoning trace on the
   right -- this is the orchestrator deciding, live, to call the
   Diagnosis Agent first, then the Advisory Agent to retrieve
   treatment guidance."
5. Point at the trace panel showing the tool calls in order
6. Read out the final synthesized answer

**[1:15-1:50] Live demo 2: combined multi-agent query**

1. Type: "Is it safe to spray this week, and what's groundnut selling
   for right now?"
2. **Narrate while loading:** "This single question needs the Market
   Agent for both weather AND price -- no image, no disease lookup.
   The orchestrator figures that out itself, it's not hardcoded."
3. Show the trace panel calling only `check_market_and_weather`
4. Read the final answer (price + sell/hold + spray safety note)

**[1:50-2:10] Memory demonstration**

1. Type a follow-up: "What was the crop I asked about earlier?"
2. Show that AgriMitra recalls context from the session
   (this demonstrates persistent memory across turns)

**[2:10-2:30] Close**

> "AgriMitra combines planning, multi-agent orchestration, tool use,
> RAG, and memory -- all the core building blocks from this course --
> applied to a problem I care about personally, agriculture in my own
> region. Code, architecture docs, and a live demo link are all in the
> GitHub repo description."

Show the GitHub repo page briefly, then the live Streamlit Cloud URL
loading in a browser tab.

---

## Tips for a strong recording

- Record at 1280x720 or 1920x1080, not a tiny window
- Zoom your browser to 110-125% so judges can read the trace panel text
- Do a dry run once before the real recording so you know your demo
  queries actually trigger the agents you expect
- If a query is slow (Gemini API + multiple tool calls can take
  5-10 seconds), don't pause the recording -- the loading spinner
  with your narration is exactly the "agent thinking" moment you want
  to show off
- Keep total length under 3 minutes -- judges watch many submissions
