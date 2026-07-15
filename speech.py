# ==============================================================================
# Speech Emotion Recognition (SER) using HuggingFace Wav2Vec2 Model
#
# Requirements installation instructions:
#   pip install torch librosa transformers soundfile
# ==============================================================================

import warnings
# Suppress python/framework warnings
warnings.filterwarnings("ignore")

import logging
# Set transformers and huggingface log levels to ERROR to keep terminal clean
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

import os
import sys
import time
import contextlib

try:
    import torch
    import librosa
    from transformers import AutoProcessor, AutoModelForAudioClassification
except ImportError as e:
    print(f"Dependency Error: {e}")
    print("Please install the required libraries by running:")
    print("pip install torch librosa transformers soundfile")
    sys.exit(1)


@contextlib.contextmanager
def suppress_outputs():
    """Context manager to suppress stdout and stderr output streams during loading and execution."""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


# Global variables for caching model load singleton pattern
_processor = None
_model = None
MODEL_ID = "Dpngtm/wav2vec2-emotion-recognition"

def load_model_once():
    """Loads and caches the Hugging Face model and processor only once."""
    global _processor, _model
    if _processor is None or _model is None:
        try:
            with suppress_outputs():
                # Download and initialize the processor and classification model
                _processor = AutoProcessor.from_pretrained(MODEL_ID)
                _model = AutoModelForAudioClassification.from_pretrained(MODEL_ID)
        except Exception as e:
            raise RuntimeError(f"Failed to load the model from Hugging Face. Details: {e}")
    return _processor, _model


def predict_emotion(audio_path: str):
    """
    Performs speech emotion recognition on a single wav file.
    
    Parameters:
        audio_path (str): The absolute or relative path to the input WAV audio file.
    """
    # 1. Error Handling - File Checks
    if not os.path.exists(audio_path):
        print(f"Error: File not found at '{audio_path}'.")
        return

    # Check extension
    if not audio_path.lower().endswith(".wav"):
        print(f"Error: Unsupported file extension. The program only supports '.wav' files.")
        return

    # 2. Loading the Model (Only once)
    print("Loading model...")
    try:
        processor, model = load_model_once()
    except Exception as e:
        print(e)
        return

    # 3. Processing Audio (librosa handles loading and automatic resampling to 16kHz)
    print("Processing audio...")
    try:
        # sr=16000 ensures audio is resampled to 16kHz if the sample rate is different.
        # mono=True ensures multi-channel audios are converted to a single channel.
        audio, sr = librosa.load(audio_path, sr=16000, mono=True)
    except Exception as e:
        print(f"Audio Processing Failure: Failed to load/read the audio file. Details: {e}")
        return

    # 4. Model Inference & Timing
    try:
        inference_start = time.time()
        
        with suppress_outputs():
            # Process input waveform to transformers tensor format
            inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
            
            with torch.no_grad():
                logits = model(**inputs).logits
                # Apply softmax normalization so the class predictions sum to ~100%
                probabilities = torch.softmax(logits, dim=-1)[0]
                
        inference_end = time.time()
    except Exception as e:
        print(f"Audio Processing Failure: Inference execution failed. Details: {e}")
        return

    # 5. Extract and Map Outputs
    # Original model labels: {0: 'angry', 1: 'calm', 2: 'disgust', 3: 'fearful', 4: 'happy', 5: 'sad', 6: 'surprised'}
    # Mapping to human-friendly target labels
    label_mapping = {
        "angry": "Angry",
        "calm": "Neutral",
        "disgust": "Disgust",
        "fearful": "Fear",
        "happy": "Happy",
        "sad": "Sad",
        "surprised": "Surprise"
    }

    id2label = model.config.id2label
    scores = {}
    for idx, prob in enumerate(probabilities):
        original_label = id2label[idx]
        mapped_label = label_mapping.get(original_label, original_label.capitalize())
        scores[mapped_label] = prob.item() * 100

    # Sort probabilities from highest to lowest
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    predicted_emotion, confidence = sorted_scores[0]
    total_time = inference_end - inference_start

    # 6. Formatting and Displaying the Result
    print("\nEmotion Scores\n")
    for emotion, score in sorted_scores:
        print(f"{emotion:<12}: {score:.2f}%")

    print(f"\nPredicted Emotion: {predicted_emotion}")
    print(f"Confidence: {confidence:.2f}%")
    print(f"Inference Time: {total_time:.2f}s")


if __name__ == "__main__":
    # Test path:
    audio_path = r"recordings\recording_5.wav"
    predict_emotion(audio_path)