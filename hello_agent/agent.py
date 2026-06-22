import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


load_dotenv()

os.environ["HOSTED_VLLM_API_BASE"] = os.getenv("HOSTED_VLLM_API_BASE", "")
os.environ["HOSTED_VLLM_API_KEY"] = os.getenv("HOSTED_VLLM_API_KEY", "dummy-key")

MODEL_NAME = os.getenv("SV_MODEL_NAME", "hosted_vllm/openai/gpt-oss-20b")


root_agent = LlmAgent(
    name="hello_agent",
    model=LiteLlm(model=MODEL_NAME),
    description="A minimal ADK agent used to verify the SV cluster connection through LiteLLM.",
    instruction="""
You are a minimal test agent.

Your job is to confirm that Google ADK can call the SV cluster model through LiteLLM.

When the user asks you a question:
- Answer clearly and briefly.
- Mention that this is the hello_agent test.
- Do not claim access to tools.
""",
)