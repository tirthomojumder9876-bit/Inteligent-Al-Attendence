import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.graph_objects as go

from theme import inject_theme, render_header
from model import pipeline

st.set_page_config(page_title="Admin & Enrollment", page_icon="⚙️", layout="wide")
inject_theme()

stats = pipeline.get_model_stats()
render_header(
    "Admin & enrollment",
    "ORL faces · PCA eigenfaces + classifier pipeline",
    status_text=f"{stats['n_students']} ENROLLED",
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Students enrolled", stats["n_students"])
col2.metric("Model accuracy", f"{stats['accuracy'] * 100:.1f}%")
col3.metric("Active classifier", stats["classifier_name"].upper())
col4.metric("Macro F1", f"{stats['f1'] * 100:.1f}%")

st.divider()

# --- Classifier comparison ------------------------------------------------
st.subheader("Classifier comparison")
if st.button("Run comparison (SVM vs kNN vs Logistic Regression)"):
    with st.spinner("Training all three classifiers..."):
        results = pipeline.compare_classifiers()
    st.session_state["comparison_results"] = results

if "comparison_results" in st.session_state:
    results = st.session_state["comparison_results"]
    labels = {"svm": "SVM (RBF)", "knn": "kNN", "logreg": "Logistic Regression"}
    ordered = sorted(results.items(), key=lambda kv: -kv[1]["accuracy"])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[labels[name] for name, _ in ordered],
        y=[m["accuracy"] * 100 for _, m in ordered],
        marker_color="#2BB3A3",
        text=[f"{m['accuracy'] * 100:.1f}%" for _, m in ordered],
        textposition="outside",
    ))
    fig.update_layout(
        height=280, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono", color="#E7EAEE", size=12),
        yaxis=dict(title="Accuracy (%)", range=[0, 105], gridcolor="rgba(255,255,255,0.08)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
    )
    st.plotly_chart(fig)

    for name, metrics in ordered:
        st.caption(
            f"**{labels[name]}** — precision {metrics['precision'] * 100:.1f}% · "
            f"recall {metrics['recall'] * 100:.1f}% · f1 {metrics['f1'] * 100:.1f}%"
        )
    st.caption(
        "Note: training the 'active' deployed model separately below picks which "
        "classifier the Login page actually uses -- running this comparison does "
        "not change it."
    )

st.divider()

# --- Eigenfaces gallery -----------------------------------------------------
st.subheader("Eigenfaces")
st.caption("Top principal components from PCA, reshaped back into images.")
eigenfaces = pipeline.get_eigenfaces(n=10)
cols = st.columns(5)
for i, ef in enumerate(eigenfaces):
    normalized = (ef - ef.min()) / (ef.max() - ef.min() + 1e-8)
    with cols[i % 5]:
        st.markdown('<div class="eigentile">', unsafe_allow_html=True)
        st.image(normalized, width='stretch', clamp=True)
        st.markdown(f'<div class="eigentile-label">PC-{i + 1:02d}</div></div>', unsafe_allow_html=True)

st.divider()

# --- Tune & retrain ----------------------------------------------------------
st.subheader("Tune & retrain the active model")
c1, c2, c3, c4 = st.columns(4)
n_components = c1.slider("PCA components", min_value=10, max_value=150, value=100, step=10)
classifier_choice = c2.selectbox("Classifier", ["svm", "knn", "logreg"])

C_val, kernel_choice, k_val = 10.0, "rbf", 3
if classifier_choice == "svm":
    C_val = c3.slider("SVM C (regularization)", min_value=0.1, max_value=100.0, value=10.0, step=0.1)
    kernel_choice = c4.selectbox("Kernel", ["rbf", "linear", "poly"])
elif classifier_choice == "knn":
    k_val = c3.slider("k (neighbors)", min_value=1, max_value=15, value=3)

if classifier_choice == "svm":
    temperature = st.slider(
        "Confidence sharpness (temperature)", min_value=0.2, max_value=2.0, value=1.0, step=0.1,
        help="Below 1.0 sharpens confidence scores for correct predictions (higher numbers shown "
             "for confident matches); above 1.0 softens them. Does not change accuracy or which "
             "student gets predicted -- only how the confidence number is reported.",
    )
else:
    temperature = 1.0

tune_col1, tune_col2 = st.columns(2)
if tune_col1.button("Train with these settings", type="primary"):
    with st.spinner("Training..."):
        bundle = pipeline.train_initial(
            n_components=n_components, classifier=classifier_choice,
            C=C_val, kernel=kernel_choice, k=k_val, confidence_temperature=temperature,
        )
    st.success(f"Trained. Accuracy: {bundle['metrics']['accuracy'] * 100:.1f}%")
    st.rerun()

if tune_col2.button("Compute learning curve for these settings"):
    with st.spinner("Running cross-validation (this refits PCA on each fold's own training data)..."):
        lc = pipeline.compute_learning_curve(
            n_components=n_components, classifier=classifier_choice,
            C=C_val, kernel=kernel_choice, k=k_val,
        )
    if lc["n_components_used"] < lc["n_components_requested"]:
        st.caption(
            f"Note: used {lc['n_components_used']} PCA components instead of "
            f"{lc['n_components_requested']} for this curve -- the smallest training "
            f"slice in the curve doesn't have enough samples to support more than that."
        )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=lc["train_sizes"], y=[v * 100 for v in lc["train_mean"]],
        mode="lines+markers", name="Training accuracy",
        line=dict(color="#E8B94A", width=2), marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=lc["train_sizes"], y=[v * 100 for v in lc["val_mean"]],
        mode="lines+markers", name="Validation accuracy",
        line=dict(color="#2BB3A3", width=2), marker=dict(size=7),
    ))
    fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono", color="#E7EAEE", size=12),
        xaxis=dict(title="Training set size", gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(title="Accuracy (%)", range=[0, 105], gridcolor="rgba(255,255,255,0.08)"),
        legend=dict(orientation="h", y=1.12, font=dict(size=11)),
    )
    st.plotly_chart(fig)

    gap = lc["train_mean"][-1] - lc["val_mean"][-1]
    if gap > 0.1:
        st.info(f"Train/validation gap is {gap * 100:.1f} points — leaning toward high variance (overfitting).")
    elif lc["val_mean"][-1] < 0.8:
        st.info("Both curves are relatively low and close together — leaning toward high bias (underfitting).")
    else:
        st.info("Train and validation accuracy are close and both high — a reasonably good fit.")

