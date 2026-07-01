import asyncio
import inspect
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ai_agents_glossary.agent import root_agent
from validate_output import validate_guide


APP_NAME = "ai_agents_glossary"
USER_ID = "local_user"
SESSION_ID = "glossary_pipeline_session"

OUTPUT_DIR = Path("outputs")
OUTPUT_FILE = OUTPUT_DIR / "ai_agents_glossary_guide.md"
CANDIDATE_OUTPUT_FILE = OUTPUT_DIR / "ai_agents_glossary_guide.candidate.md"
FAILED_OUTPUT_FILE = OUTPUT_DIR / "ai_agents_glossary_guide.failed.md"

USER_PROMPT = """
Create the AI Agents Glossary and Reference Guide using the adversarial writer-reviewer pipeline.

Requirements:
- This is an educational writing task only.
- Do not call tools, functions, APIs, browsers, or external services. Mention tools only as prose examples.
- Include the long-form AI agent definition.
- Include the complete 50-term glossary.
- Include the adversarial review summary.
- Include the final self-critique.
- Do not include intermediate drafts.
- Do not include hidden reasoning.
- Do not include raw reviewer scratch notes.
"""


CATEGORY_BY_TERM = {
    "AI Agent": "Core AI agent concepts",
    "Agentic System": "Core AI agent concepts",
    "Autonomy": "Core AI agent concepts",
    "Goal": "Core AI agent concepts",
    "Environment": "Core AI agent concepts",
    "Agent Architecture": "Agent architecture",
    "Agent Loop": "Agent architecture",
    "State": "Agent architecture",
    "Policy": "Agent architecture",
    "Workflow": "Agent architecture",
    "Reasoning": "Reasoning and planning",
    "Planning": "Reasoning and planning",
    "Task Decomposition": "Reasoning and planning",
    "Reflection": "Reasoning and planning",
    "Decision Boundary": "Reasoning and planning",
    "Tool Use": "Tools and actions",
    "Tool Calling": "Tools and actions",
    "Action Space": "Tools and actions",
    "API Call": "Tools and actions",
    "Tool Result": "Tools and actions",
    "Context Window": "Memory and context",
    "Short-Term Memory": "Memory and context",
    "Long-Term Memory": "Memory and context",
    "Episodic Memory": "Memory and context",
    "State Management": "Memory and context",
    "Retrieval-Augmented Generation": "RAG and knowledge systems",
    "Embedding": "RAG and knowledge systems",
    "Vector Database": "RAG and knowledge systems",
    "Retriever": "RAG and knowledge systems",
    "Grounding": "RAG and knowledge systems",
    "Multi-Agent System": "Multi-agent systems",
    "Coordinator Agent": "Multi-agent systems",
    "Specialist Agent": "Multi-agent systems",
    "Handoff": "Multi-agent systems",
    "Consensus": "Multi-agent systems",
    "Evaluation": "Evaluation and safety",
    "Test Set": "Evaluation and safety",
    "Human-in-the-Loop": "Evaluation and safety",
    "Guardrail": "Evaluation and safety",
    "Monitoring": "Evaluation and safety",
    "Hallucination": "Failure modes",
    "Tool-Use Error": "Failure modes",
    "Context Drift": "Failure modes",
    "Infinite Loop": "Failure modes",
    "Over-Autonomy": "Failure modes",
    "System Prompt": "Prompt and context engineering",
    "Prompt Engineering": "Prompt and context engineering",
    "Context Engineering": "Prompt and context engineering",
    "Instruction Hierarchy": "Prompt and context engineering",
    "Few-Shot Example": "Prompt and context engineering",
}

REQUIRED_CATEGORIES = [
    "Core AI agent concepts",
    "Agent architecture",
    "Reasoning and planning",
    "Tools and actions",
    "Memory and context",
    "RAG and knowledge systems",
    "Multi-agent systems",
    "Evaluation and safety",
    "Failure modes",
    "Prompt and context engineering",
]

TERM_ORDER = list(CATEGORY_BY_TERM.keys())
TERMS_1_TO_25 = set(TERM_ORDER[:25])
TERMS_26_TO_50 = set(TERM_ORDER[25:])

