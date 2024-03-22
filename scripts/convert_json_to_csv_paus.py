import csv
import json

data = None
with open("paus.json", "r") as f:
    data = json.load(f)

with open("paus.csv", "w", newline="") as csvfile:
    spamwriter = csv.writer(
        csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
    )
    for entry in data:
        spamwriter.writerow(
            [
                entry["company_id"],
                entry["type"],
                entry["member_state"],
                entry["substance"],
                entry["pau_use"],
                entry["value"],
                entry["process_name"],
                entry["year"],
            ]
        )
