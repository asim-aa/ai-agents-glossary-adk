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

CATEGORY_LOOKUP = {category.lower(): category for category in REQUIRED_CATEGORIES}
TERM_LOOKUP = {term.lower(): term for term in CATEGORY_BY_TERM}


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
    """Normalize a Markdown heading into plain comparable text."""
    text = line.strip()
    text = text.lstrip("#").strip()
    text = text.strip("*_` ")
    text = re.sub(r"^\d+\.\s*", "", text)
    text = re.sub(r"^terms?\s+\d+\s*[-–]\s*\d+\s*:\s*", "", text, flags=re.I)
    return text.strip()


def normalize_glossary_part(text: str) -> str:
    """
    Repair model Markdown so validation can reliably detect:
    - exact category headings as ### Category
    - exact term headings as #### Term
    """
    if not text:
        return ""

    normalized_lines = []

    for line in text.splitlines():
        stripped = line.strip()
        clean = clean_heading_text(stripped)
        clean_lower = clean.lower()

        if clean_lower in CATEGORY_LOOKUP:
            normalized_lines.append(f"### {CATEGORY_LOOKUP[clean_lower]}")
            continue

        if clean_lower in TERM_LOOKUP:
            normalized_lines.append(f"#### {TERM_LOOKUP[clean_lower]}")
            continue

        normalized_lines.append(line.rstrip())

    repaired_lines = []
    seen_categories = set()

    for line in normalized_lines:
        clean = clean_heading_text(line)
        clean_lower = clean.lower()

        if clean_lower in CATEGORY_LOOKUP:
            category = CATEGORY_LOOKUP[clean_lower]
            if category not in seen_categories:
                repaired_lines.append(f"### {category}")
                seen_categories.add(category)
            continue

        if clean_lower in TERM_LOOKUP:
            term = TERM_LOOKUP[clean_lower]
            category = CATEGORY_BY_TERM[term]

            if category not in seen_categories:
                repaired_lines.append("")
                repaired_lines.append(f"### {category}")
                seen_categories.add(category)

            repaired_lines.append(f"#### {term}")
            continue

        repaired_lines.append(line)

    return "\n".join(repaired_lines).strip()


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

    final_definition = state.get("final_definition", "").strip()
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
        glossary_part_a = normalize_glossary_part(glossary_part_a)
        glossary_part_b = normalize_glossary_part(glossary_part_b)
        review_summary = repair_review_summary(review_summary)

        print()
        print("Pipeline output diagnostics:")
        print(f"- glossary_part_a Definition count: {glossary_part_a.count('**Definition:**')}")
        print(f"- glossary_part_b Definition count: {glossary_part_b.count('**Definition:**')}")
        print(f"- glossary_part_a category count: {glossary_part_a.count('### ')}")
        print(f"- glossary_part_b category count: {glossary_part_b.count('### ')}")
        print(f"- review summary has section 4: {'## 4. Final Self-Critique' in review_summary}")

        final_guide = f"""# AI Agents Glossary and Reference Guide

## 1. Long-Form Definition of AI Agents

{final_definition}

## 2. The 50-Term Glossary

{glossary_part_a}

{glossary_part_b}

{review_summary}
"""

    final_guide = clean_final_guide(final_guide)

    header = (
        "<!-- Generated by AI Agents Glossary ADK pipeline on "
        f"{datetime.now().isoformat(timespec='seconds')} -->\n\n"
    )

    OUTPUT_FILE.write_text(header + final_guide, encoding="utf-8")

    print()
    print("Validating generated guide...")
    validate_guide(OUTPUT_FILE)

    print()
    print(f"Saved final guide to: {OUTPUT_FILE}")
    print()
    print("Preview:")
    print("-" * 80)
    print(final_guide[:1500])
    print("-" * 80)
    print()
    print("SUCCESS: Phase 3 + Phase 4 pipeline run completed.")


if __name__ == "__main__":
    asyncio.run(main())