import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import streamlit as st
from theme import inject_theme, render_header
from model import pipeline

st.set_page_config(page_title="Attendance Portal", page_icon="🎓", layout="wide")
inject_theme()

try:
    stats = pipeline.get_model_stats()
    status_text = f"{stats['n_students']} ENROLLED · {stats['classifier_name'].upper()} ACTIVE"
except Exception:
    status_text = "NOT YET TRAINED"

render_header(
    "Verification checkpoint",
    "Face-recognition attendance, built on PCA eigenfaces + a trained classifier over the ORL dataset.",
    status_text=status_text,
)

st.write("")
col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.markdown("### 🛠️ Admin & enrollment")
        st.write(
            "Enroll students, tune the PCA + classifier pipeline, and inspect "
            "eigenfaces, confusion matrices, and learning curves."
        )
        st.page_link("pages/1_Admin_Enrollment.py", label="Open admin panel", icon="➡️")

with col2:
    with st.container(border=True):
        st.markdown("### 🪪 Login & attendance")
        st.write(
            "Simulate a student login: claim an identity, run a captured image "
            "through the verification pipeline, and mark attendance."
        )
        st.page_link("pages/2_Login_Attendance.py", label="Open login portal", icon="➡️")

st.write("")
st.caption(
    "Both pages share the same trained pipeline (model/pipeline.py) -- anything "
    "enrolled on the Admin page is immediately recognizable on the Login page."
)
