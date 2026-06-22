import os
from dotenv import load_dotenv
from openai import OpenAI


def clean_model_name(model_name: str) -> str:
    """
    LiteLLM uses names like hosted_vllm/openai/gpt-oss-20b.
    Direct OpenAI-compatible vLLM usually expects openai/gpt-oss-20b.
    """
    if model_name.startswith("hosted_vllm/"):
        return model_name.replace("hosted_vllm/", "", 1)
    return model_name


def main() -> None:
    print("Loading environment variables...")

    load_dotenv()

    api_base = os.getenv("HOSTED_VLLM_API_BASE")
    api_key = os.getenv("HOSTED_VLLM_API_KEY", "dummy-key")
    model_name = os.getenv("SV_MODEL_NAME")

    if not api_base:
        raise ValueError("Missing HOSTED_VLLM_API_BASE in .env")

    if not model_name:
        raise ValueError("Missing SV_MODEL_NAME in .env")

    direct_model_name = clean_model_name(model_name)

    print("Environment loaded.")
    print(f"API base: {api_base}")
    print(f"Model from .env: {model_name}")
    print(f"Model used for direct OpenAI-compatible test: {direct_model_name}")
    print()

    client = OpenAI(
        base_url=api_base,
        api_key=api_key,
    )

    print("Testing /v1/models endpoint...")

    try:
        models = client.models.list()
        model_ids = [m.id for m in models.data]

        print("Available models:")
        for model_id in model_ids:
            print(f"- {model_id}")

        print()

        if direct_model_name not in model_ids:
            print("WARNING: Your selected model was not found exactly in /v1/models.")
            print("If the chat test fails, copy one of the model names above into .env.")
            print()

    except Exception as e:
        print("Failed to list models.")
        print(f"Error: {type(e).__name__}: {e}")
        raise

    print("Testing chat completion...")

    try:
        response = client.chat.completions.create(
            model=direct_model_name,
            messages=[
                {
                    "role": "user",
                    "content": "Reply with exactly: cluster connection works",
                }
            ],
            max_tokens=50,
            temperature=0,
        )

        print()
        print("Cluster response:")
        print(response.choices[0].message.content)
        print()
        print("SUCCESS: SV cluster connection works.")

    except Exception as e:
        print("Chat completion failed.")
        print(f"Error: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    main()