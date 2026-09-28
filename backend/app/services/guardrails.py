import re

CRITICAL = [
    r"\bdown\b",
    r"\boutage\b",
    r"\blost data\b",
    r"\bdata loss\b",
    r"\bsecurity breach\b",
    r"\baccount hacked\b",
]
HIGH = [
    r"can't login",
    r"cannot login",
    r"locked out",
    r"fraud",
    r"chargeback",
    r"urgent",
    r"production",
]


def apply_priority_override(
    subject: str, body: str, priority: str
) -> tuple[str, list[str]]:
    text = f"{subject} {body}".lower()
    reasons = []
    if any(re.search(p, text) for p in CRITICAL):
        return "critical", ["critical keyword rule"]
    if any(re.search(p, text) for p in HIGH) and priority == "low":
        return "high", ["high-priority keyword rule"]
    return priority, reasons
