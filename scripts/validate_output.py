import re
import sys
import unicodedata
from pathlib import Path


DEFAULT_OUTPUT_FILE = Path("outputs/ai_agents_glossary_guide.md")


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


class ValidationError(Exception):
    """Raised when the generated glossary guide fails validation."""


def normalize(text: str) -> str:
    """Normalize unicode punctuation/casing so checks are less brittle."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("-", "-").replace("–", "-").replace("—", "-")
    text = text.replace("→", "->")
    return text.lower()


def extract_section(text: str, start_pattern: str, end_pattern: str | None = None) -> str:
    start_match = re.search(start_pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not start_match:
        return ""

    start_index = start_match.start()

    if end_pattern is None:
        return text[start_index:]

    end_match = re.search(end_pattern, text[start_match.end():], flags=re.IGNORECASE | re.MULTILINE)
    if not end_match:
        return text[start_index:]

    end_index = start_match.end() + end_match.start()
    return text[start_index:end_index]


def count_glossary_terms(glossary_section: str) -> int:
    """
    Counts glossary entries by counting Definition: labels inside the glossary section.
    This is more robust than counting headings because models may use ##, ###, bold terms,
    numbered lists, or mixed Markdown formatting.
    """
    return len(re.findall(r"(?im)^\s*\**definition\**\s*:", glossary_section))


def validate_guide(path: Path = DEFAULT_OUTPUT_FILE, verbose: bool = True) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        raise ValidationError(f"Final output file does not exist: {path}")

    text = path.read_text(encoding="utf-8")
    normalized = normalize(text)

    if "ai agents glossary and reference guide" not in normalized:
        errors.append("Missing required title: AI Agents Glossary and Reference Guide")

    if not re.search(r"(?im)^#{1,3}\s*1\.\s*long-?form definition", normalize(text)):
        errors.append("Missing section 1: Long-Form Definition of AI Agents")

    glossary_section = extract_section(
        text,
        r"(?im)^#{1,3}\s*2\.\s*the\s+50[- ]term\s+glossary",
        r"(?im)^#{1,3}\s*3\.\s*adversarial\s+review\s+summary",
    )

    if not glossary_section:
        errors.append("Missing section 2: The 50-Term Glossary")

    review_section = extract_section(
        text,
        r"(?im)^#{1,3}\s*3\.\s*adversarial\s+review\s+summary",
        r"(?im)^#{1,3}\s*4\.\s*final\s+self[- ]critique",
    )

    if not review_section:
        errors.append("Missing section 3: Adversarial Review Summary")

    self_critique_section = extract_section(
        text,
        r"(?im)^#{1,3}\s*4\.\s*final\s+self[- ]critique",
        None,
    )

    if not self_critique_section:
        errors.append("Missing section 4: Final Self-Critique")

    term_count = count_glossary_terms(glossary_section) if glossary_section else 0

    if term_count != 50:
        errors.append(f"Expected exactly 50 glossary terms, but found {term_count}")

    found_categories = []
    normalized_glossary = normalize(glossary_section)

    for category in REQUIRED_CATEGORIES:
        if normalize(category) in normalized_glossary:
            found_categories.append(category)
        else:
            errors.append(f"Missing required category: {category}")

    if len(text) < 8_000:
        errors.append("Output looks too short; it may be incomplete or truncated")

    if text.count("```") % 2 != 0:
        errors.append("Unbalanced Markdown code fences detected")

    if self_critique_section and len(self_critique_section.strip()) < 300:
        warnings.append("Final Self-Critique section looks short")

    if review_section and "no major issues remain" not in normalize(review_section):
        warnings.append("Review summary does not include the expected final reviewer conclusion")

    if errors:
        message = "Validation failed:\n" + "\n".join(f"- {error}" for error in errors)

        if warnings:
            message += "\n\nWarnings:\n" + "\n".join(f"- {warning}" for warning in warnings)

        raise ValidationError(message)

    result = {
        "path": str(path),
        "term_count": term_count,
        "category_count": len(found_categories),
        "required_sections_found": True,
        "warnings": warnings,
    }

    if verbose:
        print("Validation passed:")
        print(f"- {term_count} terms found")
        print(f"- {len(found_categories)} categories found")
        print("- Required sections found")
        print(f"- Output saved to {path}")

        if warnings:
            print()
            print("Warnings:")
            for warning in warnings:
                print(f"- {warning}")

    return result


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT_FILE

    try:
        validate_guide(path)
    except ValidationError as exc:
        print(exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