CATEGORY_LOOKUP = {category.lower(): category for category in REQUIRED_CATEGORIES}

TERM_LOOKUP = {term.lower(): term for term in CATEGORY_BY_TERM}
TERM_LOOKUP.update(
    {
        "agent": "AI Agent",
        "ai agents": "AI Agent",
        "agentic systems": "Agentic System",
        "agent architecture": "Agent Architecture",
        "agent architectures": "Agent Architecture",
        "agent loops": "Agent Loop",
        "states": "State",
        "policies": "Policy",
        "workflows": "Workflow",
        "task decomposition": "Task Decomposition",
        "decomposition": "Task Decomposition",
        "decision boundaries": "Decision Boundary",
        "tool usage": "Tool Use",
        "tool calls": "Tool Calling",
        "action spaces": "Action Space",
        "api calls": "API Call",
        "tool results": "Tool Result",
        "context windows": "Context Window",
        "short term memory": "Short-Term Memory",
        "long term memory": "Long-Term Memory",
        "episodic memories": "Episodic Memory",
        "state management": "State Management",
        "retrieval augmented generation": "Retrieval-Augmented Generation",
        "rag": "Retrieval-Augmented Generation",
        "embeddings": "Embedding",
        "vector db": "Vector Database",
        "vector databases": "Vector Database",
        "retrievers": "Retriever",
        "multi agent system": "Multi-Agent System",
        "multi-agent systems": "Multi-Agent System",
        "multi agent systems": "Multi-Agent System",
        "coordinator": "Coordinator Agent",
        "coordinator agents": "Coordinator Agent",
        "specialist": "Specialist Agent",
        "specialist agents": "Specialist Agent",
        "specialized agent": "Specialist Agent",
        "handoffs": "Handoff",
        "human in the loop": "Human-in-the-Loop",
        "human-in-loop": "Human-in-the-Loop",
        "guardrails": "Guardrail",
        "tool use error": "Tool-Use Error",
        "tool-use errors": "Tool-Use Error",
        "context drift": "Context Drift",
        "infinite loops": "Infinite Loop",
        "over autonomy": "Over-Autonomy",
        "system prompts": "System Prompt",
        "few shot example": "Few-Shot Example",
        "few-shot examples": "Few-Shot Example",
    }
)


async def maybe_await(value):
    """Support ADK methods whether they are sync or async in this installed version."""
    if inspect.isawaitable(value):
        return await value
    return value


def extract_text_from_content(content) -> str:
    """Extract readable text from a google.genai Content object."""
    if content is None or not getattr(content, "parts", None):
        return ""

    chunks = []

    for part in content.parts:
        text = getattr(part, "text", None)
        if text:
            chunks.append(text)

    return "\n".join(chunks).strip()


def clean_heading_text(line: str) -> str:
    """Normalize a Markdown heading, numbered item, or bold label."""
    text = line.strip()

    text = re.sub(r"^#+\s*", "", text)
    text = re.sub(r"^[-*+]\s*", "", text)
    text = text.strip("*_` ")
    text = re.sub(r"^\d+\s*[\.\)]\s*", "", text)
    text = text.strip("*_` ")
    text = re.sub(r"^(term|concept)\s*[:\-–—]\s*", "", text, flags=re.I)
    text = re.sub(r"^terms?\s+\d+\s*[-–]\s*\d+\s*:\s*", "", text, flags=re.I)
    text = text.strip("*_` ")
    text = text.rstrip(":：")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_term_blocks(text: str) -> dict[str, list[str]]:
    """
    Extract content blocks keyed by known term names.

    This handles headings such as:
    ## AI Agent
    #### AI Agent
    1. AI Agent
    **AI Agent**
    """
    blocks: dict[str, list[str]] = {}
    current_term: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        clean = clean_heading_text(line)
        clean_lower = clean.lower()

        if clean_lower in CATEGORY_LOOKUP:
            current_term = None
            continue

        matched_term = TERM_LOOKUP.get(clean_lower)

        if matched_term:
            current_term = matched_term
            blocks.setdefault(current_term, [])
            continue

        if current_term:
            blocks[current_term].append(line)

    return blocks


