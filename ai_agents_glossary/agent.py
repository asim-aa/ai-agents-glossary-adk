import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm


load_dotenv()

os.environ["HOSTED_VLLM_API_BASE"] = os.getenv("HOSTED_VLLM_API_BASE", "")
os.environ["HOSTED_VLLM_API_KEY"] = os.getenv("HOSTED_VLLM_API_KEY", "dummy-key")

MODEL_NAME = os.getenv("SV_MODEL_NAME", "hosted_vllm/openai/gpt-oss-20b")


term_planner = LlmAgent(
    name="term_planner",
    model=LiteLlm(model=MODEL_NAME),
    output_key="term_plan",
    instruction="""
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
""",
)


definition_writer = LlmAgent(
    name="definition_writer",
    model=LiteLlm(model=MODEL_NAME),
    output_key="definition_draft",
    instruction="""
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
""",
)


definition_reviewer = LlmAgent(
    name="definition_reviewer",
    model=LiteLlm(model=MODEL_NAME),
    output_key="definition_review",
    instruction="""
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
""",
)


definition_reviser = LlmAgent(
    name="definition_reviser",
    model=LiteLlm(model=MODEL_NAME),
    output_key="final_definition",
    instruction="""
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
""",
)


glossary_writer_a = LlmAgent(
    name="glossary_writer_a",
    model=LiteLlm(model=MODEL_NAME),
    output_key="glossary_part_a",
    instruction="""
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
""",
)


glossary_writer_b = LlmAgent(
    name="glossary_writer_b",
    model=LiteLlm(model=MODEL_NAME),
    output_key="glossary_part_b",
    instruction="""
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
""",
)


glossary_reviewer = LlmAgent(
    name="glossary_reviewer",
    model=LiteLlm(model=MODEL_NAME),
    output_key="glossary_review",
    instruction="""
You are the Adversarial Glossary Reviewer.

Review the combined glossary below.

Glossary part A:
{glossary_part_a}

Glossary part B:
{glossary_part_b}

Check for:
- Whether there are exactly 50 terms
- Missing important concepts
- Weak definitions
- Vague explanations
- Misleading wording
- Technical inaccuracies
- Overlapping or redundant terms
- Missing examples
- Poor organization
- Confusing beginner language
- Shallow explanations

Return:
1. Major issues found
2. Required fixes
3. Whether revision is needed
4. Final reviewer conclusion

If no major issues remain, say:
No major issues remain. Only minor stylistic improvements are possible.
""",
)


glossary_reviser = LlmAgent(
    name="glossary_reviser",
    model=LiteLlm(model=MODEL_NAME),
    output_key="final_glossary",
    instruction="""
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
""",
)


review_summary_writer = LlmAgent(
    name="review_summary_writer",
    model=LiteLlm(model=MODEL_NAME),
    output_key="review_summary_and_self_critique",
    instruction="""
You are the Review Summary and Self-Critique Writer.

Using the definition review and glossary review below, write the final two sections.

Definition review:
{definition_review}

Glossary review:
{glossary_review}

Write:

## 3. Adversarial Review Summary

Summarize:
- Major issues found
- How definitions were improved
- How vague wording was clarified
- How examples were strengthened
- How redundancy was reduced
- How technical accuracy was improved

End this section with:
No major issues remain. Only minor stylistic improvements are possible.

## 4. Final Self-Critique

Answer:
- What does this glossary do well?
- What limitations remain?
- What topics could be expanded later?
- Who is this glossary best suited for?
- What should a learner study next after reading it?

Use a clear, honest, instructional tone.
""",
)


final_assembler = LlmAgent(
    name="final_assembler",
    model=LiteLlm(model=MODEL_NAME),
    output_key="final_guide",
    instruction="""
You are the Final Assembler.

Assemble the final guide using the provided sections.

Final definition:
{final_definition}

Final glossary:
{final_glossary}

Review summary and self-critique:
{review_summary_and_self_critique}

Return the final guide in this exact structure:

# AI Agents Glossary and Reference Guide

## 1. Long-Form Definition of AI Agents

[insert the final definition here]

## 2. The 50-Term Glossary

[insert the final glossary here]

[insert the review summary and self-critique here]

Important:
- Use clean Markdown.
- Preserve the final definition and final glossary content.
- Do not show intermediate drafts.
- Do not show hidden reasoning.
- Do not mention internal prompts.
- Return only the polished final guide.
""",
)


root_agent = SequentialAgent(
    name="ai_agents_glossary",
    description="A deterministic ADK pipeline that generates, reviews, revises, and assembles an AI agents glossary guide.",
    sub_agents=[
        term_planner,
        definition_writer,
        definition_reviewer,
        definition_reviser,
        glossary_writer_a,
        glossary_writer_b,
        glossary_reviewer,
        glossary_reviser,
        review_summary_writer,
        final_assembler,
    ],
)