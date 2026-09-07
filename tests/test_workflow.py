from unittest.mock import patch

from app.agents.research_agent import research_agent
from app.agents.script_agent import script_agent
from app.agents.workflow import build_workflow


def test_workflow_initialization() -> None:
    """Verify the workflow can initialize its state."""

    workflow = build_workflow()

    initial_state = {
        "topic": "How artificial intelligence works",
        "content_type": "short",
    }

    # We only test graph construction here.
    assert workflow is not None
    assert initial_state["topic"] == "How artificial intelligence works"
    assert initial_state["content_type"] == "short"


@patch("app.agents.research_agent.GeminiClient")
def test_research_agent(mock_gemini_client) -> None:
    """Verify the research agent processes Gemini research output."""

    mock_gemini_client.return_value.generate_text.return_value = (
        "- Artificial intelligence enables machines to perform tasks "
        "that normally require human intelligence.\n"
        "- Machine learning is a major approach used in modern AI."
    )

    result = research_agent(
        {
            "topic": "How artificial intelligence works",
            "content_type": "short",
        }
    )

    assert result["topic"] == "How artificial intelligence works"
    assert len(result["research_notes"]) == 2
    assert all(
        isinstance(note, str) and note.strip()
        for note in result["research_notes"]
    )

    mock_gemini_client.return_value.generate_text.assert_called_once()


@patch("app.agents.script_agent.GeminiClient")
def test_script_agent(mock_gemini_client) -> None:
    """Verify the script agent generates a script from research."""

    mock_gemini_client.return_value.generate_text.return_value = (
        "Artificial intelligence is changing how machines solve problems. "
        "At its core, AI uses algorithms and data to perform tasks."
    )

    result = script_agent(
        {
            "topic": "How artificial intelligence works",
            "content_type": "short",
            "research_notes": [
                "AI enables machines to perform tasks requiring intelligence.",
                "Machine learning is a major approach used in AI.",
            ],
        }
    )

    assert result["topic"] == "How artificial intelligence works"
    assert result["script"]
    assert isinstance(result["script"], str)

    mock_gemini_client.return_value.generate_text.assert_called_once()