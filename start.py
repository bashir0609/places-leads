"""Start both backend and frontend with one command"""

import os
import signal
import subprocess
import sys
import time
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
processes = []


def run_backend():
    backend_dir = os.path.join(ROOT, "backend")
    print("🔧 Starting Flask backend on http://localhost:5001 ...")
    return subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=backend_dir,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        if sys.platform == "win32"
        else 0,
    )


def run_frontend():
    frontend_dir = os.path.join(ROOT, "frontend")
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("📦 Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, shell=True, check=False)
    print("🎨 Starting React frontend on http://localhost:3000 ...")
    env = os.environ.copy()
    env["BROWSER"] = "none"
    env["NODE_NO_WARNINGS"] = "1"
    return subprocess.Popen(
        ["npx", "react-scripts", "start"],
        cwd=frontend_dir,
        env=env,
        shell=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        if sys.platform == "win32"
        else 0,
    )


def cleanup():
    print("\n🛑 Shutting down...")
    for p in processes:
        if p.poll() is not None:
            continue  # Already exited
        try:
            if sys.platform == "win32":
                p.send_signal(signal.CTRL_BREAK_EVENT)
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait()
            else:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait()
        except Exception:
            try:
                p.kill()
                p.wait()
            except Exception:
                pass
    print("Done!")


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Google Places Scraper")
    print("=" * 50)

    backend = run_backend()
    processes.append(backend)
    time.sleep(2)

    frontend = run_frontend()
    processes.append(frontend)
    time.sleep(3)

    print("\n✨ Ready! http://localhost:3000")
    print("   Press Ctrl+C to stop.\n")
    webbrowser.open("http://localhost:3000")

    try:
        while any(p.poll() is None for p in processes):
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
        sys.exit(0)
