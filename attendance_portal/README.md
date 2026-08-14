# Attendance Verification Portal

A face-recognition attendance system built for CSE445 (Machine Learning). Students
"log in" by claiming an identity, the system captures a face image, runs it through
a trained classical ML pipeline, and marks attendance only if the face matches the
claimed identity with high enough confidence.

## What this actually is

- **The ML core**: PCA (eigenfaces) for dimensionality reduction + a trained
  classifier (SVM / kNN / Logistic Regression, compared against each other) for
  identification. Fully trained from scratch on the ORL (AT&T) face dataset —
  no pretrained face-recognition models are used anywhere in the deployed system.
- **The "students"**: due to not having access to real student biometric data,
  the 40 identities in the ORL dataset stand in for an enrolled student roster.
  This is a proof-of-concept / simulation, stated openly rather than implied —
  see "Known limitations" below.
- **The system**: a two-page Streamlit app. One page is the admin/model-training
  side, the other is the student-facing login/attendance side. Both share one
  trained pipeline, so enrolling someone on the admin page makes them immediately
  recognizable on the login page.

## Project structure

```
attendance_portal/
├── Home.py                        landing page, links to both sides of the app
├── theme.py                       shared visual styling + the verification readout component
├── model/
│   └── pipeline.py                all ML logic: data split, PCA, training, prediction, enrollment
├── pages/
│   ├── 1_Admin_Enrollment.py      Member 1: enrollment, tuning, model performance
│   └── 2_Login_Attendance.py      Member 2: login, verification, attendance log
├── scripts/
│   └── batch_verification_test.py   automated genuine/impostor testing, produces FAR/FRR numbers
├── data/                          generated at runtime: trained model, data split, test results
├── attendance_log.csv             generated at runtime: every login attempt, timestamped
├── .streamlit/config.toml         dark theme colors for native Streamlit widgets
└── requirements.txt
```

## Setup

```
pip install -r requirements.txt
streamlit run Home.py
```

If `streamlit` or `pip` aren't recognized on Windows, use `python -m streamlit run Home.py`
and `python -m pip install -r requirements.txt` instead.

The first run downloads the ORL faces dataset automatically (via scikit-learn) and
trains an initial model — this takes a few seconds.

## How to use it

**Admin & Enrollment page:**
1. View live model stats (accuracy, active classifier, students enrolled).
2. Run the SVM vs kNN vs Logistic Regression comparison.
3. View the eigenfaces (top PCA components).
4. Tune hyperparameters (PCA components, classifier, C/kernel or k, confidence
   temperature) and click "Train with these settings" to actually redeploy that
   configuration — this is what the Login page uses.
5. Optionally compute a learning curve for the current settings (bias/variance
   diagnostic — doesn't change the deployed model).
6. Enroll one of the 5 reserved ("not yet enrolled") students to simulate a new
   student joining — this retrains the model live.

**Login & Attendance page:**
1. Pick a student ID (simulating login).
2. Choose a genuine attempt (their own held-out photo) or an impostor attempt
   (someone else's photo, claimed under this ID).
3. Click "Mark attendance" — see the verification readout (confidence, threshold
   bar, VERIFIED/REJECTED stamp).
4. Check the attendance log at the bottom.

Runs every enrolled student's held-out images as genuine attempts, plus up to 300
impostor pairings, and reports True Accept Rate, False Reject Rate, False Accept
Rate, and True Reject Rate. Results are also saved to `data/batch_verification_results.csv`.
