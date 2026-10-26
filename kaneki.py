import speech_recognition as  sr
import platform
import subprocess

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


def execute_actions(command):
    """Mocks the android environment through text outputs that
    later can be replaced with android api keys"""
    if "call" in command:
       # speak_mock ("calling [contact name]...")
        print(f"\n[Status...kaneki(test): (calling [contact name])...]")
    elif "open calender" in command or "add event" in command:
        # speak_mock ("opening calender...")
        print(f"\n[Status...kaneki(test): (opening calender)...]")
    elif "close" in command:
        # speak_mock ("closing application...")
        print(f"\n[Status...kaneki(test): (closing application)...]")
        exit()
    else:
        print("\n [kaneki]: command not recognized or not allowed yet...")

if __name__ == "__main__":
    print ("==========================================")
    print ("  Kaneki: Voice Assistant (Test Mode)     ")
    print ("==========================================")

    while True:
        cmd = listen_voice()
        if cmd:
            execute_actions(cmd)


        