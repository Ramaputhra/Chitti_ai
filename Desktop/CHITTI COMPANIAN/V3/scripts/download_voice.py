import os
import urllib.request
import zipfile
import tarfile
import json

def download_voice(dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    
    # Fetch all voices from voices.json
    print("Fetching voice registry...")
    voices_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json"
    req = urllib.request.urlopen(voices_url)
    data = json.loads(req.read())
    
    # Find Amy voice
    en_voice = "en_US-amy-medium"
    
    if en_voice not in data:
        print("Could not find Amy voice. Defaulting to first available.")
        en_voice = list(data.keys())[0]
        
    model_id = en_voice
    
    # Get direct file urls from voices.json
    files = data[model_id]['files']
    
    onnx_url = None
    json_url = None
    for f in files:
        if f.endswith('.onnx'):
            onnx_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/{f}"
        elif f.endswith('.onnx.json'):
            json_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/{f}"
            
    onnx_path = os.path.join(dest_dir, f"{model_id}.onnx")
    json_path = os.path.join(dest_dir, f"{model_id}.onnx.json")
    
    print(f"Downloading {model_id} model...")
    urllib.request.urlretrieve(onnx_url, onnx_path)
    
    print(f"Downloading {model_id} config...")
    urllib.request.urlretrieve(json_url, json_path)
    
    print(f"Voice {model_id} successfully downloaded to {dest_dir}!")
    
    # Return the actual voice name so we can instruct the user
    return model_id

if __name__ == "__main__":
    dest = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop\models\piper"
    model_id = download_voice(dest)
    print(f"\nIMPORTANT: Open your preview scripts and ensure the model path points to: {model_id}.onnx")
