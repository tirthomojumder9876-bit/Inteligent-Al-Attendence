# SnapClass — AI-Powered Dual-Modality Classroom Attendance

SnapClass is a web-based attendance system that replaces manual roll call with **face and voice recognition**, while keeping a teacher firmly in control of every attendance decision. Built with Streamlit and a Supabase (PostgreSQL) backend, it runs entirely from a browser — no dedicated hardware, no app installs, just a webcam and a microphone.

## The Problem

Reading names aloud wastes class time, and it's trivial for one student to answer for an absent friend. Existing "digital" solutions like QR check-ins or app taps don't actually verify *who* is checking in — they just move the same trust problem online.

## Our Approach

SnapClass verifies attendance using two independent biometric signals instead of one:

- **Face recognition** — dlib's HOG detector locates faces in a classroom photo, encodes each into a 128-dimensional embedding, and a per-class SVM classifier matches it against enrolled students. A secondary distance check rejects any face that isn't confidently close to an enrolled student, instead of forcing a guess.
- **Voice recognition** — Resemblyzer generates speaker embeddings from short audio clips; `librosa` splits a classroom recording into individual speech segments, and each is matched by cosine similarity against enrolled students' voice profiles.

Critically, **neither pipeline writes to the database on its own.** Every automated match is shown to the teacher — complete with the source photo or audio segment behind it — and only saved after an explicit "Confirm & Save." A "Discard" clears a bad result instantly. This human-in-the-loop step is intentional: it's what makes an imperfect AI model safe to use for something as consequential as an attendance record.

## Key Features

-  **Face-ID login & registration** for students — new faces trigger an on-the-spot profile creation flow (name + optional voice sample)
-  **Dual biometric attendance capture** — teachers can run face analysis, voice analysis, or both, per session
-  **Teacher dashboard** — create subjects, share join codes/QR codes, take attendance, and review historical records
-  **Student dashboard** — view enrolled subjects and personal attendance history
-  **Mandatory human review** before any attendance record is saved — no automated decision is ever final
-  **Secure by design** — bcrypt-hashed teacher passwords, and only numerical embeddings (never raw photos/audio) are stored in the database

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Face recognition | dlib, face_recognition_models, scikit-learn |
| Voice recognition | Resemblyzer, librosa, PyTorch |
| Backend | Supabase (PostgreSQL) |
| Auth | bcrypt |
| Utilities | segno (QR codes), pandas, Pillow |

## Project Context

Built as a course project for **CSE445 (Section 7)** at North South University by **Group 3**: Tirtho Mojumdar, Ramisa Anjum, Md Rakibul Hasan, and Hafsa Amin Ela.