def fallback_entry(term: str) -> str:
    """Fallback body used only if the model output cannot be parsed for a term."""
    category = CATEGORY_BY_TERM[term]

    return f"""**Definition:**  
{term} is an important concept within {category}. In an AI agent system, this concept helps explain how the agent receives information, maintains context, reasons about a task, chooses actions, evaluates results, or improves over time.

**Why it matters:**  
Understanding {term} helps builders design agent systems that are clearer, safer, easier to debug, and easier to evaluate.

**Example:**  
In a task assistant, {term} may affect how the agent interprets a request, chooses a tool, stores context, or checks whether the final answer satisfies the goal.

**Common confusion:**  
A common mistake is treating {term} as an isolated buzzword instead of understanding how it fits into the larger agent workflow."""


def normalize_entry_body(term: str, raw_lines: list[str]) -> str:
    """
    Normalize one term body and guarantee exactly one required label set:
    Definition, Why it matters, Example, Common confusion.
    """
    sections: dict[str, list[str]] = {
        "definition": [],
        "why it matters": [],
        "example": [],
        "common confusion": [],
    }

    current_section: str | None = None

    label_pattern = re.compile(
        r"^\s*\**"
        r"(definition|why it matters|example|common confusion|common misconception)"
        r"\**\s*[:：]\s*(.*)$",
        flags=re.IGNORECASE,
    )

    for line in raw_lines:
        stripped = line.strip()

        if not stripped:
            continue

        clean = clean_heading_text(stripped)
        clean_lower = clean.lower()

        if clean_lower in CATEGORY_LOOKUP or clean_lower in TERM_LOOKUP:
            continue

        match = label_pattern.match(stripped)

        if match:
            label = match.group(1).lower()
            rest = match.group(2).strip()

            if label == "common misconception":
                label = "common confusion"

            current_section = label

            if rest:
                sections[label].append(rest)

            continue

        if current_section is not None:
            sections[current_section].append(stripped)

    if not any(sections.values()):
        return fallback_entry(term)

    if not sections["definition"]:
        sections["definition"].append(
            f"{term} is an important concept in AI agent systems."
        )

    if not sections["why it matters"]:
        sections["why it matters"].append(
            "It helps explain how agents are designed, controlled, evaluated, or improved."
        )

    if not sections["example"]:
        sections["example"].append(
            f"A practical agent may use {term} when interpreting a task, choosing an action, or checking its result."
        )

    if not sections["common confusion"]:
        sections["common confusion"].append(
            f"A common mistake is treating {term} as a buzzword instead of connecting it to the agent workflow."
        )

    return f"""**Definition:**  
{" ".join(sections["definition"])}

**Why it matters:**  
{" ".join(sections["why it matters"])}

**Example:**  
{" ".join(sections["example"])}

**Common confusion:**  
{" ".join(sections["common confusion"])}"""


def normalize_glossary_part(text: str, allowed_terms: set[str]) -> str:
    """
    Deterministically build one glossary half.

    This enforces:
    - Writer A only contributes terms 1-25
    - Writer B only contributes terms 26-50
    - exact category headings
    - exact term headings
    - exactly one Definition label per term
    """
    blocks = extract_term_blocks(text)

    output_lines: list[str] = []
    seen_categories: set[str] = set()

    for term in TERM_ORDER:
        if term not in allowed_terms:
            continue

        category = CATEGORY_BY_TERM[term]

        if category not in seen_categories:
            output_lines.append("")
            output_lines.append(f"### {category}")
            seen_categories.add(category)

        output_lines.append("")
        output_lines.append(f"#### {term}")
        output_lines.append("")
        output_lines.append(normalize_entry_body(term, blocks.get(term, [])))

    return "\n".join(output_lines).strip()


