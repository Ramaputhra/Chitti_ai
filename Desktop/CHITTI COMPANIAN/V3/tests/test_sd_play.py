import sys
import os
import numpy as np

model_path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop\models\piper\en_US-lessac-medium.onnx"

def main():
    try:
        from piper.voice import PiperVoice
        voice = PiperVoice.load(model_path=model_path, config_path=model_path + ".json")
        
        text = "Hello, this is a test using the sounddevice play method."
        print("Synthesizing audio...")
        
        audio_arrays = []
        for chunk in voice.synthesize(text):
            if hasattr(chunk, 'audio_int16_array'):
                audio_arrays.append(chunk.audio_int16_array)
                
        if not audio_arrays:
            print("No audio arrays generated.")
            return
            
        full_audio = np.concatenate(audio_arrays)
        
        print("Playing audio...")
        import sounddevice as sd
        sd.play(full_audio, 22050, blocking=True)
        print("Playback finished!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
