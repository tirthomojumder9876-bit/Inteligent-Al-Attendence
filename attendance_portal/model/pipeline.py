"""
Shared model pipeline for the Attendance Portal.

Member 1 owns the internals of this file (data split, PCA, classifier
training/evaluation). Member 2 should only need these functions:

    predict(image)              -> (student_id, confidence)
    get_enrolled_students()     -> {student_id: name}
    get_not_yet_enrolled_students() -> {student_id: name}
    get_simulated_capture(student_id) -> image array (stands in for a webcam frame)
    get_model_stats()           -> dict of accuracy/precision/recall/f1/etc.
    enroll_new_student(student_id, images) -> retrains and returns the new model bundle

Nothing here should need to change from the Login/Attendance page's point of view
even as Member 1 tunes the model internals.
"""

import numpy as np
import joblib
from pathlib import Path

from sklearn.datasets import fetch_olivetti_faces
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.model_selection import learning_curve
from sklearn.pipeline import Pipeline

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
SPLIT_PATH = DATA_DIR / "split.joblib"
MODEL_PATH = DATA_DIR / "model.joblib"

# --- config -----------------------------------------------------------
N_HOLDOUT_IDENTITIES = 5   # reserved entirely as "not yet enrolled" -> live enrollment demo
N_TEST_PER_IDENTITY = 3    # held out per enrolled identity -> "simulated live captures"
RANDOM_STATE = 42
IMAGE_SHAPE = (64, 64)     # ORL face image dimensions


def _default_student_names(n_people):
    return {i: f"Student_{i + 1:02d}" for i in range(n_people)}


# --- data loading & split ----------------------------------------------
def load_and_split_data():
    """
    Loads ORL faces, reserves N_HOLDOUT_IDENTITIES entirely (for the live
    enrollment demo), and splits the rest into train / held-out-test per
    identity. Saves the split to disk so it only needs to be computed once
    and both members work from the same data.
    """
    data = fetch_olivetti_faces()
    X, y = data.images, data.target  # X: (400, 64, 64) floats in [0, 1], y: (400,)
    n_people = len(np.unique(y))

    rng = np.random.RandomState(RANDOM_STATE)
    all_ids = np.arange(n_people)
    rng.shuffle(all_ids)
    holdout_ids = set(all_ids[:N_HOLDOUT_IDENTITIES].tolist())
    enrolled_ids = sorted(set(all_ids.tolist()) - holdout_ids)

    train_X, train_y, test_X, test_y = [], [], [], []
    holdout_images, holdout_labels = [], []

    for pid in range(n_people):
        idx = np.where(y == pid)[0]
        rng.shuffle(idx)
        if pid in holdout_ids:
            holdout_images.append(X[idx])
            holdout_labels.append(y[idx])
            continue
        test_idx = idx[:N_TEST_PER_IDENTITY]
        train_idx = idx[N_TEST_PER_IDENTITY:]
        train_X.append(X[train_idx]); train_y.append(y[train_idx])
        test_X.append(X[test_idx]); test_y.append(y[test_idx])

    split = {
        "train_X": np.concatenate(train_X),
        "train_y": np.concatenate(train_y),
        "test_X": np.concatenate(test_X),
        "test_y": np.concatenate(test_y),
        "not_yet_enrolled_images": np.concatenate(holdout_images),
        "not_yet_enrolled_labels": np.concatenate(holdout_labels),
        "enrolled_ids": enrolled_ids,
        "holdout_ids": sorted(holdout_ids),
        "student_names": _default_student_names(n_people),
    }
    joblib.dump(split, SPLIT_PATH)
    return split


def get_split():
    if SPLIT_PATH.exists():
        return joblib.load(SPLIT_PATH)
    return load_and_split_data()


def _flatten(images):
    return images.reshape(len(images), -1)


