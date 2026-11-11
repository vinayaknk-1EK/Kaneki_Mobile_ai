import subprocess
import os
import json
import shutil
import sys
import time
import socket
 
# force IPv4: IPv6 is dropped on this network and makes Google requests hang
_orig_getaddrinfo = socket.getaddrinfo
 
 
def _ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
 
 
socket.getaddrinfo = _ipv4_only
 
IS_ANDROID = "com.termux" in os.environ.get("PREFIX", "")
 
 
# ---------------------------------------------------------------
# helpers: nothing below is allowed to block forever
# ---------------------------------------------------------------
def run_termux(cmd, timeout=10, **kwargs):
    """Runs a command with a timeout. termux-* commands hang forever if the
    Termux:API app isn't responding, which looks exactly like a frozen script."""
    try:
        return subprocess.run(cmd, timeout=timeout, **kwargs)
    except subprocess.TimeoutExpired:
        print(f"[Warning]: '{cmd[0]}' timed out after {timeout}s "
              f"(is the Termux:API app installed, allowed to run in background, and permitted?)")
    except FileNotFoundError:
        print(f"[Warning]: command '{cmd[0]}' not found")
    return None
 
 
def notify(message):
    """prints a status line and shows a toast"""
    print(f"[Kaneki]: {message}")
    if IS_ANDROID:
        run_termux(["termux-toast", message], timeout=5)
 
 
# ---------------------------------------------------------------
# dependency check: only does work when something is actually missing
# ---------------------------------------------------------------
def install_dependencies():
    print("==========================================")
    print("            Kaneki: starting up           ")
    print("==========================================")
 
    required = {"speech_recognition": "SpeechRecognition", "pyaudio": "pyaudio"}
    missing = []
    for module_name, pip_name in required.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_name)
 
    if IS_ANDROID and shutil.which("termux-toast") is None:
        print("[Setup]: termux-toast not found. Run: pkg install termux-api")
 
    if not missing:
        return
 
    print(f"[Setup]: missing {missing}, installing...")
    if IS_ANDROID:
        subprocess.run(["pkg", "install", "-y", "portaudio", "clang", "ffmpeg", "termux-api", "flac"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
 
 
install_dependencies()
 
import speech_recognition as sr
 
recognizer = sr.Recognizer()
recognizer.operation_timeout = 10
 
# variants because Google often mishears the name
WAKE_WORD = ["kaneki", "kanaki", "kaneeki"]
 
 
# ---------------------------------------------------------------
# 1. MIC ENGINE
# ---------------------------------------------------------------
def listen_for_wake_word():
    """Listens quietly until the wake word is heard.
    Returns None if no wake word, "" if only the wake word was said,
    or the command spoken after the wake word."""
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
        text = recognizer.recognize_google(audio).lower()
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return None
    except sr.RequestError as e:
        print(f"[network]: speech service unreachable ({e})")
        return None
    except Exception as e:
        print(f"[mic error]: {e}")     # shown on purpose, so a dead mic is never silent
        time.sleep(3)
        return None
 
    print(f"[heard]: {text}")
    for w in WAKE_WORD:
        if w in text:
            return text.split(w, 1)[1].strip()
    return None
 
 
def listen_voice():
    """catches user audio through microphone and converts it to text"""
    try:
        with sr.Microphone() as source:
            print("\n listening through microphone... speak now!!")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
        text = recognizer.recognize_google(audio)
        print(f"\n command was: {text}")
        return text.lower()
 
    except sr.WaitTimeoutError:
        notify("Timeout, no input detected")
        return None
    except sr.UnknownValueError:
        notify("Could not understand audio")
        return None
    except sr.RequestError:
        notify("Could not reach Google Speech service")
        return None
    except Exception as e:
        print(f"[hardware warning]: microphone busy, ({e}) Retrying in a moment...")
        time.sleep(3)
        return None
 
 
# ---------------------------------------------------------------
# 2. INTENT PARSER
# ---------------------------------------------------------------
def parse_intent(user_input):
    if any(word in user_input for word in ["call", "phone", "dial"]):
        return "call", user_input
    elif any(word in user_input for word in ["calendar", "event", "schedule"]):
        return "open_calendar", user_input
    elif any(word in user_input for word in ["close", "shutdown", "exit", "stop"]):
        return "close", user_input
    return "unknown", user_input
 
 
# ---------------------------------------------------------------
# 3. ACTION EXECUTOR
# ---------------------------------------------------------------
def execute_actions(action_type, raw_text):
    """Runs the command through Termux-API. Returns False only to quit."""
 
    if action_type == "call":
        result = run_termux(["termux-contact-list"], timeout=15, capture_output=True, text=True)
        if result is None or result.returncode != 0:
            notify("Contact fetch failed!")
            return True
        try:
            contacts = json.loads(result.stdout)
        except json.JSONDecodeError:
            notify("Contact fetch failed!")
            return True
 
        # keep whole words only, so names like "aarav" or "tom" stay intact
        filler = {"call", "phone", "dial", "please", "make", "a", "to"}
        search_name = " ".join(w for w in raw_text.split() if w not in filler)
 
        if not search_name:
            notify("No contact name specified. Who do you want to call?")
            return True
 
        notify(f"Searching {search_name}...")
 
        target_number = None
        matched_name = None
        for contact in contacts:
            name = contact.get("name", "").lower()
            if search_name in name:
                target_number = contact.get("number")
                matched_name = contact.get("name")
                break
 
        if target_number:
            notify(f"Calling {matched_name}...")
            run_termux(["termux-telephony-call", target_number], timeout=15)
 
            # wait until the call ends: the mic is locked while the call is active
            print("[Status]: Call in progress. Waiting for microphone release...")
            while True:
                time.sleep(5)
                try:
                    with sr.Microphone():
                        break          # mic opened fine -> call ended
                except Exception:
                    pass               # mic still busy -> keep waiting
            notify("Call ended. Back online.")
        else:
            notify(f"{search_name} not found in contacts!")
 
    elif action_type == "open_calendar":
        notify("Opening Calendar...")
        run_termux([
            "am", "start",
            "-a", "android.intent.action.INSERT",
            "-d", "content://com.android.calendar/events",
        ], timeout=10)
 
    elif action_type == "close":
        notify("Closing down...")
        return False
 
    else:
        notify("Command not recognized...")
 
    return True
 
 
# ---------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------
if __name__ == "__main__":
    print("==========================================")
    print("     Kaneki: Voice Assistant (live)       ")
    print("==========================================")
    notify("Kaneki online!!")
    print("[Kaneki]: listening for the wake word 'Kaneki'... (Ctrl+C to stop)")
 
    is_running = True
    try:
        while is_running:
            cmd = listen_for_wake_word()
            if cmd is None:
                continue                      # wake word not heard, keep waiting
            if cmd == "":                     # only said "Kaneki"
                notify("Yes?")
                cmd = listen_voice()
            if cmd:
                intent, text = parse_intent(cmd)
                is_running = execute_actions(intent, text)
    except KeyboardInterrupt:
        notify("Shutting down...")
 

