# 🤖 AI Agents Glossary Generator

A validated multi-agent glossary generation pipeline built with **Google ADK**, Python, LiteLLM, and an OpenAI-compatible model endpoint.

This project generates a polished **AI Agents Glossary and Reference Guide** using a bounded adversarial writer-reviewer workflow. Instead of asking one model to produce a long document in one shot, the system decomposes the writing task into multiple stages: planning, definition writing, review, revision, glossary generation, adversarial critique, deterministic assembly, and validation.

The final result is a structured Markdown guide containing:

* A long-form explanation of what AI agents are
* A categorized 50-term AI agents glossary
* An adversarial review summary
* A final self-critique
* Automated validation to confirm the guide is complete

Although this project was developed using the **SupportVectors AI Cluster**, the architecture works with any OpenAI-compatible endpoint supported through LiteLLM, such as OpenAI, Azure OpenAI, Ollama, vLLM, Together AI, or a private hosted model server.

---

## Features

* 🧠 **Google ADK Agent Pipeline** for structured multi-stage generation
* ✍️ **Glossary Writer Agent** for educational content generation
* 🔍 **Adversarial Reviewer Agent** for critique and quality improvement
* 🔁 **Definition Review + Revision Flow** for improving the main explanation
* 📚 **50-Term AI Agents Glossary** organized into required categories
* 🧩 **Deterministic Python Assembly Layer** to enforce final Markdown structure
* ✅ **Automated Validation Script** to check output quality
* 🛡️ **Candidate Output Safety System** to prevent bad generations from overwriting valid output
* 🔌 **LiteLLM Integration** for OpenAI-compatible model access
* 🧪 **Connection Test Script** for verifying cluster/model access before running the full pipeline
* 📄 **Markdown Output Artifact** ready for study, documentation, or portfolio display

---

## What This Project Demonstrates

This project is not just a chatbot.

It demonstrates a practical agentic workflow where an LLM is used for generation and critique, while Python is used for structure, safety, and validation.

The core engineering idea is:

```text
LLM agents generate and review content.
Python enforces structure and validates the result.
```

This separation matters because LLM outputs are nondeterministic. The model may sometimes produce too many terms, too few terms, duplicate sections, or inconsistent formatting. The pipeline solves this by using deterministic Python logic to assemble the final document and validate that it meets the required output contract.

---

## Example Output

The pipeline generates a file named:

```text
outputs/ai_agents_glossary_guide.md
```

The final guide follows this structure:

```text
# AI Agents Glossary and Reference Guide

## 1. Long-Form Definition of AI Agents

## 2. The 50-Term Glossary

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

## 3. Adversarial Review Summary

## 4. Final Self-Critique
```

Each glossary term includes:

```text
Definition:
Why it matters:
Example:
Common confusion:
```

---

## Execution Pipeline

```text
User Prompt
    │
    ▼
Google ADK Root Agent
    │
    ▼
Term Planner
    │
    ▼
Definition Writer
    │
    ▼
Definition Reviewer
    │
    ▼
Definition Reviser
    │
    ▼
Glossary Writer A
Terms 1–25
    │
    ▼
Glossary Writer B
Terms 26–50
    │
    ▼
Glossary Reviewer
    │
    ▼
Review Summary Writer
    │
    ▼
Python Assembly Layer
    │
    ▼
Candidate Markdown File
    │
    ▼
Validation Script
    │
    ├── Pass → Save Final Guide
    │
    └── Fail → Keep Previous Valid Output
```

---

## Why Validation Matters

Long LLM-generated documents can fail in subtle ways.

During development, the model sometimes generated:

* 75 glossary terms instead of 50
* 100 glossary terms because both glossary writers produced all terms
* missing categories
* inconsistent Markdown headings
* extra draft content inside the final guide

To make the project reliable, the final pipeline validates the generated guide before accepting it.

The validator checks that the final Markdown file includes:

* The required title
* Section 1: Long-Form Definition of AI Agents
* Section 2: The 50-Term Glossary
* Section 3: Adversarial Review Summary
* Section 4: Final Self-Critique
* Exactly 50 glossary terms
* All 10 required categories
* Sufficient document length
* Balanced Markdown code fences

