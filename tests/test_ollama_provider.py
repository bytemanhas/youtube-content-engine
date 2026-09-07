from pydantic import BaseModel

from app.services.ollama_provider import OllamaProvider


class TestResponse(BaseModel):
    answer: str


def main() -> None:
    """Test Ollama text and structured generation."""

    provider = OllamaProvider()

    text_response = provider.generate_text(
        "Explain artificial intelligence in exactly one sentence."
    )

    print("\n--- TEXT RESPONSE ---")
    print(text_response)

    structured_response = provider.generate_structured(
        """
Return a JSON object containing one field called "answer".

The answer should explain what a database is in one sentence.
""".strip(),
        TestResponse,
    )

    print("\n--- STRUCTURED RESPONSE ---")
    print(structured_response)
    print(structured_response.answer)


if __name__ == "__main__":
    main()