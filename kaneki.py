import speech_recognition as  sr
import platform
import subprocess
import os

# initialize recognizer
recognizer = sr.Recognizer()

# this was the place holder for that actions showcased terminal outputs.
"""def speak_mock(text):
    "Simulates the assistance responce through text in terminal"
    print(f"\n[Status...kaneki(test): (listening)...]")"""
# this is not utilized anymore

# this is the listening string that takes voice commandsa and turns them into texts
# for the next step of executing the commands through android api keys 
# (for now it is mocked through text outputs)  

def listen_voice():
    """catches user audio though microphone and converts it to text"""
    with sr.Microphone() as source:
        print("\n listening through microphone... speak now!!")
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        try:
            # listen for speech input
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            print(f"\n command was; {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            print("\n[Status...kaneki(test): (timeout, no input detected)...]")
            return None
        except sr.UnknownValueError:
            print("\n [Status...kaneki(test): (could not understand audio)...]")
            return None
        except sr.RequestError:
            print("\n [Status...kaneki(test): (could not request results from Google Speech Recognition service)...]")
            return None

# till here ends the input string and the error handlers(for now!)




# from here begins the execution part that takes the input from abovce and 
# execute the commands through android api keys (for now it is mocked through text outputs) 


def execute_actions(action_type, raw_text):
    """Mocks the android environment through text outputs that
    later can be replaced with android api keys"""
    
    if action_type == "call":
       # handels the call command and executes it through android api keys (for now it is mocked through text outputs)
       # notification popups from toast
       subprocess.run(["termux-toast", "Kaneki: Calling..."])
       # need to profide dynamic parser to select number from contact through 
       # name input
       target_number= "1234567890"
       print(f"[Hardware]: calling{target_number}...")
       subprocess.run(["termux-telephony-call", target_number])
       """ print(f"\n[Status...kaneki: (calling [contact name])...]")"""

    elif action_type == "open_calender":
        subprocess.run(["termux-toast", "Kaneki: Opening Calender..."])
        print("[Hardware]: Opening Calender...")
        """print(f"\n[Status...kaneki: (opening calender)...]")"""

    elif action_type == "close":
        subprocess.run(["termux-toast", "Kaneki: Closing Application..."])
        print("[Hardware]: Closing Application...")
        """print(f"\n[Status...kaneki: (closing application)...]")"""
        return False

    else:
        subprocess.run(["termux-toast", "Kaneki: command not recognized..."])
        print("\n [kaneki]: command not recognized or not allowed yet...")

    return True

if __name__ == "__main__":
    print ("==========================================")
    print ("  Kaneki: Voice Assistant (Test Mode)     ")
    print ("==========================================")

    while True:
        cmd = listen_voice()
        if cmd:
            execute_actions(cmd, cmd)


        