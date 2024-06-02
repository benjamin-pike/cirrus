import os
import sys
import subprocess

REQUIRED_PYTHON = "3.10"

def validate_python_version():
    if sys.version_info < (3, 10):
        sys.exit(f"Python {REQUIRED_PYTHON} is required. You are using {sys.version}")

def install_packages():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def install_pre_commit_hook():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pre-commit"])
    subprocess.check_call(["pre-commit", "install"])

def add_src_to_sys_path():
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

def main():
    validate_python_version()
    install_packages()
    install_pre_commit_hook()
    add_src_to_sys_path()
    print("Setup completed successfully.")

if __name__ == "__main__":
    main()
