import csv
import io
import json


def export_to_csv(data, columns=None):
    if not data:
        return ""
    if columns is None:
        columns = list(data[0].keys()) if isinstance(data[0], dict) else []

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for row in data:
        writer.writerow({k: row.get(k, "") for k in columns})
    return output.getvalue()


def export_to_json(data):
    return json.dumps(data, indent=2, default=str)
