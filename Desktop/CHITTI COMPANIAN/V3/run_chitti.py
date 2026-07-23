import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from desktop.app.main import main

if __name__ == "__main__":
    main()
