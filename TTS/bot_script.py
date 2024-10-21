import json
import os
import sounddevice as sd
import numpy as np
from TTS.utils import setup_environment
from TTS import TTS
import playsound
import speech_recognition as sr
import tempfile
import threading
import time
from fuzzywuzzy import process

# Suppress ALSA warnings and errors
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.environ['ALSA_NO_ERROR_SUSPEND'] = '1'

# Set specific input and output devices
input_device_index = 0  # ALC283 Analog
output_device_index = 1  # AB13X USB Audio

# Global variables
user_response = ""
is_listening = False
response_lock = threading.Lock()
recognizer = sr.Recognizer()
source = sr.Microphone(device_index=input_device_index)

# Predefined interruptions or conditions
INTERRUPTION_PHRASES = ["don't call again", "stop calling me", "not interested", "remove my number"]
STOP_PHRASE = "Sorry for bothering you, I'm going to remove your number from the calling list and make sure you will never get a call from us in the future. Have a good day, bye!"

# Set up TTS
setup_environment()
tts_model_name = "your_model_name"  # Replace with your actual model name
tts = TTS(model_name=tts_model_name)

def speak_text(text):
    """Convert text to speech using the TTS library and play it."""
    output_file = "output.wav"
    tts.tts_to_file(text=text, file_path=output_file)  # Generate speech to a file
    playsound.playsound(output_file)  # Play the generated audio file

def load_script(script_name):
    """Load the conversation script from a JSON file."""
    script_path = f'scripts/{script_name}.json'
    try:
        with open(script_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error loading script: {script_path}")
        return None

def get_user_response():
    """Capture user response using speech recognition."""
    global is_listening, source
    with source as audio_source:
        recognizer.adjust_for_ambient_noise(audio_source)
        while is_listening:
            try:
                print("Listening for user response...")
                audio = recognizer.listen(audio_source, timeout=5)
                response = recognizer.recognize_google(audio).lower().strip()
                with response_lock:
                    global user_response
                    user_response = response
                print(f'User: {response}')
            except sr.UnknownValueError:
                continue
            except sr.WaitTimeoutError:
                print("Listening timed out, waiting for user response...")
                continue
            except sr.RequestError as e:
                print(f"Could not request results: {e}")
                break

def check_user_response(user_input, user_responses):
    """Check user response against possible responses using fuzzy matching."""
    if any(phrase in user_input for phrase in INTERRUPTION_PHRASES):
        return "interruption"  # Trigger interruption action

    matched_response = process.extractOne(user_input, user_responses.keys())
    if matched_response and matched_response[1] >= 70:
        return matched_response[0]
    return None

def handle_dynamic_input(prompt_type):
    """Handle dynamic inputs like names, age, or date of birth."""
    global is_listening
    is_listening = True
    listening_thread = threading.Thread(target=get_user_response, daemon=True)
    listening_thread.start()
    listening_thread.join()  # Wait for the response
    is_listening = False

    # Capture user input from the global user_response
    global user_response
    response = user_response.lower().strip()

    if prompt_type == "age":
        try:
            age = int(response)
            if 65 <= age <= 85:
                return "valid_age"
            else:
                return "invalid_age"
        except ValueError:
            return None

    return response  # For other dynamic inputs like names

def run_bot(script):
    """Run the bot based on the loaded script."""
    global is_listening
    if not script or "dialog" not in script:
        print("Invalid script. Check the file.")
        return

    for entry in script["dialog"]:
        bot_message = entry["line"]
        user_responses = entry["user_responses"]

        speak_text(bot_message)
        global user_response
        user_response = ""
        
        is_listening = True
        listening_thread = threading.Thread(target=get_user_response, daemon=True)
        listening_thread.start()

        while is_listening:
            time.sleep(1)
            with response_lock:
                current_response = user_response

            if current_response:
                matched_key = check_user_response(current_response, user_responses)

                if matched_key == "interruption":
                    print(f'Bot: {STOP_PHRASE}')
                    speak_text(STOP_PHRASE)
                    is_listening = False  # Stop listening after interruption
                    listening_thread.join()  # Wait for the listener thread to finish
                    return  # Exit the bot session

                if matched_key:
                    bot_response = user_responses[matched_key][0]
                    print(f'Bot: {bot_response}')
                    speak_text(bot_response)

                    if bot_response.lower().startswith("sorry our insurance"):
                        is_listening = False  # Stop listening when specific phrase is matched
                        listening_thread.join()  # Wait for the listener thread to finish
                        return  # Terminate the bot session

                    break

                print("No predefined response, moving on.")
                break

        is_listening = False
        listening_thread.join()  # Wait for the listener thread to finish

    # Automatically hang up at the end of the script
    print("Script completed. Hanging up.")
    is_listening = False

def main():
    script_name = input("Enter Script Name to Use: ")
    print(f"Loading script from: scripts/{script_name}.json")
    script = load_script(script_name)
    run_bot(script)

if __name__ == "__main__":
    main()
