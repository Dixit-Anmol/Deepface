# Onboarding Progress Report - Day 3: Speech Emotion Recognition (SER)

## 1. Introduction to SER
* **Definition**: Identifying the speaker's emotional state using only their voice (focuses on *how* it is spoken, not *what* is spoken).
* **Key Acoustic Cues**: Pitch, loudness, rhythm, speech rate, and spectral characteristics.
* **Applications**:
  - Human-Computer Interaction (HCI)
  - Mental Health Monitoring
  - Customer Service Analytics & Call Centers
  - Emotion-aware AI Systems (Virtual Assistants, Robotics, Gaming)

---

## 2. ASR vs. SER
| Metric | Speech Recognition (ASR) | Speech Emotion Recognition (SER) |
| :--- | :--- | :--- |
| **Input** | Voice Audio | Voice Audio |
| **Output** | Literal text transcript (e.g., *"I am feeling happy today"*) | Emotional state label (e.g., *Happy*) |
| **Goal** | Transcribe spoken words | Infer internal mood/feeling |
| **Common Models** | Whisper, Wav2Vec2 ASR, DeepSpeech | Wav2Vec2 SER, HuBERT, WavLM, SpeechBrain |

---

## 3. Core Challenges in SER
* **Speaker Variability**: Normal voice pitch and speech rates differ significantly across individuals.
* **Background Noise**: Keyboard typing, echo, fans, and low-quality microphone hardware degrade predictions.
* **Emotion Overlap**: High-energy emotions (e.g., Fear vs. Excitement) or low-energy emotions (e.g., Sadness vs. Calmness) share similar acoustics.
* **Language/Culture**: Models are heavily trained on English, making accents and non-English expressions harder to generalise.

---

## 4. Wav2Vec2 Architecture
* Developed by Meta AI; learns representations directly from raw audio waveforms (no handcrafted feature extraction like MFCCs).
* **Processing Flow**:
  ```
  Raw Waveform ──> Feature Encoder (CNN) ──> Transformer (Self-Attention) ──> Classification Head ──> Emotion Label
  ```

---

## 5. Key Acoustic Features Used
* **Pitch (F0)**: Most critical factor (e.g., high unstable pitch indicates Fear; high strong pitch indicates Anger).
* **Loudness / Energy**: High energy points to Anger/Excitement; low energy points to Sadness.
* **Speaking Rate**: Happy is generally fast; Sad is generally slow/paused.
* **Prosody & Intonation**: Rhythm and emphasis are key indicators of the vocal expression.

---

## 6. Dataset & Testing Evaluation
* **Offline Dataset**: Evaluated on professionally recorded datasets from Kaggle (English emotional speech), achieving high accuracy due to clean recording environments.
* **Live Microphone Testing**:
  - Fixed virtual microphone routing issues (switched to AMD Microphone Array).
  - Obtained 80-90% accuracy under clean indoor conditions.
* **Language Generalization (Hindi)**: 
  - Although the model was trained primarily on English datasets, testing showed that it **successfully and accurately predicts emotions from Hindi audio inputs** as well. This indicates that speech emotion models capture universal prosodic and pitch features that transcend language boundaries.


