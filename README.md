# AI Agents Glossary Generator with Adversarial Review

## Overview

This project is a Google ADK multi-agent glossary generation pipeline. It creates a polished AI Agents Glossary and Reference Guide using staged writer, reviewer, and reviser agents.

The system uses deterministic pipeline orchestration instead of relying on model-routed agent transfers. This makes the workflow easier to debug, test, and reproduce.

## Project Goals

- Generate a 50-term AI agents glossary.
- Write a 500–600 token long-form definition of AI agents.
- Use adversarial review to identify weak, vague, or misleading explanations.
- Revise the output based on reviewer feedback.
- Save the final guide as a Markdown artifact.
- Validate that the required sections and term count are present.

## Architecture

```text
Local VS Code Project
        ↓
Google ADK
        ↓
Sequential multi-agent pipeline
        ↓
LiteLLM connector
        ↓
SV cluster vLLM endpoint
        ↓
Final Markdown guide