Only validated output is saved as the final guide.

---

## Output Safety System

The pipeline writes to a candidate file first:

```text
outputs/ai_agents_glossary_guide.candidate.md
```

Then it runs validation.

If validation passes, the candidate output replaces:

```text
outputs/ai_agents_glossary_guide.md
```

If validation fails, the bad attempt is saved as:

```text
outputs/ai_agents_glossary_guide.failed.md
```

This prevents malformed model outputs from overwriting the last known-good generated guide.

For GitHub, only the final validated guide should usually be committed:

```text
outputs/ai_agents_glossary_guide.md
```

Candidate and failed files should remain ignored.

---

## Project Structure

```text
ai-agents-glossary-adk/

├── README.md
├── .env.example
├── pyproject.toml
├── uv.lock
│
├── ai_agents_glossary/
│   ├── __init__.py
│   └── agent.py
│
├── hello_agent/
│   ├── __init__.py
│   └── agent.py
│
├── scripts/
│   ├── test_connection.py
│   ├── run_pipeline.py
│   └── validate_output.py
│
└── outputs/
    └── ai_agents_glossary_guide.md
```

---

## File Overview

### `ai_agents_glossary/agent.py`

Defines the main Google ADK glossary generation pipeline.

This is where the agent stages are configured, including the planner, writer, reviewer, reviser, glossary writers, and review summary writer.

### `hello_agent/agent.py`

A minimal ADK test agent used to confirm that Google ADK can call the configured model through LiteLLM.

This is useful for Phase 1 testing before running the larger pipeline.

### `scripts/test_connection.py`

Tests direct OpenAI-compatible access to the model endpoint.

It verifies:

* `.env` variables are loaded
* the model endpoint is reachable
* the configured model appears in `/v1/models`
* a small chat completion request succeeds

### `scripts/run_pipeline.py`

Runs the full glossary generation pipeline from the command line.

It:

* starts the ADK runner
* sends the glossary prompt
* streams pipeline stage events
* extracts outputs from session state
* normalizes glossary sections
* assembles the final Markdown guide
* validates a candidate output
* saves the final guide only if validation passes

### `scripts/validate_output.py`

Validates the generated Markdown guide.

It checks that the guide has exactly 50 glossary entries, all required sections, all required categories, and enough content to be considered complete.

---

## Required Categories

The generated glossary is organized into 10 AI-agent categories:

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

These categories were chosen to give readers a complete conceptual map of AI agents, from basic definitions to architecture, memory, tools, retrieval, evaluation, and failure modes.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/asim-aa/ai-agents-glossary-adk.git
cd ai-agents-glossary-adk
```

Create and sync the environment:

```bash
uv sync
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Create a `.env` file:

```bash
cp .env.example .env
```

Fill in your model endpoint settings:

```env
HOSTED_VLLM_API_BASE=http://your-openai-compatible-endpoint/v1
HOSTED_VLLM_API_KEY=dummy-key
SV_MODEL_NAME=hosted_vllm/openai/gpt-oss-20b
```

Do not commit real API keys or private credentials.

---

## Usage

### Phase 0: Test the Model Connection

Before running ADK, verify that the endpoint works:

```bash
uv run python scripts/test_connection.py
```

Expected result:

```text
SUCCESS: SV cluster connection works.
```

---

### Phase 1: Run the Hello Agent

The hello agent is a minimal ADK test agent.

Start the ADK web interface:

```bash
uv run adk web
```

Open the local ADK web UI in your browser, select the hello agent, and send a simple prompt.

This confirms that:

```text
Google ADK → LiteLLM → OpenAI-compatible endpoint → model
```

is working correctly.

---

### Phase 2: Run the Full Agent Pipeline in ADK Web

Start ADK web:

```bash
uv run adk web
```

Select the glossary agent and run the full glossary generation prompt.

This is useful for visually inspecting the multi-stage ADK pipeline.

---

### Phase 3: Run the CLI Pipeline

Run the full pipeline from the terminal:

```bash
uv run python scripts/run_pipeline.py
```

Expected successful output:

