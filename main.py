import subprocess
import os
import sys
import shutil
import atexit
from password_analyzer.gui.app import run_app

def start_backend():
    print("[+] Starting Local Backend API in background...")
    
    # Force UTF-8 encoding to prevent UnicodeEncodeError on Windows
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Find the correct Python executable:
    # Priority: .venv in project dir -> .venv in HK3 dir -> python in current PATH
    project_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(project_dir, ".venv", "Scripts", "python.exe"),
        os.path.join(project_dir, "..", "..", ".venv", "Scripts", "python.exe"),
        r"D:\0. UIT\HK3\.venv\Scripts\python.exe",  # Absolute fallback for this workspace
        shutil.which("python"),  # Python currently active in terminal
        sys.executable,          # Last resort fallback
    ]
    python_exe = next((p for p in candidates if p and os.path.isfile(p)), sys.executable)
    print(f"[+] Using Python: {python_exe}")
    
    log_file = open("backend_error.log", "w", encoding="utf-8")
    process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "backend.server:app", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=log_file,
        env=env
    )
    
    def cleanup():
        process.terminate()
        log_file.close()
        print("[+] Local Backend stopped.")
        
    atexit.register(cleanup)
    print("[+] Backend loading in background. GUI will auto-ping.")


if __name__ == "__main__":
    start_backend()
    print("[+] Launching GUI...")
    run_app()
