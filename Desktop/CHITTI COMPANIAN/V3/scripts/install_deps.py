import subprocess
import sys

def main():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "llama-cpp-python", "huggingface-hub"])
    print("Dependencies installed successfully.")

if __name__ == "__main__":
    main()
