import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from theme import inject_theme, render_header, render_verification_readout
from model import pipeline

st.set_page_config(page_title="Login & Attendance", page_icon="🪪", layout="wide")
inject_theme()

CONFIDENCE_THRESHOLD = 0.6
LOG_PATH = Path(__file__).resolve().parent.parent / "attendance_log.csv"

enrolled = pipeline.get_enrolled_students()

render_header(
    "Login & attendance",
    "Claim an identity, run a captured image through the verification pipeline.",
    status_text=f"THRESHOLD {int(CONFIDENCE_THRESHOLD * 100)}%",
)

if not enrolled:
    st.warning("No students enrolled yet. Ask the admin to enroll students first.")
    st.stop()

st.subheader("Login")
claimed_id = st.selectbox(
    "Student ID",
    options=list(enrolled.keys()),
    format_func=lambda pid: enrolled[pid],
)

st.caption(
    "No live webcam yet -- this simulates a capture using held-out images "
    "the model has never trained on, standing in for a fresh photo."
)
attempt_type = st.radio(
    "Simulated capture",
    ["Genuine (my own held-out image)", "Impostor (someone else's image)"],
)

if attempt_type.startswith("Genuine"):
    image_owner_id = claimed_id
else:
    other_ids = [pid for pid in enrolled if pid != claimed_id]
    image_owner_id = st.selectbox(
        "Feed in whose image instead", options=other_ids, format_func=lambda pid: enrolled[pid]
    )

if st.button("Mark attendance", type="primary"):
    image = pipeline.get_simulated_capture(image_owner_id)
    predicted_id, confidence = pipeline.predict(image)

    match = predicted_id == claimed_id and confidence >= CONFIDENCE_THRESHOLD
    status = "Present" if match else "Rejected"

    render_verification_readout(
        accepted=match,
        name=enrolled[claimed_id],
        confidence=confidence,
        threshold=CONFIDENCE_THRESHOLD,
    )
    if not match:
        predicted_name = enrolled.get(predicted_id, f"Student_{predicted_id}")
        st.caption(f"System matched this capture to **{predicted_name}** instead, not the claimed ID.")

    row = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "claimed_id": enrolled[claimed_id],
        "predicted_id": enrolled.get(predicted_id, str(predicted_id)),
        "confidence": round(confidence, 3),
        "status": status,
    }])
    header = not LOG_PATH.exists()
    row.to_csv(LOG_PATH, mode="a", header=header, index=False)

st.divider()
st.subheader("Attendance log")
if LOG_PATH.exists():
    log_df = pd.read_csv(LOG_PATH)
    st.dataframe(log_df.sort_values("timestamp", ascending=False), width='stretch')

    total = len(log_df)
    present = (log_df["status"] == "Present").sum()
    c1, c2 = st.columns(2)
    c1.metric("Total attempts", total)
    c2.metric("Accepted", f"{present}/{total}")
else:
    st.info("No attendance marked yet.")
