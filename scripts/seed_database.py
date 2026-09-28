import requests

API = "http://localhost:8000"
rows = [
    ("Refund", "I was charged twice for the same invoice."),
    ("Login", "I cannot login after resetting my password."),
    ("Crash", "The dashboard crashes when I open reports."),
    ("Export", "Please add an Excel export option."),
    ("Documentation", "Where is the API documentation?"),
    ("Outage", "The production service is down for all users."),
]
for s, b in rows:
    r = requests.post(
        API + "/tickets", json={"subject": s, "body": b, "source": "seed"}
    )
    print(r.status_code, r.json())
