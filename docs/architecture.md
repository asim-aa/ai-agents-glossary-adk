# Architecture Notes: AI Agents Glossary Generator

This document explains the architecture behind the **AI Agents Glossary Generator** project: why it uses a fixed Google ADK pipeline, how the writer-reviewer stages work, why Python handles final assembly and validation, and how the system evolved from a simple generation script into a validated AI content pipeline.

The main `README.md` gives a fast professional overview. This document goes deeper. It is written for students, engineers, and reviewers who want to understand the design decisions behind the implementation.

---

## 1. Project Overview

The AI Agents Glossary Generator is a Python and Google ADK project that generates a structured educational reference guide about AI agents.

The final output is a Markdown document titled:

```text
AI Agents Glossary and Reference Guide
```

The generated guide includes:

* A long-form explanation of what AI agents are
* A categorized 50-term glossary
* An adversarial review summary
* A final self-critique
* A validated final Markdown artifact

The purpose of the project is not simply to ask a model for a long answer. The goal is to demonstrate a more reliable AI generation workflow:

```text
LLM agents generate and critique content.
Python assembles, normalizes, and validates the final artifact.
```

This matters because LLM outputs can be inconsistent. The model may generate too many glossary terms, skip a category, use inconsistent Markdown, or produce extra draft content. The pipeline solves this by separating creative generation from deterministic validation.

---

## 2. High-Level Architecture

```text
                         User Prompt
                              │
                              ▼
                    Google ADK Root Agent
                              │
                              ▼
                       Sequential Pipeline
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   Writer Stages        Reviewer Stages       Reviser Stages
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    Session State Outputs
                              │
                              ▼
                 Python Assembly + Normalization
                              │
                              ▼
                    Candidate Markdown File
                              │
                              ▼
                        Validation Script
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
       Validation Pass                   Validation Fail
             │                                 │
             ▼                                 ▼
   Save Final Markdown Guide        Keep Previous Valid Output
```

The system has two major layers:

```text
Google ADK layer
    ↓
generation, review, and revision

Python layer
    ↓
assembly, cleanup, safety, and validation
```

The ADK agents are responsible for producing educational content. The Python code is responsible for enforcing the final structure.

---

## 3. Why a Sequential Pipeline?

This project uses a fixed sequential pipeline instead of an autonomous routing coordinator.

That design choice is intentional.

A router agent is useful when the system needs to decide which specialist should handle a user's request. This project does not need that. The task is always the same:

```text
Generate a high-quality AI Agents Glossary and Reference Guide.
```

Because the task is fixed, the pipeline should also be fixed.

The goal is not:

```text
Let the model decide what to do next.
```

The goal is:

```text
Guarantee that the same writer-reviewer-reviser process runs in the same order every time.
```

That makes the system easier to debug, easier to explain, and easier to validate.

---

## 4. Pipeline Stages

The Google ADK pipeline runs a sequence of specialized stages.

```text
Term Planner
    ↓
Definition Writer
    ↓
Definition Reviewer
    ↓
Definition Reviser
    ↓
Glossary Writer A
    ↓
Glossary Writer B
    ↓
Glossary Reviewer
    ↓
Review Summary Writer
    ↓
Python Assembly Layer
    ↓
Validator
    ↓
Final Markdown Output
```

Each stage has a specific responsibility.

---

## 5. Term Planner

The Term Planner decides the conceptual scope of the glossary.

It organizes the guide around 50 AI-agent-related terms grouped into 10 required categories:

```text
Core AI agent concepts
Agent architecture
Reasoning and planning
Tools and actions
Memory and context
RAG and knowledge systems
Multi-agent systems
Evaluation and safety
Failure modes
Prompt and context engineering
```

This stage exists because long educational content needs structure before writing begins.

Without planning, the model might over-focus on basic terms and ignore important areas like evaluation, failure modes, RAG, memory, or human oversight.

The planner gives the rest of the pipeline a conceptual map.

---

## 6. Definition Writer

The Definition Writer produces the long-form explanation of what an AI agent is.

This section introduces the reader to the main mental model behind AI agents:

```text
observe → reason → plan → act
```

It explains how an AI agent differs from a normal chatbot, why tools matter, how memory affects behavior, what autonomy means, and why agents can fail.

This stage is important because the glossary should not start with isolated vocabulary. A beginner first needs a broad explanation before studying individual terms.

The long-form definition acts as the foundation for the rest of the guide.

---

## 7. Definition Reviewer

The Definition Reviewer critiques the long-form explanation.

Its job is to look for weaknesses such as:

* vague wording
* missing examples
* confusing explanations
* technical inaccuracies
* unclear distinction between chatbots and agents
* missing discussion of tools, memory, autonomy, or evaluation

