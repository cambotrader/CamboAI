import subprocess, os, time, logging
from datetime import datetime

logging.basicConfig(filename="supervisor_agent.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def execute_powershell(path):
    try: subprocess.run(["powershell.exe", "-File", path], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e: logging.error(f"? PowerShell failed: {e.stderr}")

def check_log(path):
    if not os.path.exists(path): return "? Missing"
    age = time.time() - os.path.getmtime(path)
    return "?? Fresh" if age < 600 else "?? Fading" if age < 3600 else "?? Stale"

def dashboard():
    path = "C:\\CamboAgent\\Logs\\status_monitor_log.txt"
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("=== Cambo Reflex Dashboard ===")
        print(f"Log: {check_log(path)}")
        print("Ctrl+C to exit.")
        time.sleep(10)

execute_powershell("C:\\CamboAgent\\Scripts\\status_monitor.ps1")
dashboard()
