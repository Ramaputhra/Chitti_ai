import os
import sys
import json
import time
from datetime import datetime

# Add root directory to path so we can import desktop modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from desktop.platform.shared.models.biometrics import VoiceProfile
from desktop.platform.integrations.core.event_bus import EventBus
from desktop.services.audio.providers.sherpa_onnx_auth_provider import SherpaOnnxSpeakerVerifier

def wait_for_enter():
    input("\nPress Enter to begin recording...")

def record_audio(duration=5, samplerate=16000) -> bytes:
    import sounddevice as sd
    import numpy as np
    
    print(f"Recording for {duration} seconds. Please speak now...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    for i in range(duration):
        print(f"Recording... {duration-i}s remaining", end='\r')
        time.sleep(1)
    sd.wait()
    print("Recording complete!                 ")
    
    # Convert numpy array back to bytes
    return recording.tobytes()

def main():
    print("========================================")
    print("   CHITTI Initial Setup - Voice Profile   ")
    print("========================================\n")
    
    print("Hello! Let's recognize your voice so I can authenticate your commands.")
    owner_id = input("Please enter your name/owner ID (e.g. Rama): ").strip() or "Owner"
    
    print("\nInitializing Voice Engine...")
    import logging
    bus = EventBus(logger=logging.getLogger(__name__))
    verifier = SherpaOnnxSpeakerVerifier(bus)
    
    # Normally this would be downloaded via ModelManager (per Rule 9 from user)
    # For the script, we assume the user has a model at this path or provide instructions
    model_path = os.path.join("models", "voice", "sherpa_speaker_model.onnx")
    if not os.path.exists(model_path):
        print(f"\n[!] WARNING: Sherpa-ONNX speaker model not found at {model_path}.")
        print("Please use the Model Manager to download a speaker model first.")
        print("For testing purposes, we will mock the embedding extraction if the model fails to load.")
    
    verifier.load_model(model_path)
    
    embeddings = []
    
    sentences = [
        "Hi Chitti, wake up and initialize my workspace.",
        "Please open the browser and check my emails for today.",
        "Set the security mode to voice authentication only."
    ]
    
    for i, sentence in enumerate(sentences):
        print(f"\n--- Recording {i+1}/3 ---")
        print(f"Please read this sentence clearly:\n\n> \"{sentence}\"")
        wait_for_enter()
        
        audio_data = record_audio(duration=5)
        
        print("Extracting voice print...")
        embedding = verifier.extract_embedding(audio_data)
        
        if embedding:
            embeddings.append(embedding)
            print("Successfully extracted voice print!")
        else:
            print("Failed to extract voice print (Mocking embedding for demo).")
            embeddings.append([0.1, 0.2, 0.3, 0.4]) # mock
            
    print("\n--- Testing ---")
    print("Let's do one final test. Say anything you like for 3 seconds.")
    wait_for_enter()
    test_audio = record_audio(duration=3)
    
    print("Verifying...")
    state = verifier.verify(test_audio, reference_embeddings=embeddings, threshold=0.6)
    print(f"Recognition complete. Result: {state.name}")
    
    print("\n--- Saving Profile ---")
    profile = VoiceProfile(
        owner_id=owner_id,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        embeddings=embeddings,
        microphones_tested=["default_system_mic"],
        confidence_threshold=0.65,
        model_version="1.0",
        sample_count=len(embeddings)
    )
    
    profile_dir = os.path.join(os.path.dirname(__file__), '..', 'config', 'profiles')
    os.makedirs(profile_dir, exist_ok=True)
    profile_path = os.path.join(profile_dir, f"{owner_id.lower()}_voice_profile.json")
    
    # Using dataclasses asdict workaround for simple dict mapping
    import dataclasses
    with open(profile_path, 'w') as f:
        json.dump(dataclasses.asdict(profile), f, indent=4)
        
    print(f"\nVoice Profile successfully saved to {profile_path}!")
    print("Welcome aboard, boss.")
    
if __name__ == "__main__":
    main()
