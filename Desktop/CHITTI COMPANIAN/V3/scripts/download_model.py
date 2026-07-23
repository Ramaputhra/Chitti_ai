import os
import json
import logging
from huggingface_hub import hf_hub_download

"""
=========================================================
[Developer Utility — Temporary]
This script bypasses the Presentation Runtime to download 
model assets during early development. It should NOT survive 
into the end-user product. The ModelManager UI will replace this.
=========================================================
"""

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ModelManager")

def main():
    print("========================================")
    print("   CHITTI Model Manager - LLM Downloader  ")
    print("========================================\n")
    
    repo_id = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
    filename = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
    model_name = "qwen2.5-1.5b-instruct"
    
    # Calculate target directory relative to this script
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model_dir = os.path.join(base_dir, 'models', 'llm', model_name)
    os.makedirs(model_dir, exist_ok=True)
    
    target_model_path = os.path.join(model_dir, 'model.gguf')
    metadata_path = os.path.join(model_dir, 'metadata.json')
    
    if os.path.exists(target_model_path):
        print(f"✅ Model already exists at {target_model_path}.")
        return

    print(f"Downloading {filename} from {repo_id}...")
    try:
        # Download the file to a cache or directly to the target location
        downloaded_path = hf_hub_download(
            repo_id=repo_id, 
            filename=filename,
            local_dir=model_dir,
            local_dir_use_symlinks=False
        )
        
        # Rename the downloaded file to 'model.gguf' for standardization
        if downloaded_path != target_model_path:
            # Huggingface hub might save it as the original filename in local_dir
            actual_download_path = os.path.join(model_dir, filename)
            if os.path.exists(actual_download_path):
                os.rename(actual_download_path, target_model_path)
            
        print(f"✅ Download complete! Model saved to {target_model_path}")
        
        # Write metadata.json
        metadata = {
            "id": "qwen2.5-1.5b-instruct-q4_k_m",
            "display_name": "Qwen 2.5 1.5B Instruct",
            "engine": "llama.cpp",
            "format": "GGUF",
            "sha256": "unknown_calculated_at_runtime",
            "context": 32768,
            "quantization": "Q4_K_M",
            "size_mb": 1120,
            "tool_calling": True,
            "streaming": True,
            "languages": [
                "English",
                "Hindi",
                "Telugu"
            ]
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
            
        print(f"✅ Metadata written to {metadata_path}")
        print("\nCHITTI is now ready to use the local LLM!")
        
    except ImportError:
        print("❌ Error: huggingface-hub is not installed. Run: pip install huggingface-hub")
    except Exception as e:
        print(f"❌ Error downloading model: {e}")

if __name__ == "__main__":
    main()
