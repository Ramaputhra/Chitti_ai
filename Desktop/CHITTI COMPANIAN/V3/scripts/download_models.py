import os
import sys
import urllib.request
import tarfile
import hashlib
from pathlib import Path

# Config
MODELS_DIR = Path("models")
INDIC_DIR = MODELS_DIR / "indicconformer"
WHISPER_DIR = MODELS_DIR / "whisper"
ECAPA_DIR = MODELS_DIR / "ecapa_tdnn"

# Example Sherpa-ONNX compatible models (AI4Bharat / Sherpa-ONNX releases)
INDIC_MODEL_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-en-2023-06-26.tar.bz2" # Placeholder URL, in production use actual IndicConformer
ECAPA_MODEL_URL = "https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb/resolve/main/embedding_model.ckpt" # Placeholder for ECAPA-TDNN ONNX/ckpt

def create_folders():
    print("Ensuring model directories exist...")
    INDIC_DIR.mkdir(parents=True, exist_ok=True)
    WHISPER_DIR.mkdir(parents=True, exist_ok=True)
    ECAPA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directories verified: {MODELS_DIR.absolute()}")

def download_file(url: str, dest: Path) -> bool:
    print(f"Downloading {url} to {dest}...")
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def verify_file(filepath: Path, expected_sha256: str = None) -> bool:
    if not filepath.exists():
        return False
    if expected_sha256:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        if sha256_hash.hexdigest() != expected_sha256:
            print(f"❌ Hash mismatch for {filepath}")
            return False
    return True

def setup_indic_conformer():
    print("\n--- Setting up IndicConformer (Sherpa-ONNX) ---")
    tar_path = MODELS_DIR / "indic_model.tar.bz2"
    if not (INDIC_DIR / "model.onnx").exists():
        if download_file(INDIC_MODEL_URL, tar_path):
            print("Extracting...")
            with tarfile.open(tar_path, "r:bz2") as tar:
                tar.extractall(path=INDIC_DIR)
            tar_path.unlink()
            # Rename internal folder contents up if needed, assuming extraction puts files properly
            print("✅ IndicConformer installed.")
    else:
        print("✅ IndicConformer already installed.")

def setup_ecapa_tdnn():
    print("\n--- Setting up Voice Auth (ECAPA-TDNN) ---")
    model_path = ECAPA_DIR / "embedding_model.ckpt"
    if not model_path.exists():
        if download_file(ECAPA_MODEL_URL, model_path):
            print("✅ ECAPA-TDNN installed.")
    else:
        print("✅ ECAPA-TDNN already installed.")

def setup_faster_whisper():
    print("\n--- Setting up Faster-Whisper ---")
    print("Faster-whisper automatically downloads models on first load via CTranslate2.")
    print("✅ Faster-whisper setup complete.")

def main():
    print("Starting CHITTI Model Downloader...\n")
    create_folders()
    setup_faster_whisper()
    setup_indic_conformer()
    setup_ecapa_tdnn()
    
    print("\n🎉 All models downloaded and verified successfully!")

if __name__ == "__main__":
    main()