```text
Pipeline output diagnostics:
- glossary_part_a Definition count: 25
- glossary_part_b Definition count: 25
- total Definition count: 50
- review summary has section 4: True

Validation passed:
- 50 terms found
- 10 categories found
- Required sections found

SUCCESS: Phase 3 + Phase 4 pipeline run completed.
```

The final Markdown file will be saved to:

```text
outputs/ai_agents_glossary_guide.md
```

---

### Phase 4: Run Validation Separately

You can validate the final generated guide at any time:

```bash
uv run python scripts/validate_output.py
```

Expected result:

```text
Validation passed:
- 50 terms found
- 10 categories found
- Required sections found
```

---

## Example Terminal Session

```text
Starting ADK glossary pipeline...
Root agent: ai_agents_glossary
Output file: outputs/ai_agents_glossary_guide.md

Running pipeline. This may take several minutes...

Stage event from: term_planner
Stage event from: definition_writer
Stage event from: definition_reviewer
Stage event from: definition_reviser
Stage event from: glossary_writer_a
Stage event from: glossary_writer_b
Stage event from: glossary_reviewer
Stage event from: review_summary_writer

Pipeline finished. Extracting pipeline outputs from session state...

Pipeline output diagnostics:
- glossary_part_a Definition count: 25
- glossary_part_b Definition count: 25
- total Definition count: 50
- review summary has section 4: True

Validating candidate guide...
Validation passed:
- 50 terms found
- 10 categories found
- Required sections found

Saved validated guide to: outputs/ai_agents_glossary_guide.md

SUCCESS: Phase 3 + Phase 4 pipeline run completed.
```

---

## Design Highlights

### Bounded Adversarial Review

The project uses a bounded writer-reviewer pipeline instead of an infinite autonomous loop.

This keeps execution predictable while still demonstrating adversarial improvement:

```text
Writer creates content.
Reviewer critiques weaknesses.
Reviser improves the content.
Final reviewer summary explains what was improved.
```

This is a practical engineering compromise: enough review to improve quality, but bounded enough to avoid runaway agent loops.

---

### Deterministic Assembly

The model is responsible for writing content, but Python is responsible for assembling the final document.

This prevents common LLM failure modes such as:

* duplicate glossary terms
* missing categories
* inconsistent Markdown headings
* malformed final sections
* too many or too few glossary entries

The final guide is therefore not accepted just because the model generated text. It must pass the validator.

---

### Candidate-First Output

The pipeline never blindly overwrites the final guide.

Instead, it writes a candidate output, validates it, and only saves it as the final output if all checks pass.

This makes the workflow safer and closer to how production generation systems handle unreliable model outputs.

---

### Provider-Agnostic Model Access

The project was built with the SupportVectors cluster, but it uses OpenAI-compatible conventions through LiteLLM.

That means the model backend can be swapped by changing environment variables rather than rewriting the pipeline.

---

## Technologies Used

* Python
* Google ADK
* LiteLLM
* OpenAI-compatible Chat Completions API
* SupportVectors AI Cluster
* vLLM-style hosted model endpoint
* python-dotenv
* Markdown
* Regular expressions for validation and cleanup
* uv for dependency and environment management

---

## What I Learned

This project helped me understand:

* how Google ADK structures agent applications
* how to connect ADK to a private model endpoint through LiteLLM
* how multi-stage agent pipelines differ from simple chatbot scripts
* why LLM outputs need deterministic post-processing
* how validation improves reliability in generative systems
* how adversarial review can improve educational content
* how to separate generation, orchestration, assembly, and validation responsibilities

---

## Future Improvements

Possible next steps:

* Add a CLI argument for generating glossaries on any topic
* Add configurable term counts and categories
* Add retry logic when validation fails
* Add structured JSON output before Markdown rendering
* Add a Streamlit or FastAPI interface
* Add automated tests for the validator
* Add token/cost/runtime logging
* Add support for saving outputs as PDF or HTML
* Add a formal evaluation rubric for glossary quality
* Add tracing or telemetry for each ADK stage

---

## Resume Bullet

Built a validated Google ADK pipeline that generates a 50-term AI Agents Glossary and Reference Guide using adversarial writer-reviewer stages, a private OpenAI-compatible vLLM endpoint, deterministic Python assembly, and automated Markdown validation.

---

## License

This project is provided for educational and portfolio purposes.
