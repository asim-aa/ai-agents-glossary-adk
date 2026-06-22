import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm


load_dotenv()

os.environ["HOSTED_VLLM_API_BASE"] = os.getenv("HOSTED_VLLM_API_BASE", "")
os.environ["HOSTED_VLLM_API_KEY"] = os.getenv("HOSTED_VLLM_API_KEY", "dummy-key")

MODEL_NAME = os.getenv("SV_MODEL_NAME", "hosted_vllm/openai/gpt-oss-20b")


NO_TOOL_CALLING_RULE = """
IMPORTANT EXECUTION RULE:
You are writing educational Markdown content only.
You do not have access to executable tools, functions, APIs, browsers, or external services.
Never call or invent functions such as search_flights, book_ticket, send_email, web_search, calculator, or any API.
If you mention a tool or API in an example, describe it in prose only.
Do not output function_call JSON, tool-call syntax, executable code, or code-like API invocations.
Return plain Markdown text only.
"""


def safe_instruction(text: str) -> str:
    return text.strip() + "\n\n" + NO_TOOL_CALLING_RULE.strip()


term_planner = LlmAgent(
    name="term_planner",
    model=LiteLlm(model=MODEL_NAME),
    output_key="term_plan",
    instruction=safe_instruction("""
You are the Term Planner.

Create the final term plan for an AI Agents Glossary and Reference Guide.

Return exactly the following 50 terms, organized under exactly these 10 category headings.
Do not rename categories.
Do not add or remove terms.
Do not write definitions yet.

### Core AI agent concepts
1. AI Agent
2. Agentic System
3. Autonomy
4. Goal
5. Environment

### Agent architecture
6. Agent Architecture
7. Agent Loop
8. State
9. Policy
10. Workflow

### Reasoning and planning
11. Reasoning
12. Planning
13. Task Decomposition
14. Reflection
15. Decision Boundary

### Tools and actions
16. Tool Use
17. Tool Calling
18. Action Space
19. API Call
20. Tool Result

### Memory and context
21. Context Window
22. Short-Term Memory
23. Long-Term Memory
24. Episodic Memory
25. State Management

### RAG and knowledge systems
26. Retrieval-Augmented Generation
27. Embedding
28. Vector Database
29. Retriever
30. Grounding

### Multi-agent systems
31. Multi-Agent System
32. Coordinator Agent
33. Specialist Agent
34. Handoff
35. Consensus

### Evaluation and safety
36. Evaluation
37. Test Set
38. Human-in-the-Loop
39. Guardrail
40. Monitoring

### Failure modes
41. Hallucination
42. Tool-Use Error
43. Context Drift
44. Infinite Loop
45. Over-Autonomy

### Prompt and context engineering
46. System Prompt
47. Prompt Engineering
48. Context Engineering
49. Instruction Hierarchy
50. Few-Shot Example

Return only this categorized numbered term list.
"""),
)


definition_writer = LlmAgent(
    name="definition_writer",
    model=LiteLlm(model=MODEL_NAME),
    output_key="definition_draft",
    instruction=safe_instruction("""
You are the Long-Form Definition Writer.

Using the term plan below, write a polished 500-600 token explanation of what an AI agent is.

Term plan:
{term_plan}

The explanation must cover:
- What an AI agent is
- How an agent differs from a normal chatbot
- The observe -> reason -> plan -> act loop
- The role of tools
- The role of memory
- The role of autonomy
- Why agents can fail
- Why evaluation matters
- A simple example of an AI agent

Style requirements:
- Clear
- Beginner-friendly
- Technically accurate
- Practical
- No hype
- No vague buzzwords
- No overly academic language

Return only the definition draft.
"""),
)


definition_reviewer = LlmAgent(
    name="definition_reviewer",
    model=LiteLlm(model=MODEL_NAME),
    output_key="definition_review",
    instruction=safe_instruction("""
You are the Adversarial Definition Reviewer.

Review the AI agent definition below.

Definition draft:
{definition_draft}

Check for:
- Unclear explanations
- Vague wording
- Technical weakness
- Beginner confusion
- Missing concepts
- Weak or missing examples
- Misleading claims
- Hype-driven language

Return a concise review with:
1. Major issues found
2. Required fixes
3. Whether revision is needed

Maximum length: 250 words.

If no major issues remain, say:
No major issues remain. Only minor stylistic improvements are possible.
"""),
)


definition_reviser = LlmAgent(
    name="definition_reviser",
    model=LiteLlm(model=MODEL_NAME),
    output_key="final_definition",
    instruction=safe_instruction("""
You are the Definition Reviser.

Revise the AI agent definition using the reviewer feedback.

Original definition:
{definition_draft}

Reviewer feedback:
{definition_review}

Requirements:
- Keep the final definition around 500-600 tokens.
- Improve clarity, accuracy, examples, and beginner-friendliness.
- Remove vague wording.
- Do not mention the review process.
- Return only the improved final definition.
"""),
)