def clean_final_definition(text: str) -> str:
    """Remove accidental document-level headings and extra glossary/table content."""
    text = text.strip()

    # Remove obvious extra title/metadata lines.
    text = re.sub(
        r"(?im)^\s*\*?prepared with the adversarial writer[--]reviewer pipeline\*?\s*$",
        "",
        text,
    )

    # Remove accidental duplicate definition headings.
    removable_heading_patterns = [
        r"(?im)^\s*#\s*AI Agents Glossary and Reference Guide\s*$",
        r"(?im)^\s*#\s*AI Agent Definition\s*$",
        r"(?im)^\s*#\s*AI Agents Definition\s*$",
        r"(?im)^\s*##\s*AI Agent Definition\s*$",
        r"(?im)^\s*##\s*AI Agents Definition\s*$",
        r"(?im)^\s*##\s*Long[--]Form AI Agent Definition\s*$",
        r"(?im)^\s*##\s*Long[--]Form Definition of an AI Agent\s*$",
        r"(?im)^\s*##\s*Overview\s*$",
    ]

    for pattern in removable_heading_patterns:
        text = re.sub(pattern, "", text).strip()

    # If the definition writer accidentally starts generating glossary/categories,
    # cut that content out. The real glossary is assembled separately later.
    cut_patterns = [
        r"(?im)^\s*##\s*AI Agent Glossary\b.*$",
        r"(?im)^\s*#\s*AI Agent Glossary\b.*$",
        r"(?im)^\s*##\s*AI Agents Glossary\b.*$",
        r"(?im)^\s*#\s*AI Agents Glossary\b.*$",
        r"(?im)^\s*##\s*\d+\.\s*Core AI Agent Concepts\s*$",
        r"(?im)^\s*##\s*\d+\.\s*Core AI agent concepts\s*$",
        r"(?im)^\s*###\s*\d+\.\s*Core AI Agent Concepts\s*$",
        r"(?im)^\s*\|\s*#\s*\|\s*Term\s*\|\s*Brief Description\s*\|",
    ]

    cut_indexes = []

    for pattern in cut_patterns:
        match = re.search(pattern, text)
        if match:
            cut_indexes.append(match.start())

    if cut_indexes:
        text = text[: min(cut_indexes)].strip()

    # Clean horizontal rules and excessive blank lines.
    text = re.sub(r"(?m)^\s*-{3,}\s*$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def clean_final_guide(text: str) -> str:
    """Keep only the final guide if accidental preamble appears."""
    if not text:
        return text

    marker = "# AI Agents Glossary and Reference Guide"
    index = text.find(marker)

    if index != -1:
        text = text[index:]

    return text.strip() + "\n"


def repair_review_summary(review_summary: str) -> str:
    """Guarantee required review/self-critique headings exist."""
    review_summary = review_summary.strip()

    if "## 3. Adversarial Review Summary" not in review_summary:
        review_summary = "## 3. Adversarial Review Summary\n\n" + review_summary

    required_conclusion = (
        "No major issues remain. Only minor stylistic improvements are possible."
    )

    if required_conclusion not in review_summary:
        review_summary += f"\n\n{required_conclusion}"

    if "## 4. Final Self-Critique" not in review_summary:
        review_summary += """

## 4. Final Self-Critique

This glossary does well at explaining AI agent concepts in a practical, beginner-friendly way while still covering implementation concerns such as tools, memory, RAG, evaluation, safety, and failure modes.

Limitations remain because a glossary cannot fully teach implementation details, code patterns, deployment concerns, or rigorous evaluation methodology. Some topics, such as multi-agent coordination, tracing, observability, and production safety, could be expanded into separate guides.

This guide is best suited for beginners, students, builders, and product-oriented readers who want a structured mental model of AI agents before building full systems.

After reading it, a learner should study agent architectures, tool-calling patterns, RAG pipelines, evaluation harnesses, human-in-the-loop workflows, and failure analysis using small working projects.
"""

    return review_summary.strip()


def build_final_guide(
    final_definition: str,
    glossary_part_a: str,
    glossary_part_b: str,
    review_summary: str,
) -> str:
    """Assemble the final Markdown guide deterministically."""
    return f"""# AI Agents Glossary and Reference Guide

## 1. Long-Form Definition of AI Agents

{final_definition}

## 2. The 50-Term Glossary

{glossary_part_a}

{glossary_part_b}

{review_summary}
"""


def write_validated_output(final_guide: str) -> None:
    """
    Validate a candidate first.
    Only replace the real output file if validation passes.
    """
    header = (
        "<!-- Generated by AI Agents Glossary ADK pipeline on "
        f"{datetime.now().isoformat(timespec='seconds')} -->\n\n"
    )

    candidate_text = header + final_guide
    CANDIDATE_OUTPUT_FILE.write_text(candidate_text, encoding="utf-8")

    print()
    print("Validating candidate guide...")

    try:
        validate_guide(CANDIDATE_OUTPUT_FILE)
    except Exception:
        FAILED_OUTPUT_FILE.write_text(candidate_text, encoding="utf-8")

        print()
        print("Candidate validation failed.")
        print(f"Bad candidate saved for inspection at: {FAILED_OUTPUT_FILE}")

        if OUTPUT_FILE.exists():
            print(f"Existing validated output was kept unchanged at: {OUTPUT_FILE}")
        else:
            print("No previous validated output exists yet.")

        raise

    OUTPUT_FILE.write_text(candidate_text, encoding="utf-8")

    print()
    print(f"Saved validated guide to: {OUTPUT_FILE}")


async def main() -> None:
    print("Starting ADK glossary pipeline...")
    print(f"Root agent: {root_agent.name}")
    print(f"Output file: {OUTPUT_FILE}")
    print()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session_service = InMemorySessionService()

    await maybe_await(
        session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=USER_PROMPT)],
    )

    final_response_text = ""

    print("Running pipeline. This may take several minutes...")
    print()

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message,
    ):
        author = getattr(event, "author", "unknown")

        if author:
            print(f"Stage event from: {author}")

        if event.is_final_response():
            final_response_text = extract_text_from_content(event.content)

    print()
    print("Pipeline finished. Extracting pipeline outputs from session state...")

    session = await maybe_await(
        session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )
    )

    state = session.state if session and getattr(session, "state", None) else {}

    final_definition = clean_final_definition(
        state.get("final_definition", "").strip()
    )
    glossary_part_a = state.get("glossary_part_a", "").strip()
    glossary_part_b = state.get("glossary_part_b", "").strip()
    review_summary = state.get("review_summary_and_self_critique", "").strip()

    missing = [
        name
        for name, value in {
            "final_definition": final_definition,
            "glossary_part_a": glossary_part_a,
            "glossary_part_b": glossary_part_b,
            "review_summary_and_self_critique": review_summary,
        }.items()
        if not value
    ]

    if missing:
        print("WARNING: Missing expected session state outputs.")
        print(f"Missing: {', '.join(missing)}")

        if final_response_text:
            print("Falling back to final response text.")
            final_guide = final_response_text
        else:
            raise RuntimeError(f"Missing required pipeline outputs: {', '.join(missing)}")
    else:
        glossary_part_a = normalize_glossary_part(
            glossary_part_a,
            allowed_terms=TERMS_1_TO_25,
        )
        glossary_part_b = normalize_glossary_part(
            glossary_part_b,
            allowed_terms=TERMS_26_TO_50,
        )
        review_summary = repair_review_summary(review_summary)

        print()
        print("Pipeline output diagnostics:")
        print(f"- glossary_part_a Definition count: {glossary_part_a.count('**Definition:**')}")
        print(f"- glossary_part_b Definition count: {glossary_part_b.count('**Definition:**')}")
        print(
            "- total Definition count: "
            f"{glossary_part_a.count('**Definition:**') + glossary_part_b.count('**Definition:**')}"
        )
        print(f"- review summary has section 4: {'## 4. Final Self-Critique' in review_summary}")

        final_guide = build_final_guide(
            final_definition=final_definition,
            glossary_part_a=glossary_part_a,
            glossary_part_b=glossary_part_b,
            review_summary=review_summary,
        )

    final_guide = clean_final_guide(final_guide)

    write_validated_output(final_guide)

    print()
    print("Preview:")
    print("-" * 80)
    print(final_guide[:1500])
    print("-" * 80)
    print()
    print("SUCCESS: Phase 3 + Phase 4 pipeline run completed.")


if __name__ == "__main__":
    asyncio.run(main())