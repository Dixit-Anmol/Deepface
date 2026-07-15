# ==============================================================================
# Debugging / Real-Time Speech Emotion Recognition Experiment
#
# Requirements installation instructions:
#   pip install transformers torch sounddevice librosa scipy soundfile numpy
# ==============================================================================

import warnings
warnings.filterwarnings("ignore")

import logging
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

import os
import sys
import time
import tempfile
import contextlib
import numpy as np

try:
    import torch
    import librosa
    import sounddevice as sd
    import soundfile as sf
    from transformers import AutoProcessor, AutoModelForAudioClassification
except ImportError as e:
    print(f"Dependency Error: {e}")
    print("Please install the required libraries by running:")
    print("pip install transformers torch sounddevice librosa scipy soundfile numpy")
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


# Global variables
MODEL_ID = "Dpngtm/wav2vec2-emotion-recognition"
CONFIDENCE_HISTORY = []
HISTORY_LIMIT = 5
SILENCE_THRESHOLD = 0.003  # RMS energy threshold for speech activity detection


def load_model():
    """Loads and caches the Hugging Face model and processor."""
    print("Loading model...")
    try:
        with suppress_outputs():
            processor = AutoProcessor.from_pretrained(MODEL_ID)
            model = AutoModelForAudioClassification.from_pretrained(MODEL_ID)
        return processor, model
    except Exception as e:
        print(f"Model Loading Failure: Could not load Hugging Face model '{MODEL_ID}'. Details: {e}")
        sys.exit(1)


def record_audio(duration=5, target_sr=16000):
    """Captures audio from default input device (microphone) for the given duration."""
    print("Listening...")
    try:
        device_info = sd.query_devices(kind='input')
        input_sr = int(device_info['default_samplerate'])
    except Exception as e:
        print(f"Error checking microphone devices: {e}")
        print("Please check if your microphone is plugged in and accessible.")
        return None

    try:
        recording = sd.rec(int(duration * input_sr), samplerate=input_sr, channels=1, dtype='float32')
        sd.wait()  # Block until the recording completes
        print("Recording Complete\n")
        
        audio_data = recording.flatten()
        
        # Resample to 16kHz if the hardware samplerate is different
        if input_sr != target_sr:
            audio_data = librosa.resample(audio_data, orig_sr=input_sr, target_sr=target_sr)
            
        return audio_data
    except Exception as e:
        print(f"\nRecording Interrupted or Failed: {e}")
        return None


def preprocess_audio(audio_data):
    """Applies volume normalization to the audio signal."""
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        audio_data = audio_data / max_val
    return audio_data


def predict_emotion(audio_path, processor, model):
    """
    Inference helper that runs the preprocessing and prediction pipeline,
    printing debugging data, raw logits, softmax probabilities, and prediction results.
    """
    try:
        # Load audio using librosa (Step 9: ensure identical loading path)
        audio, sr = librosa.load(audio_path, sr=16000, mono=True)
        
        # Volume normalization preprocessing (Step 9: same preprocessing)
        audio = preprocess_audio(audio)
        
        # Gather info (Step 4: debug info)
        duration = len(audio) / sr
        rms_energy = np.sqrt(np.mean(audio**2))
        
        print("\n====================================")
        print("Recording Information")
        print(f"Duration:           {duration:.2f} seconds")
        print(f"Sample Rate:        {sr} Hz")
        print(f"Channels:           1 (Mono)")
        print(f"Maximum Amplitude:  {np.max(audio):.4f}")
        print(f"Minimum Amplitude:  {np.min(audio):.4f}")
        print(f"Mean:               {np.mean(audio):.4f}")
        print(f"Standard Deviation: {np.std(audio):.4f}")
        print(f"RMS Energy:         {rms_energy:.4f}")
        print("====================================")
        
        # Silence check
        if rms_energy < SILENCE_THRESHOLD:
            print("Silence detected (empty audio)... skipping prediction.")
            return None, 0.0

        # Predict
        inference_start = time.time()
        with suppress_outputs():
            inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
            with torch.no_grad():
                logits = model(**inputs).logits[0]
                probabilities = torch.softmax(logits, dim=-1)
        inference_end = time.time()
        
        # Step 5: Print Raw Logits
        print("\nRaw Logits")
        print(logits)
        
        # Mapping labels
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
            
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
        # Step 6: Print Softmax Probabilities
        print("\nSoftmax Probabilities\n")
        for emotion, score in sorted_scores:
            print(f"{emotion:<12}: {score:.2f}%")
            
        # Step 7: Print Predicted Emotion and Confidence
        predicted_emotion, confidence = sorted_scores[0]
        print(f"\nPredicted Emotion : {predicted_emotion}")
        print(f"Confidence        : {confidence:.2f}%")
        print(f"Inference Time    : {inference_end - inference_start:.2f}s")
        
        # Play the recorded audio back automatically (Step 2 - optional)
        try:
            # Play audio in the background asynchronously
            sd.play(audio, 16000)
        except Exception:
            pass
            
        return scores, (inference_end - inference_start)
    except Exception as e:
        print(f"Audio processing or inference failure: {e}")
        return None, 0.0


