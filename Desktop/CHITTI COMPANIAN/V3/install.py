import os
import sys
import subprocess
import venv

def main():
    print("Setting up CHITTI COMPANIAN V3 environment...")
    
    venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment at {venv_dir}...")
        venv.create(venv_dir, with_pip=True)
    else:
        print(f"Virtual environment already exists at {venv_dir}.")
        
    # Determine the pip executable path
    if sys.platform == "win32":
        pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        pip_exe = os.path.join(venv_dir, "bin", "pip")
        
    if not os.path.exists(pip_exe):
        print(f"Error: Could not find pip at {pip_exe}")
        sys.exit(1)
        
    # Upgrade pip
    print("Upgrading pip...")
    subprocess.check_call([pip_exe, "install", "--upgrade", "pip"])
    
    # Install requirements
    req_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    if os.path.exists(req_file):
        print(f"Installing dependencies from {req_file}...")
        subprocess.check_call([pip_exe, "install", "-r", req_file])
    else:
        print(f"Error: {req_file} not found.")
        sys.exit(1)
        
    print("\nEnvironment setup complete!")
    if sys.platform == "win32":
        print("To activate the virtual environment, run:")
        print(f"  {os.path.join('venv', 'Scripts', 'activate')}")
    else:
        print("To activate the virtual environment, run:")
        print(f"  source {os.path.join('venv', 'bin', 'activate')}")

if __name__ == "__main__":
    main()
