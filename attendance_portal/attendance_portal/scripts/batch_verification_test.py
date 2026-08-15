"""
Batch verification testing for the Attendance Portal login flow.

This measures a different thing than the Admin page's classifier accuracy:
that number tells you how well the classifier identifies WHO someone is.
This script tells you how well the full LOGIN/VERIFICATION step performs --
does it correctly accept genuine students and correctly reject impostors,
given the confidence threshold used at login.

Genuine attempt  = a student's held-out image, claimed under their own ID.
Impostor attempt = a student's held-out image, claimed under someone else's ID.

Reports the standard biometric verification metrics:
  True Accept Rate  (TAR) = genuine attempts correctly accepted
  False Reject Rate (FRR) = genuine attempts incorrectly rejected (1 - TAR)
  False Accept Rate (FAR) = impostor attempts incorrectly accepted
  True Reject Rate  (TRR) = impostor attempts correctly rejected (1 - FAR)

Run from the project root:
    python scripts/batch_verification_test.py
"""

import sys
import itertools
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
from model import pipeline

CONFIDENCE_THRESHOLD = 0.6
MAX_IMPOSTOR_PAIRS = 300  # caps runtime; increase for a more thorough report


def run_batch_test(confidence_threshold=CONFIDENCE_THRESHOLD):
    enrolled = pipeline.get_enrolled_students()
    split = pipeline.get_split()
    student_ids = list(enrolled.keys())

    results = []

    # --- Genuine attempts: every enrolled student's every held-out image ---
    for sid in student_ids:
        mask = split["test_y"] == sid
        images = split["test_X"][mask]
        for img in images:
            pred_id, conf = pipeline.predict(img)
            accepted = (pred_id == sid) and (conf >= confidence_threshold)
            results.append({
                "type": "genuine",
                "claimed_id": sid,
                "image_owner_id": sid,
                "predicted_id": pred_id,
                "confidence": conf,
                "accepted": accepted,
            })

    # --- Impostor attempts: claim someone else's ID, feed in your own image ---
    pairs = itertools.islice(itertools.permutations(student_ids, 2), 0, MAX_IMPOSTOR_PAIRS)
    for claimed_sid, actual_sid in pairs:
        mask = split["test_y"] == actual_sid
        images = split["test_X"][mask]
        if len(images) == 0:
            continue
        img = images[0]
        pred_id, conf = pipeline.predict(img)
        accepted = (pred_id == claimed_sid) and (conf >= confidence_threshold)
        results.append({
            "type": "impostor",
            "claimed_id": claimed_sid,
            "image_owner_id": actual_sid,
            "predicted_id": pred_id,
            "confidence": conf,
            "accepted": accepted,
        })

    return pd.DataFrame(results)


def summarize(df):
    genuine = df[df["type"] == "genuine"]
    impostor = df[df["type"] == "impostor"]

    tar = genuine["accepted"].mean() if len(genuine) else float("nan")
    far = impostor["accepted"].mean() if len(impostor) else float("nan")

    print(f"Genuine attempts: {len(genuine)}")
    print(f"  True Accept Rate  (TAR): {tar * 100:.2f}%")
    print(f"  False Reject Rate (FRR): {(1 - tar) * 100:.2f}%")
    print()
    print(f"Impostor attempts: {len(impostor)}")
    print(f"  False Accept Rate (FAR): {far * 100:.2f}%")
    print(f"  True Reject Rate  (TRR): {(1 - far) * 100:.2f}%")
    print()
    print(f"(Confidence threshold used: {CONFIDENCE_THRESHOLD})")


if __name__ == "__main__":
    df = run_batch_test()

    out_path = Path(__file__).resolve().parent.parent / "data" / "batch_verification_results.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} trial results to {out_path}\n")

    summarize(df)
