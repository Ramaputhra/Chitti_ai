import wave
import sys
import os

model_path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop\models\piper\en_US-lessac-medium.onnx"

def main():
    try:
        from piper.voice import PiperVoice
        voice = PiperVoice.load(model_path=model_path, config_path=model_path + ".json")
        
        text = "Hello."
        for chunk in voice.synthesize(text):
            print("AudioChunk attributes:")
            for attr in dir(chunk):
                if not attr.startswith('_'):
                    print(f" - {attr}: {type(getattr(chunk, attr))}")
            break
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
