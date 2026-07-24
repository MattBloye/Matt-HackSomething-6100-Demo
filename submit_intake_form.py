"""Interactively simulates a patient submitting the intake form through the online
portal. The "Reason for Visit" field is the delivery vector for this demo -- whatever
the person running this types there (benign text or an injected instruction) goes into
the document verbatim. Each submission triggers a full rebuild of the index via
ingest.build_index() -- baseline documents/ plus every accumulated intake submission,
re-embedded from scratch -- so the index can never diverge from what's on disk.
"""
import glob
import os
from datetime import datetime

from ingest import build_index

SUBMISSIONS_DIR = "intake_submissions"


def read_multiline_field(prompt: str) -> str:
    print(prompt)
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def main():
    print("=== Patient Intake Form Submission ===")
    print("Simulates a patient submitting this form through the online patient portal.\n")

    name = input("Patient Name: ")
    dob = input("Date of Birth: ")
    contact = input("Preferred Contact: ")
    reason = read_multiline_field(
        "Reason for Visit / Symptom Description (this is submitted as free text on "
        "the portal -- type your entry, then on a new line type END to finish):"
    )

    text = (
        "New Patient Intake Form Submission\n\n"
        f"Patient Name: {name}\n"
        f"Date of Birth: {dob}\n"
        f"Reason for Visit: {reason}\n"
        f"Preferred Contact: {contact}\n"
        "Submitted Via: Online patient intake portal"
    )

    os.makedirs(SUBMISSIONS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    record_path = os.path.join(SUBMISSIONS_DIR, f"intake_{timestamp}.txt")
    with open(record_path, "w", encoding="utf-8") as f:
        f.write(text)

    extra_files = sorted(glob.glob(os.path.join(SUBMISSIONS_DIR, "*.txt")))
    build_index(extra_files=extra_files)

    print(f"[intake] submitted and ingested. Saved record: {record_path}")


if __name__ == "__main__":
    main()