This stage gives the project its adversarial review behavior.

The reviewer does not replace the writer. It challenges the writer.

That pattern is useful because the first draft from an LLM often sounds polished but may still contain vague, incomplete, or misleading explanations.

---

## 8. Definition Reviser

The Definition Reviser improves the long-form definition using the review feedback.

This creates a bounded review loop:

```text
Writer creates definition.
Reviewer critiques definition.
Reviser improves definition.
```

The loop is intentionally bounded. The system does not run forever. It performs a defined review-and-revision pass, then moves forward.

That is an important engineering trade-off. Fully autonomous review loops can become slow, expensive, unpredictable, or repetitive. A bounded pipeline gives the benefits of critique while keeping execution predictable.

---

## 9. Glossary Writer A and Glossary Writer B

The glossary is split into two writing stages:

```text
Glossary Writer A → terms 1–25
Glossary Writer B → terms 26–50
```

This split exists because generating 50 detailed glossary entries in one model call can be unreliable. The output may become too long, inconsistent, or truncated.

Splitting the work into two halves makes the task more manageable.

Each glossary entry is expected to include:

```text
Definition:
Why it matters:
Example:
Common confusion:
```

This format makes each term more useful than a one-sentence definition. The goal is for every term to teach the concept, explain why it matters in agent systems, and clarify a common misunderstanding.

---

## 10. Glossary Reviewer

The Glossary Reviewer critiques the full glossary.

It checks for issues such as:

* missing important concepts
* weak definitions
* shallow examples
* redundant terms
* confusing language
* technical inaccuracies
* poor category organization
* missing discussion of limitations or failure modes

The review stage helps the final guide feel more like a learning reference instead of a raw model dump.

The reviewer summary also becomes part of the final artifact. This makes the quality-control process visible to readers.

---

## 11. Review Summary Writer

The Review Summary Writer produces the final adversarial review summary and self-critique.

The output includes:

```text
3. Adversarial Review Summary
4. Final Self-Critique
```

The adversarial review summary explains what weaknesses were found and how they were improved.

The final self-critique explains:

* what the glossary does well
* what limitations remain
* what topics could be expanded later
* who the guide is best suited for
* what a learner should study next

This is important because strong AI-generated educational material should not pretend to be perfect. It should explain its own limitations and recommend next steps.

---

## 12. Why Python Handles Final Assembly

One of the most important design decisions in this project is that Python, not the LLM, assembles the final guide.

The LLM produces content. Python enforces structure.

This separation exists because LLMs are nondeterministic. During development, the model sometimes produced:

* 75 glossary terms instead of 50
* 100 glossary terms because both glossary writers generated all terms
* missing required categories
* inconsistent Markdown headings
* extra draft content inside the final guide
* malformed sections

Instead of relying only on prompting, the Python layer enforces the output contract.

The final assembly step guarantees that the guide follows this structure:

```text
# AI Agents Glossary and Reference Guide

## 1. Long-Form Definition of AI Agents

## 2. The 50-Term Glossary

## 3. Adversarial Review Summary

## 4. Final Self-Critique
```

This design makes the project much more reliable.

---

## 13. Deterministic Glossary Normalization

The pipeline does not blindly trust the glossary writers.

Even if Writer A or Writer B outputs too many terms, the Python layer keeps the final structure stable.

The intended split is:

```text
Writer A:
terms 1–25

Writer B:
terms 26–50
```

The Python normalization layer enforces that split.

This solved a real failure mode. At one point, Writer B generated all 50 terms instead of only terms 26–50. The raw output had 75 total definitions. The validator correctly rejected it.

The fix was to make Python responsible for the final glossary contract:

```text
Only include terms 1–25 from part A.
Only include terms 26–50 from part B.
Guarantee exactly 50 Definition labels.
Guarantee all 10 required categories.
```

This is an example of a broader lesson:

> Prompting is not enough for reliability. Critical structure should be enforced in code.

---

## 14. Candidate-First Output Safety

The pipeline uses a candidate-first output strategy.

Instead of directly overwriting the final guide, the system first writes:

```text
outputs/ai_agents_glossary_guide.candidate.md
```

Then it runs validation.

If validation passes, the candidate file becomes the final output:

```text
outputs/ai_agents_glossary_guide.md
```

If validation fails, the failed attempt is saved for debugging:

```text
outputs/ai_agents_glossary_guide.failed.md
```

This prevents a bad model run from overwriting the last valid output.

The output safety flow is:

```text
Generate candidate
    ↓
Validate candidate
    ↓
Pass?
    ├── Yes → save as final guide
    └── No  → save as failed output and keep previous final guide
```

This pattern is common in production systems: never replace a known-good artifact until the new artifact passes quality checks.

