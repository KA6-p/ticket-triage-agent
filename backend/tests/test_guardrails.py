from app.services.guardrails import apply_priority_override


def test_critical():
    assert (
        apply_priority_override("Site down", "Everything is down", "low")[0]
        == "critical"
    )


def test_no_change():
    assert apply_priority_override("Question", "Hello", "medium")[0] == "medium"
