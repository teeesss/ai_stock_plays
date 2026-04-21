import subprocess
import sys
import importlib.util
import os

def ensure_dependencies():
    """
    V23.59: Auto-Dependency Guardian (Cross-Platform)
    Checks requirements and asks to install if missing.
    """
    # Map of module name to pip package name
    deps = {
        "bs4": "beautifulsoup4",
        "feedparser": "feedparser",
        "playwright": "playwright",
        "dotenv": "python-dotenv",
        "vaderSentiment": "vaderSentiment",
        "sumy": "sumy",
        "sklearn": "scikit-learn",
        "nltk": "nltk",
        "pandas": "pandas",
        "requests": "requests",
        "curl_cffi": "curl-cffi",
        "deep_translator": "deep-translator"
    }
    
    missing = []
    for module, package in deps.items():
        try:
            if importlib.util.find_spec(module) is None:
                missing.append(package)
        except Exception:
            missing.append(package)
            
    if missing:
        print(f"\n[!] MISSING DEPENDENCIES: {', '.join(missing)}")
        
        # Check if we are in an interactive terminal
        # Note: In some environments like certain IDE consoles, isatty() might be False even if interactive
        # But for CLI scripts, this is the standard.
        is_interactive = sys.stdin.isatty()
        
        if is_interactive:
            try:
                choice = input(f"[?] Would you like to auto-install these {len(missing)} packages now? (y/n): ").lower()
            except EOFError:
                choice = 'n'
                
            if choice == 'y':
                print(f"[*] Installing {len(missing)} packages via {sys.executable}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
                    print("[+] Python packages installed.")
                    
                    # Special Case: Playwright browsers
                    if "playwright" in missing or importlib.util.find_spec("playwright"):
                        print("[*] Installing Playwright Chromium...")
                        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
                    
                    print("[+] All dependencies resolved. Auto-restarting engine...\n")
                    # V23.60: Auto-restart the process to pick up new packages
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                except Exception as e:
                    print(f"[-] Installation failed: {e}")
                    sys.exit(1)
            else:
                print("[!] Please install dependencies manually: pip install " + " ".join(missing))
                sys.exit(1)
        else:
            # Non-interactive: just fail with instructions to avoid hanging automation
            print(f"[!] FATAL: Missing dependencies in non-interactive shell.")
            print(f"[!] Run this command to fix: {sys.executable} -m pip install {' '.join(missing)}")
            sys.exit(1)

if __name__ == "__main__":
    ensure_dependencies()