---

## 15. Validation Script

The validation script is the quality-control layer of the project.

It checks that the final Markdown guide contains:

* the required title
* section 1: Long-Form Definition of AI Agents
* section 2: The 50-Term Glossary
* section 3: Adversarial Review Summary
* section 4: Final Self-Critique
* exactly 50 glossary terms
* all 10 required categories
* sufficient document length
* balanced Markdown code fences

The validator counts glossary entries by counting `Definition:` labels inside the glossary section.

That means the final guide must contain exactly 50 `Definition:` entries in section 2.

This is why deterministic assembly matters. The validator gives the project an objective pass/fail signal instead of relying on visual inspection.

---

## 16. Why No Tool Calling?

This project intentionally does not use external tools during generation.

The task is educational writing, not live data retrieval.

The agents are instructed not to call tools, APIs, browsers, or external services. They may discuss tools as concepts, but they do not execute tools.

This keeps the project focused on:

```text
agent orchestration
adversarial review
structured generation
deterministic assembly
validation
```

Rather than mixing in unrelated API dependencies.

This also reduces failure points. The only model dependency is the OpenAI-compatible endpoint used for LLM inference.

---

## 17. Model Access Design

The project uses Google ADK with LiteLLM to connect to an OpenAI-compatible model endpoint.

The environment variables define the backend:

```text
HOSTED_VLLM_API_BASE
HOSTED_VLLM_API_KEY
SV_MODEL_NAME
```

This makes the project provider-flexible.

Although it was developed with the SupportVectors AI Cluster, the same architecture can work with other OpenAI-compatible model endpoints by changing the environment configuration.

The important design idea is:

> Application logic should not be tightly coupled to one specific model provider.

The pipeline stages, validation logic, and Markdown assembly do not depend on a specific model vendor.

---

## 18. Connection Testing

Before running the full ADK pipeline, the project includes a smaller connection test.

The connection test verifies:

1. Environment variables are loaded.
2. The model endpoint is reachable.
3. The configured model appears in the model list.
4. A small chat completion succeeds.

This is useful because the full glossary pipeline is slower and more expensive to debug.

The development flow is:

```text
First prove the cluster works.
Then prove ADK can call the model.
Then run the full pipeline.
Then validate the final guide.
```

This avoids confusing infrastructure failures with pipeline failures.

---

## 19. Message Flow Through the System

When the CLI pipeline runs, the flow looks like this:

```text
run_pipeline.py
    ↓
Create ADK session
    ↓
Create ADK Runner
    ↓
Send glossary prompt
    ↓
Run root_agent sequential pipeline
    ↓
Stream stage events
    ↓
Extract session state
    ↓
Clean long-form definition
    ↓
Normalize glossary part A
    ↓
Normalize glossary part B
    ↓
Repair review summary if needed
    ↓
Assemble final Markdown guide
    ↓
Write candidate file
    ↓
Validate candidate
    ↓
Save final guide if validation passes
```

The terminal prints progress as stages complete:

```text
Stage event from: term_planner
Stage event from: definition_writer
Stage event from: definition_reviewer
Stage event from: definition_reviser
Stage event from: glossary_writer_a
Stage event from: glossary_writer_b
Stage event from: glossary_reviewer
Stage event from: review_summary_writer
```

This visibility makes the pipeline easier to debug because the user can see how far the system progressed.

---

## 20. Why the Project Has Multiple Files

The project is split into multiple files because each file has a different responsibility.

```text
ai_agents_glossary/agent.py
    ↓
Defines the ADK agent pipeline.

scripts/test_connection.py
    ↓
Tests the model endpoint directly.

scripts/run_pipeline.py
    ↓
Runs the full CLI generation pipeline.

scripts/validate_output.py
    ↓
Validates the generated Markdown guide.

outputs/ai_agents_glossary_guide.md
    ↓
Stores the final generated artifact.
```

This separation makes the project easier to understand and maintain.

A single huge script could work, but it would mix together:

* model configuration
* ADK agent definitions
* pipeline execution
* Markdown cleanup
* validation
* output writing

Splitting the responsibilities makes the code more readable and easier to explain in a portfolio review.

---

## 21. Development Timeline

This project grew in phases.

### Phase 0 — Direct Cluster Test

Created a small script to verify the SupportVectors model endpoint.

**Lesson:** Before debugging agent logic, first prove the model endpoint works.

---

### Phase 1 — Hello Agent

Built a minimal ADK agent to verify that Google ADK could call the model through LiteLLM.

**Lesson:** Test the smallest possible ADK workflow before building a full pipeline.

---

### Phase 2 — Initial Glossary Pipeline

Created the first ADK glossary pipeline with planner, writer, reviewer, and glossary stages.

