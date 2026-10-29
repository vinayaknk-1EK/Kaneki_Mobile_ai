import speech_recognition as  sr
import platform
import subprocess
import os
import json


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

# this is the intent parser that takes in commands (hardcoded for now)
def parse_intent(user_input):
    """currently hardcoded for tsertain taska but acan be integrated with ai 
    for future repurposing"""

    if "call" in user_input:
        return "call", user_input
    elif "open calender" in user_input:
        return "calender", user_input
    elif "close" or "shutdown" in user_input:
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

        for word in ["call", "phone", "dial", "please", "make", "a", "to"]:
           raw_text = raw_text.replace(word, "")
        search_name= raw_text.strip().lower()
        subprocess.run(["termux-toast", f"Kaneki: searching {search_name}..."])

        if not search_name:
            print("kaneki: No contact name specified...")
            subprocess.run(["termux-toast", "Kaneki: No contact name specified\n "
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
        else:
            print(f" hardware: {search_name} not in contacts!")
            subprocess.run(["termux-toast", f"kaneki: {search_name} not found!"])

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
    subprocess.run(["termux-toast", "Kaneki online!!"])

    is_running = True
    while is_running:
        cmd = listen_voice()
        if cmd:
            intent, text = parse_intent(cmd)
            is_running = execute_actions(intent, text)


        