# --- training & evaluation ---------------------------------------------
def train_initial(n_components=100, classifier="svm", C=10, kernel="rbf", k=3, confidence_temperature=1.0):
    """
    Fits PCA + the chosen classifier on the currently enrolled students,
    evaluates on the held-out test set, and saves the bundle to disk.
    Called on Day 3 for the first fit, and again by enroll_new_student().

    confidence_temperature: scales SVM decision margins before the softmax
    used to compute confidence in predict(). 1.0 = no change. Values below
    1.0 sharpen confidence (push correct predictions closer to 1.0); values
    above 1.0 soften it. This only affects the reported confidence number,
    not accuracy or which student gets predicted -- it's a standard
    calibration technique, not a change to the underlying model.
    """
    split = get_split()
    X_train = _flatten(split["train_X"])
    y_train = split["train_y"]
    X_test = _flatten(split["test_X"])
    y_test = split["test_y"]

    pca = PCA(n_components=min(n_components, len(X_train) - 1), whiten=True, random_state=RANDOM_STATE)
    X_train_pca = pca.fit_transform(X_train)
    X_test_pca = pca.transform(X_test)

    if classifier == "svm":
        clf = SVC(C=C, kernel=kernel, random_state=RANDOM_STATE)
    elif classifier == "knn":
        clf = KNeighborsClassifier(n_neighbors=k)
    elif classifier == "logreg":
        clf = LogisticRegression(max_iter=2000)
    else:
        raise ValueError(f"Unknown classifier: {classifier}")

    clf.fit(X_train_pca, y_train)

    y_pred = clf.predict(X_test_pca)
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="macro", zero_division=0
    )
    cm = confusion_matrix(y_test, y_pred)

    bundle = {
        "pca": pca,
        "clf": clf,
        "classifier_name": classifier,
        "confidence_temperature": confidence_temperature,
        "metrics": {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1},
        "confusion_matrix": cm,
        "labels": sorted(np.unique(y_train).tolist()),
    }
    joblib.dump(bundle, MODEL_PATH)
    return bundle


def compare_classifiers(n_components=100):
    """
    Trains SVM, kNN, and Logistic Regression on the same split and returns
    their metrics side by side. Used by the Admin page's comparison table.
    Does NOT overwrite the saved 'active' model -- call train_initial()
    separately for whichever one you want deployed.
    """
    results = {}
    for name in ("svm", "knn", "logreg"):
        bundle = train_initial(n_components=n_components, classifier=name)
        results[name] = bundle["metrics"]
    return results


def get_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return train_initial()


# --- inference interface (what Member 2 calls) --------------------------
def predict(image):
    """
    image: a (64, 64) grayscale array (float 0-1), e.g. one of the held-out
    'simulated capture' images returned by get_simulated_capture().
    Returns (predicted_student_id, confidence in [0, 1]).

    Note: for SVM, confidence comes from softmax over decision_function()
    margins rather than predict_proba(). SVC's predict_proba relies on
    Platt-scaling calibration via internal cross-validation, which is
    unreliable when there are very few training images per class (as here) --
    it can report low confidence even for predictions that are actually
    correct and confident. decision_function's margins don't have this
    problem. kNN and Logistic Regression don't need this workaround; their
    predict_proba is already consistent with predict().
    """
    bundle = get_model()
    clf = bundle["clf"]
    temperature = bundle.get("confidence_temperature", 1.0)
    flat = np.asarray(image).reshape(1, -1)
    flat_pca = bundle["pca"].transform(flat)

    if hasattr(clf, "decision_function"):
        scores = clf.decision_function(flat_pca)[0] / temperature
        exp_scores = np.exp(scores - scores.max())
        proba = exp_scores / exp_scores.sum()
    else:
        proba = clf.predict_proba(flat_pca)[0]

    pred_idx = int(np.argmax(proba))
    pred_label = int(clf.classes_[pred_idx])
    confidence = float(proba[pred_idx])
    return pred_label, confidence


def get_enrolled_students():
    split = get_split()
    names = split["student_names"]
    return {pid: names[pid] for pid in split["enrolled_ids"]}


def get_not_yet_enrolled_students():
    split = get_split()
    names = split["student_names"]
    return {pid: names[pid] for pid in split["holdout_ids"]}