**Lesson:** Multi-stage generation is easier to reason about than one giant prompt.

---

### Phase 3 — CLI Pipeline

Added a command-line runner to execute the full pipeline outside ADK web.

**Lesson:** A project should be runnable and reproducible from the terminal.

---

### Phase 4 — Validation

Added a validation script to check that the output contained the required sections, 50 terms, and 10 categories.

**Lesson:** Generated content should have objective quality gates.

---

### Phase 5 — Deterministic Assembly

Moved final structure enforcement into Python.

**Lesson:** LLMs are good at writing content, but code should enforce contracts.

---

### Phase 6 — Candidate Output Safety

Added candidate and failed output files so invalid generations cannot overwrite the final guide.

**Lesson:** A reliable generation pipeline should protect known-good outputs.

---

## 22. Challenges and Lessons Learned

### LLMs Do Not Always Follow Count Constraints

One of the biggest problems was getting the model to generate exactly 50 terms.

Even with clear prompts, the model sometimes generated too many or too few terms.

The fix was not just more prompting. The better fix was deterministic enforcement in Python.

---

### Long Outputs Are Hard to Control

Long educational documents are more likely to have formatting drift.

The model might start with one Markdown pattern and later switch to another. It might add extra headings, tables, or repeated sections.

This taught an important lesson:

> The longer the output, the more important validation becomes.

---

### Prompting and Programming Serve Different Roles

Prompts are good for guiding style, tone, and content.

Code is better for enforcing exact constraints.

This project uses both:

```text
Prompts guide what the model should write.
Python guarantees what the final artifact must contain.
```

That division made the project much more reliable.

---

### Validation Makes the Project Easier to Trust

Before validation, the only way to judge the output was to read through the Markdown manually.

After validation, the terminal could clearly report:

```text
Validation passed:
- 50 terms found
- 10 categories found
- Required sections found
```

That pass/fail signal made the project easier to debug and easier to present.

---

## 23. Design Trade-offs

This architecture favors reliability over simplicity.

For a small content-generation project, a single prompt and one API call would be much shorter.

However, that simpler version would not demonstrate:

* agent orchestration
* adversarial review
* multi-stage generation
* deterministic assembly
* validation
* output safety

The trade-off is that this project has more files and more structure.

Advantages:

* clearer pipeline stages
* easier debugging
* objective validation
* safer output handling
* stronger portfolio value
* better demonstration of agentic workflow design

Disadvantages:

* more boilerplate
* more moving parts
* slower runtime
* possible model latency
* some cleanup logic required for Markdown formatting

For a quick one-off generation task, this architecture would be excessive. For learning how to build reliable LLM pipelines, the structure is valuable.

---

## 24. Future Improvements

The project is fully functional as a V1, but there are several useful directions for improvement.

### Generalize to Any Topic

The current project is fixed to AI agents.

A future version could accept a topic argument:

```bash
uv run python scripts/run_pipeline.py --topic "machine learning"
```

The planner could then generate categories and terms dynamically.

---

### Use Structured JSON Before Markdown

A future version could require each stage to output structured JSON.

Then Python could render the final Markdown from JSON instead of parsing Markdown.

This would reduce formatting errors and make validation even stronger.

---

### Add Retry Logic

If validation fails, the pipeline could automatically retry once or twice before stopping.

This would make the workflow more robust without requiring manual reruns.

---

### Add Tests

The validator could have unit tests for:

* missing sections
* too many terms
* too few terms
* missing categories
* malformed Markdown
* short or truncated output

---

### Add a Web Interface

A Streamlit or FastAPI interface could make the project easier to demo visually.

The web interface could display:

* current pipeline stage
* generated sections
* validation result
* final Markdown preview

---

### Export to PDF or HTML

The final Markdown guide could be converted to PDF or HTML for easier sharing.

This would make the project feel more like a complete publishing pipeline.

---

## 25. Final Reflection

This project started as an idea for a glossary generator.

It became a lesson in building reliable LLM systems.

The biggest shift was moving from:

```text
How do I make the model generate a good answer?
```

to:

```text
How do I build a system that can generate, review, assemble, and validate a reliable artifact?
```

That shift influenced the whole architecture.

The final system is not just one model call. It is a pipeline:

* the planner scopes the content
* the writer drafts explanations
* the reviewer critiques weaknesses
* the reviser improves the draft
* the glossary writers create structured entries
* the reviewer summarizes remaining issues
* Python assembles the guide
* the validator checks the artifact
* the output safety system protects the final result

This project taught me that building useful AI systems is not only about prompting. It is about designing software around the model so the final result is structured, inspectable, and trustworthy.

The model provides language and reasoning.

The code provides reliability.

That combination is the core architecture of this project.
