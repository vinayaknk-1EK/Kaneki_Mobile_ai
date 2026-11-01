import platform
import subprocess
import os
import json
import shutil
import sys
import time
import socket

_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_only(host, port, family=0, type=0, proto=0, flags=0 ):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _ipv4_only

# this block installs dependencies needed from the get go
IS_ANDROID =""
def install_dependencies():
    """checks and installs dependencies needed"""
    IS_ANDROID = "com.termux" in os.environ.get("PREFIX", "") or (platform.system() == "linux" and os.path.exists("/data/data/com.termux"))

    has_termux_api = shutil.which("termux-toast") is not None

    print("==========================================")
    print("            Kaneki: starting up           ")
    print("==========================================")

    if IS_ANDROID:
        print("android env detected(currently running on Termux), " \
        "\n checking system packages...")
        try:
            # check if portaudio or clang is missing by running a quick check, or just safe-install them via pkg
            subprocess.run(["dpkg", "-s", "portaudio", "clang", "ffmpeg", "termux-api", "flac"], 
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("[Setup]: Missing essential system binaries. Installing via pkg (portaudio, clang, ffmpeg, termux-api)...")
            subprocess.run(["pkg", "update", "-y"])
            subprocess.run(["pkg", "install", "portaudio", "clang", "ffmpeg", "termux-api", "flac", "-y"])


    required_packages = {"SpeechRecognition": "SpeechRecognition", 
                         "pyaudio": "pyaudio", 
                         "termux-api": "termux-api"}
    
    for module_name, pip_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            print(f"[Setup]: Missing dependency {pip_name}, installing automatically...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

# this checks if all the dependencies are installed
install_dependencies()

import speech_recognition as  sr
# initialize recognizer
recognizer = sr.Recognizer()
recognizer.operation_timeout = 10
#  giving the wake word
WAKE_WORD = ["Kaneki",  "kaneki",  "kaneeki"] # adding variables to make sure google catches all the possible spells

def notify(Message):
    if IS_ANDROID:
        try: 
            subprocess.run(["termux-toast", "kaneki Online..."])
        except FileNotFoundError:
            pass

# this was the place holder for that actions showcased terminal outputs.
#"""def speak_mock(text):
 #   "Simulates the assistance responce through text in terminal"
  #  print(f"\n[Status...kaneki(test): (listening)...]")"""
# this is not utilized anymore!!!

# this is the listening string that takes voice commandsa and turns them into texts
# for the next step of executing the commands through android api keys 
# (for now it is mocked through text outputs)  
source =""

def listen_for_wake_word():
    """listens quitely until the wake word is heard,
    Returns none if no wake word, "" ifthe wake word is used """
    try:
        with sr.Microphone()as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
        text= recognizer.recognize_google(audio).lower()
    except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
        return None
    except Exception:
        time.sleep(3)
        return None

    for w in WAKE_WORD:
        if w in text:
            return text.split(w, 1)[1].strip()
    return None


def listen_voice():
    """catches user audio though microphone and converts it to text"""
    with sr.Microphone() as source:
        print("\n listening through microphone... speak now!!")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            # listen for speech input
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            print(f"\n command was; {text}")
            return text.lower()
        
        except sr.WaitTimeoutError:
            print("\n[Status...kaneki: (timeout, no input detected)...]")
            subprocess.run(["termux-toast", "Kaneki: timeout, no input detected"])
            return None
        
        except sr.UnknownValueError:
            print("\n [Status...kaneki: (could not understand audio)...]")
            subprocess.run(["termux-toast", "Kaneki: could not understand audio"])
            return None
        
        except sr.RequestError:
            print("\n [Status...kaneki: (could not request results from Google Speech Recognition service)...]")
            subprocess.run(["termux-toast", "Kaneki: could not request results from Google Speech Recognition service)..."])
            return None
        except Exception as e:
            # Tihs catches OS/PortAudio errors when the mic is locked by phone call
            print(f"[hardware warning]: microphone busy, ({e}) Retrying in a moment...")
            return None

        

# till here ends the input string and the error handlers(for now!)

# this is the intent parser that takes in commands (hardcoded for now)
def parse_intent(user_input):
    """currently hardcoded for certain tasks but can be integrated with ai 
    for future repurposing"""

    if any(word in user_input for word in ["call", "phone", "dial"]):
        return "call", user_input 
    elif any(word in user_input for word in ["open calendar", "calendar", "event"]):
        return "calendar", user_input
    elif "close" in user_input or "shutdown" in user_input:
        return "close", user_input

# from here begins the execution part that takes the input from abovce and 
# execute the commands through android api keys (for now it is mocked through text outputs) 


def execute_actions(action_type, raw_text):
    """Mocks the android environment through text outputs that
    later can be replaced with android api keys"""
       # handels the call command and executes it through android api keys (for now it is mocked through text outputs)
       # notification popups from toast  
    if action_type == "call":

        try: 
            result = subprocess.run(["termux-contact-list"], capture_output=True,  text=True, check=True)
            contacts = json.loads(result.stdout)
        except Exception as e:
            subprocess.run(["termux-toast", "Kaneki: contact fetch failed!..."])
            return True
        # extracts the contact name from the commabd spoken
        # uses simple split logic for the words in the [] bracket.

        filler = {"call", "phone", "dial", "please", "make", "a", "to",}
        search_name = " ".join(w for w in raw_text.split() if w not in filler)
        subprocess.run(["termux-toast", f"Kaneki: searching {search_name}..."])

        if not search_name:
            print("kaneki: No contact name specified...")
            subprocess.run(["termux-toast", "Kaneki: No co  ntact name specified\n "
            "who do you want to call?..."])
            return True


        target_number= None
        matched_number = None
        for contact in contacts:
            name = contact.get("name", "").lower()
            if search_name in name:
                target_number = contact.get("number")
                matched_number = contact.get("number")
                break

        if target_number:
            subprocess.run(["termux-toast", f"Kaneki: calling {matched_number}..."])
            print(f"Terminal: found {matched_number}, calling {matched_number}...")
            subprocess.run(["termux-telephony-call", target_number])

#Dynamic waiting perriod for the microphone to reactivate
            while True:
                time.sleep(5)
                try:
                    with sr.Microphone() as source:                 # if this while block crashes it means the call ended
                        break                                            # if it does not it retries after every 5 seconds to check 
                except Exception:
                    pass # this works if the microphone is still in use                                                    # the microphone is free
                        
        else:
            print(f" hardware: {search_name} not in contacts!")
            subprocess.run(["termux-toast", f"kaneki: {search_name} not found!"])


    elif action_type == "open_calendar":
        subprocess.run(["termux-toast", "Kaneki: Opening Calendar..."])
        print("[Hardware]: Opening Calendar...")
        """print(f"\n[Status...kaneki: (opening calendar)...]")"""


    elif action_type == "close":
        subprocess.run(["termux-toast", "Kaneki: closing down..."])
        print("[Hardware]: Closing Application...")
        """print(f"\n[Status...kaneki: (closing application)...]")"""
        return False


    else:
        subprocess.run(["termux-toast", "Kaneki: command not recognized..."])
        print("\n [kaneki]: command not recognized or not allowed yet...")

    return True

if __name__ == "__main__":
    print ("==========================================")
    print ("     Kaneki: Voice Assistant (live)       ")
    print ("==========================================")
    subprocess.run(["termux-toast", "Kaneki online!!"])

    is_running = True
    while is_running:
        cmd = listen_for_wake_word()
        if cmd is None:
            continue
        if cmd == "":
            subprocess.run(["termux-toast", "Kaneki: yes?.."])
            cmd = listen_voice()
        if cmd:
            intent, text = parse_intent(cmd)
            is_running = execute_actions(intent, text)


        