def get_simulated_capture(student_id, index=0):
    """Returns one held-out image for a student, standing in for a fresh webcam capture."""
    split = get_split()
    mask = split["test_y"] == student_id
    images = split["test_X"][mask]
    if len(images) == 0:
        # student was enrolled live and has no held-out test images yet;
        # fall back to one of their training images instead.
        mask = split["train_y"] == student_id
        images = split["train_X"][mask]
    return images[index % len(images)]


def enroll_new_student(student_id, images, classifier="svm", C=10, kernel="rbf", confidence_temperature=None):
    """
    Member 1: adds a new student's images into the training set and retrains
    the deployed model. images: array of (64,64) images for this student
    (typically pulled from the 'not yet enrolled' pool for the demo).

    confidence_temperature: if not given, keeps whatever temperature the
    currently deployed model is using, so enrolling a student doesn't
    silently reset any tuning already applied.
    """
    if confidence_temperature is None:
        confidence_temperature = get_model().get("confidence_temperature", 1.0)
    split = get_split()
    split["train_X"] = np.concatenate([split["train_X"], images])
    split["train_y"] = np.concatenate([split["train_y"], np.full(len(images), student_id)])
    if student_id not in split["enrolled_ids"]:
        split["enrolled_ids"].append(student_id)
        split["enrolled_ids"] = sorted(split["enrolled_ids"])
    if student_id in split["holdout_ids"]:
        split["holdout_ids"].remove(student_id)
    joblib.dump(split, SPLIT_PATH)
    return train_initial(classifier=classifier, C=C, kernel=kernel, confidence_temperature=confidence_temperature)


def get_eigenfaces(n=10):
    """
    Returns the top n PCA components ('eigenfaces') reshaped back into
    (64, 64) images, for visualization on the Admin page.
    """
    bundle = get_model()
    pca = bundle["pca"]
    n = min(n, pca.components_.shape[0])
    return pca.components_[:n].reshape(n, *IMAGE_SHAPE)


def compute_learning_curve(n_components=100, classifier="svm", C=10, kernel="rbf", k=3):
    """
    Computes a learning curve (train size vs train/validation accuracy) for
    bias-variance diagnosis, as covered in the course's 'Learning Curve
    Analysis' section.

    Uses an sklearn Pipeline so PCA is refit on each fold's OWN training
    portion only -- per the course notes' caution to never fit PCA using
    validation/test data.
    """
    split = get_split()
    X = _flatten(np.concatenate([split["train_X"], split["test_X"]]))
    y = np.concatenate([split["train_y"], split["test_y"]])

    if classifier == "svm":
        clf = SVC(C=C, kernel=kernel, random_state=RANDOM_STATE)
    elif classifier == "knn":
        clf = KNeighborsClassifier(n_neighbors=k)
    elif classifier == "logreg":
        clf = LogisticRegression(max_iter=2000)
    else:
        raise ValueError(f"Unknown classifier: {classifier}")

    cv = 3
    train_sizes_frac = np.linspace(0.3, 1.0, 5)
    # learning_curve trains on shrinking slices of data (that's the point --
    # to see how accuracy changes with training size). PCA's n_components
    # must stay below the SMALLEST slice it will ever see, not just the
    # full dataset, or the smallest few points fail with a ValueError.
    approx_max_train = len(X) * (cv - 1) / cv
    smallest_fold_size = int(approx_max_train * train_sizes_frac.min())
    safe_n_components = max(2, min(n_components, smallest_fold_size - 1))

    pipe = Pipeline([
        ("pca", PCA(n_components=safe_n_components, whiten=True, random_state=RANDOM_STATE)),
        ("clf", clf),
    ])

    train_sizes, train_scores, val_scores = learning_curve(
        pipe, X, y, cv=cv, train_sizes=train_sizes_frac,
        scoring="accuracy", random_state=RANDOM_STATE,
    )
    return {
        "train_sizes": train_sizes.tolist(),
        "train_mean": train_scores.mean(axis=1).tolist(),
        "val_mean": val_scores.mean(axis=1).tolist(),
        "n_components_used": safe_n_components,
        "n_components_requested": n_components,
    }


def get_model_stats():
    bundle = get_model()
    return {
        "classifier_name": bundle["classifier_name"],
        **bundle["metrics"],
        "n_students": len(get_enrolled_students()),
    }
