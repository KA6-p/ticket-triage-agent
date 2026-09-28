import argparse
import csv

import requests
from sklearn.metrics import classification_report, confusion_matrix


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", default="evaluation/dataset/labeled_tickets.csv")
    p.add_argument("--api", default="http://localhost:8000")
    a = p.parse_args()
    y_true = []
    y_pred = []
    with open(a.file, encoding="utf8") as f:
        for row in csv.DictReader(f):
            r = requests.post(
                a.api + "/tickets",
                json={
                    "subject": row["subject"],
                    "body": row["body"],
                    "source": "evaluation",
                },
                timeout=120,
            )
            r.raise_for_status()
            y_true.append(row["category"])
            y_pred.append(r.json()["category"])
    print(classification_report(y_true, y_pred, digits=3))
    print("Confusion matrix:\n", confusion_matrix(y_true, y_pred))


if __name__ == "__main__":
    main()