def main():
    """Main execution entry point."""
    
    # 1. Load model once on startup
    processor, model = load_model()
    
    # Step 8: check if file path is provided as CLI argument
    if len(sys.argv) > 1:
        test_file_path = sys.argv[1]
        print(f"\n--- Testing Existing File: {test_file_path} ---")
        predict_emotion(test_file_path, processor, model)
        sys.exit(0)
        
    # Otherwise run microphone loop
    print("=========================================================")
    print("  Real-Time Speech Emotion Recognition System (Debug)")
    print("  Press Ctrl+C to stop recording.")
    print("=========================================================")

    # Check if microphone is connected
    try:
        sd.query_devices(kind='input')
    except Exception as e:
        print(f"Hardware Error: No audio input device (microphone) detected: {e}")
        sys.exit(1)

    # Ensure recordings/ directory exists (Step 1)
    if not os.path.exists("recordings"):
        os.makedirs("recordings")
        
    print("\nSystem listening loop initialized. Speak now...\n")
    
    try:
        recording_idx = 1
        while True:
            # Find next filename that doesn't exist to avoid overwriting
            while os.path.exists(f"recordings/recording_{recording_idx}.wav"):
                recording_idx += 1
            saved_path = f"recordings/recording_{recording_idx}.wav"
            
            print("\n------------------------------------")
            # Capture audio from mic
            audio_samples = record_audio(duration=5, target_sr=16000)
            if audio_samples is None:
                time.sleep(1)
                continue
                
            # Save raw recorded audio to recordings/ directory permanently (Step 1 & 2)
            try:
                sf.write(saved_path, audio_samples, 16000)
                print(f"Saved recording to: {saved_path}")
            except Exception as e:
                print(f"Failed to save recording to disk: {e}")
                continue
                
            # Predict emotion immediately using the exact same path and process function (Step 3)
            print("Processing...")
            scores, inf_time = predict_emotion(saved_path, processor, model)
            
            if scores is not None:
                sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
                predicted_emotion, confidence = sorted_scores[0]
                
                # Add to rolling history of predictions
                CONFIDENCE_HISTORY.append(confidence)
                if len(CONFIDENCE_HISTORY) > HISTORY_LIMIT:
                    CONFIDENCE_HISTORY.pop(0)
                avg_confidence = sum(CONFIDENCE_HISTORY) / len(CONFIDENCE_HISTORY)
                
                top_3_str = ", ".join([f"{emo} ({val:.1f}%)" for emo, val in sorted_scores[:3]])
                print(f"Top 3 Predictions : {top_3_str}")
                print(f"Average Confidence (Last {len(CONFIDENCE_HISTORY)} predictions): {avg_confidence:.2f}%")
                
            print("------------------------------------")
            
    except KeyboardInterrupt:
        print("\nStopping real-time speech recognition system. Exiting gracefully.")


if __name__ == "__main__":
    main()
