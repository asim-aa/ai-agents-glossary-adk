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
If you mention a tool/API in an example, describe it in prose only.
Do not output function_call JSON, tool-call syntax, or code-like API invocations.
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

Create exactly 50 important AI agent-related glossary terms.

Organize them into these categories:

1. Core AI agent concepts
2. Agent architecture
3. Reasoning and planning
4. Tools and actions
5. Memory and context
6. RAG and knowledge systems
7. Multi-agent systems
8. Evaluation and safety
9. Failure modes
10. Prompt and context engineering

Requirements:
- Exactly 50 terms total.
- Number the terms from 1 to 50.
- Include foundational, intermediate, and advanced concepts.
- Return only the categorized numbered term list.
- Do not write definitions yet.
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
You are the Adversarial Reviewer.

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

For each term, use this exact format:

## Term Name

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
- Preserve the category headings from the term plan.
- Be beginner-friendly, practical, and technically accurate.
- Avoid hype and repeated generic explanations.
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

For each term, use this exact format:

## Term Name

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
- Preserve the category headings from the term plan.
- Be beginner-friendly, practical, and technically accurate.
- Avoid hype and repeated generic explanations.
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
- Missing required categories
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


glossary_reviser = LlmAgent(
    name="glossary_reviser",
    model=LiteLlm(model=MODEL_NAME),
    output_key="final_glossary",
    instruction=safe_instruction("""
You are the Glossary Reviser.

Revise the combined glossary using the adversarial review feedback.

Glossary part A:
{glossary_part_a}

Glossary part B:
{glossary_part_b}

Reviewer feedback:
{glossary_review}

Requirements:
- Keep exactly 50 terms total.
- Preserve the required categories.
- Preserve the required per-term format.
- Strengthen weak definitions.
- Clarify vague wording.
- Reduce redundancy.
- Improve examples.
- Fix technical inaccuracies.
- Do not mention the review process inside the glossary.
- Return only the improved final glossary.
- Organize the final glossary under exactly these 10 category headings:
  ### Core AI agent concepts
  ### Agent architecture
  ### Reasoning and planning
  ### Tools and actions
  ### Memory and context
  ### RAG and knowledge systems
  ### Multi-agent systems
  ### Evaluation and safety
  ### Failure modes
  ### Prompt and context engineering
- Every term must use this exact format:
  #### Term Name
  **Definition:**
  **Why it matters:**
  **Example:**
  **Common confusion:**
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


final_assembler = LlmAgent(
    name="final_assembler",
    model=LiteLlm(model=MODEL_NAME),
    output_key="final_guide",
    instruction=safe_instruction("""
You are the Final Assembler.

Assemble a clean final Markdown guide from these provided sections.

Final definition:
{final_definition}

Final glossary:
{final_glossary}

Review summary and self-critique:
{review_summary_and_self_critique}

CRITICAL FORMAT RULES:
You must return the final guide using these exact Markdown headings:

# AI Agents Glossary and Reference Guide

## 1. Long-Form Definition of AI Agents

## 2. The 50-Term Glossary

## 3. Adversarial Review Summary

## 4. Final Self-Critique

Do not rename these headings.
Do not skip any section.
Do not include intermediate drafts.
Do not include reviewer scratch notes.
Do not include hidden reasoning.
Do not mention internal prompts.
Do not mention pipeline mechanics.

The glossary section must contain exactly 10 category headings:

### Core AI agent concepts
### Agent architecture
### Reasoning and planning
### Tools and actions
### Memory and context
### RAG and knowledge systems
### Multi-agent systems
### Evaluation and safety
### Failure modes
### Prompt and context engineering

The glossary must contain exactly 50 terms total.

Every glossary term must use this exact format:

#### Term Name

**Definition:**  
...

**Why it matters:**  
...

**Example:**  
...

**Common confusion:**  
...

Return only the polished final guide in clean Markdown.
"""),
)

root_agent = SequentialAgent(
    name="ai_agents_glossary",
    description="A deterministic ADK pipeline that generates, reviews, and assembles an AI agents glossary guide.",
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