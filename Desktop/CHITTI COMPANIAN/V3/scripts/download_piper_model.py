import os
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_file(url: str, dest_path: str):
    logger.info(f"Downloading {url} to {dest_path}...")
    urllib.request.urlretrieve(url, dest_path)
    logger.info(f"Successfully downloaded to {dest_path}")

def main():
    model_dir = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop\models\piper"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    # We use en_US-lessac-medium as recommended
    base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/"
    model_name = "en_US-lessac-medium.onnx"
    config_name = "en_US-lessac-medium.onnx.json"

    model_path = os.path.join(model_dir, model_name)
    config_path = os.path.join(model_dir, config_name)

    if not os.path.exists(model_path):
        download_file(base_url + model_name, model_path)
    else:
        logger.info(f"Model already exists at {model_path}")

    if not os.path.exists(config_path):
        download_file(base_url + config_name, config_path)
    else:
        logger.info(f"Config already exists at {config_path}")

    logger.info("Piper model setup complete!")

if __name__ == "__main__":
    main()