glossary_writer_a = LlmAgent(
    name="glossary_writer_a",
    model=LiteLlm(model=MODEL_NAME),
    output_key="glossary_part_a",
    instruction=safe_instruction("""
You are Glossary Writer A.

Using the term plan below, write glossary entries for terms 1-25 only.

Term plan:
{term_plan}

You must include only these categories:
### Core AI agent concepts
### Agent architecture
### Reasoning and planning
### Tools and actions
### Memory and context

For each term, use this exact Markdown format:

#### Term Name

**Definition:**  
Explain the term clearly and accurately. Make it detailed enough to teach the concept.

**Why it matters:**  
Explain why this concept is important in AI agent systems.

**Example:**  
Give a simple example that makes the term easier to understand.

**Common confusion:**  
Explain a common misunderstanding, mistake, or ambiguity related to the term.

Requirements:
- Write terms 1-25 only.
- Do not write terms 26-50.
- Preserve the exact category headings listed above.
- Use exactly 25 terms total.
- Be beginner-friendly, practical, and technically accurate.
- Avoid hype, repeated generic explanations, and overly long entries.
- Each entry should be useful but concise.
"""),
)


glossary_writer_b = LlmAgent(
    name="glossary_writer_b",
    model=LiteLlm(model=MODEL_NAME),
    output_key="glossary_part_b",
    instruction=safe_instruction("""
You are Glossary Writer B.

Using the term plan below, write glossary entries for terms 26-50 only.

Term plan:
{term_plan}

You must include only these categories:
### RAG and knowledge systems
### Multi-agent systems
### Evaluation and safety
### Failure modes
### Prompt and context engineering

For each term, use this exact Markdown format:

#### Term Name

**Definition:**  
Explain the term clearly and accurately. Make it detailed enough to teach the concept.

**Why it matters:**  
Explain why this concept is important in AI agent systems.

**Example:**  
Give a simple example that makes the term easier to understand.

**Common confusion:**  
Explain a common misunderstanding, mistake, or ambiguity related to the term.

Requirements:
- Write terms 26-50 only.
- Do not write terms 1-25.
- Preserve the exact category headings listed above.
- Use exactly 25 terms total.
- Be beginner-friendly, practical, and technically accurate.
- Avoid hype, repeated generic explanations, and overly long entries.
- Each entry should be useful but concise.
"""),
)


glossary_reviewer = LlmAgent(
    name="glossary_reviewer",
    model=LiteLlm(model=MODEL_NAME),
    output_key="glossary_review",
    instruction=safe_instruction("""
You are the Adversarial Glossary Reviewer.

Review the combined glossary below.

Glossary part A:
{glossary_part_a}

Glossary part B:
{glossary_part_b}

Your job is to identify only major issues.

Check for:
- Whether there are exactly 50 terms
- Whether all 10 required categories appear
- Missing important AI agent concepts
- Weak or vague definitions
- Technical inaccuracies
- Repeated or overlapping terms
- Weak examples
- Formatting problems
- Confusing beginner language

Return a concise review only.

Do not rewrite the glossary.
Do not review every term one by one unless a term has a serious issue.
Do not produce a full revised glossary.
Do not produce a long essay.

Limit the review to:
1. Major issues found
2. Required fixes
3. Whether revision is needed
4. Final reviewer conclusion

Maximum length: 350 words.

End with one of these exact conclusions:
Revision needed.

or:

No major issues remain. Only minor stylistic improvements are possible.
"""),
)


review_summary_writer = LlmAgent(
    name="review_summary_writer",
    model=LiteLlm(model=MODEL_NAME),
    output_key="review_summary_and_self_critique",
    instruction=safe_instruction("""
You are the Review Summary and Self-Critique Writer.

Using only the definition review and glossary review below, write the final two sections.

Definition review:
{definition_review}

Glossary review:
{glossary_review}

Return exactly these two Markdown sections:

## 3. Adversarial Review Summary

Summarize the major issues found and how they were fixed. Mention improvements to:
- clarity
- technical accuracy
- examples
- organization
- redundancy reduction
- beginner usefulness
- formatting consistency

End this section with this exact sentence:
No major issues remain. Only minor stylistic improvements are possible.

## 4. Final Self-Critique

Answer:
- What does this glossary do well?
- What limitations remain?
- What topics could be expanded later?
- Who is this glossary best suited for?
- What should a learner study next after reading it?

Do not include glossary entries here.
Do not reference internal pipeline mechanics.
Return only sections 3 and 4.
"""),
)


root_agent = SequentialAgent(
    name="ai_agents_glossary",
    description=(
        "A deterministic ADK pipeline that generates and reviews an AI agents "
        "glossary guide. Python handles final assembly and validation."
    ),
    sub_agents=[
        term_planner,
        definition_writer,
        definition_reviewer,
        definition_reviser,
        glossary_writer_a,
        glossary_writer_b,
        glossary_reviewer,
        review_summary_writer,
    ],
)
