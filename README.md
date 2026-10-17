# 🎓 SnapClass — AI-Powered Dual-Modality Classroom Attendance

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Backend-Supabase%20(PostgreSQL)-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![PyTorch](https://img.shields.io/badge/AI-PyTorch%20%7C%20dlib%20%7C%20scikit--learn-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**SnapClass** is a browser-based classroom attendance system that replaces manual roll calls with **dual-modality biometric verification (face and voice recognition)** while keeping the instructor firmly in control through a human-in-the-loop review workflow. Built with **Streamlit** and **Supabase (PostgreSQL)**, it runs entirely in the browser using a standard webcam and microphone—no dedicated hardware or client app installations required.

---

## 📌 Problem Statement

Traditional roll calls consume valuable lecture time and are vulnerable to proxy attendance. Meanwhile, common digital alternatives—such as QR code check-ins or mobile app taps—only verify *device presence* rather than *student identity*, shifting the same trust issue online without solving it.

---

## 🧠 Core Architecture & Approach

SnapClass verifies student presence using two independent biometric pipelines paired with mandatory instructor verification:

```text
[Classroom Photo / Audio] 
        │
        ├─► Face Pipeline:  dlib HOG Detection ──► 128-D Embedding ──► Per-Class SVM + Distance Threshold
        │
        └─► Voice Pipeline: librosa Segmentation ──► Resemblyzer 256-D Embedding ──► Cosine Similarity Match
                                                      │
                                                      ▼
                                     [ Teacher Review Dashboard ]
                                     (Inspect Source Photo / Audio)
                                        ├── ✅ Confirm & Save ──► Supabase (PostgreSQL)
                                        └── ❌ Discard
```

### 1. Facial Recognition Pipeline
* **Detection & Encoding:** Uses `dlib`’s HOG (Histogram of Oriented Gradients) face detector to locate faces in classroom snapshots and project each face into a **128-dimensional embedding**.
* **Classification & Open-Set Rejection:** A per-class **Support Vector Machine (SVM)** classifier matches embeddings against enrolled students, while a secondary Euclidean distance check rejects unknown or low-confidence faces instead of forcing false-positive guesses.

### 2. Voice Recognition Pipeline
* **Segmentation:** Uses `librosa` to split continuous classroom audio recordings into discrete individual speech segments.
* **Speaker Verification:** Generates **256-dimensional speaker embeddings** via `Resemblyzer` (PyTorch) and matches each segment against enrolled student voice profiles using **cosine similarity**.

### 3. Human-in-the-Loop Verification
Neither AI pipeline writes directly to the database. Every automated prediction is surfaced on the instructor's screen alongside the exact cropped face or audio segment that triggered it. Records are committed to Supabase only after the instructor clicks **"Confirm & Save"**—or cleared immediately via **"Discard"**.

---

## ✨ Key Features

* **Zero-Friction Biometric Onboarding:** Students log in via Face-ID; unrecognized faces automatically trigger a guided registration flow to capture the student's name, facial encoding, and optional voice sample.
* **Flexible Attendance Capture:** Instructors can run facial recognition, voice recognition, or both modalities within a single session.
* **Instructor Dashboard:** Create and manage subjects, generate shareable join codes and downloadable QR codes (`segno`), verify AI attendance matches, and audit historical attendance logs.
* **Student Dashboard:** Enroll in subjects via join code and track personal attendance history across courses.
* **Privacy & Security by Design:** 
  * Raw classroom photos and voice recordings are **never stored** in the database—only numerical embeddings are persisted.
  * Instructor accounts are protected with `bcrypt` password hashing.

---

## 🛠️ Tech Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend & UI** | Streamlit |
| **Face Recognition** | `dlib`, `face_recognition_models`, `scikit-learn` (SVM) |
| **Voice Recognition** | `Resemblyzer`, `librosa`, `PyTorch` |
| **Database & Backend** | Supabase (PostgreSQL) |
| **Authentication** | `bcrypt` |
| **Utilities** | `segno` (QR code generation), `pandas`, `Pillow` |

---

## 🚀 Getting Started

### 1. Prerequisites
* **Python 3.9+**
* CMake and a C++ compiler (required for building `dlib`)
* A [Supabase](https://supabase.com/) project (PostgreSQL database)

### 2. Clone the Repository
```bash
git clone [https://github.com/tirthomojumder9876-bit/Inteligent-Al-Attendence.git](https://github.com/tirthomojumder9876-bit/Inteligent-Al-Attendence.git)
cd Inteligent-Al-Attendence
```

### 3. Set Up a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` file or `.streamlit/secrets.toml` in the project root with your Supabase credentials:

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "[https://your-project-id.supabase.co](https://your-project-id.supabase.co)"
SUPABASE_KEY = "your-anon-or-service-role-key"
```

### 6. Run the Application
```bash
streamlit run app.py
```
*(Replace `app.py` with your main entry-point script if named differently.)*

---

## 🎓 Academic Context & Team

Developed as a capstone course project for **CSE445 (Machine Learning — Section 7)** at **North South University (NSU)**.

**Group 3 Contributors:**
* **Tirtho Mojumdar** — [@tirthomojumder9876-bit](https://github.com/tirthomojumder9876-bit)
* **Ramisa Anjum**
* **Md Rakibul Hasan**
* **Hafsa Amin Ela**

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