st.divider()

# --- Enroll a new student --------------------------------------------------
st.subheader("Enroll a new student")

not_yet = pipeline.get_not_yet_enrolled_students()
if not_yet:
    student_id = st.selectbox(
        "Select a reserved (not-yet-enrolled) student to simulate enrollment",
        options=list(not_yet.keys()),
        format_func=lambda pid: not_yet[pid],
    )
    if st.button("Capture images & enroll", type="primary"):
        split = pipeline.get_split()
        mask = split["not_yet_enrolled_labels"] == student_id
        images = split["not_yet_enrolled_images"][mask]
        with st.spinner("Extracting features and retraining..."):
            bundle = pipeline.enroll_new_student(student_id, images)
        st.success(
            f"{not_yet[student_id]} enrolled. Model retrained -- "
            f"new accuracy: {bundle['metrics']['accuracy'] * 100:.1f}%"
        )
        st.session_state.pop("comparison_results", None)
        st.rerun()
else:
    st.info("All reserved students have already been enrolled.")

st.divider()

# --- Model performance detail ----------------------------------------------
st.subheader("Model performance (active model)")
bundle = pipeline.get_model()
cm = bundle["confusion_matrix"]

fig = go.Figure(data=go.Heatmap(
    z=cm, colorscale=[[0, "#1A222C"], [1, "#2BB3A3"]],
    showscale=True, hoverongaps=False,
))
fig.update_layout(
    height=420, margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono", color="#E7EAEE", size=11),
    xaxis=dict(title="Predicted student", gridcolor="rgba(255,255,255,0.08)"),
    yaxis=dict(title="Actual student", autorange="reversed", gridcolor="rgba(255,255,255,0.08)"),
)
st.plotly_chart(fig)
