import json
import os
import sounddevice as sd
import numpy as np
from gtts import gTTS
import playsound
import speech_recognition as sr
import tempfile
import threading
import time
from fuzzywuzzy import process  # Import fuzzywuzzy for string matching

# Suppress ALSA warnings and errors
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.environ['ALSA_NO_ERROR_SUSPEND'] = '1'

# Set specific input and output devices
input_device_index = 0  # ALC283 Analog
output_device_index = 1  # AB13X USB Audio

# Global variables for managing listening state
user_response = ""
is_listening = False  # Flag to control the listening state
response_lock = threading.Lock()
recognizer = sr.Recognizer()
source = sr.Microphone(device_index=input_device_index)

def speak_text(text):
    """Function to convert text to speech using gTTS and playsound."""
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
        tts.save(f"{tmp_file.name}.mp3")
        playsound.playsound(f"{tmp_file.name}.mp3")

def load_script(script_name):
    """Function to load the conversation script from a JSON file."""
    script_path = f'scripts/{script_name}.json'
    try:
        with open(script_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Script file {script_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the script file {script_path}.")
        return None

def get_user_response():
    """Function to capture user response using speech recognition."""
    global is_listening, source
    with source as audio_source:
        recognizer.adjust_for_ambient_noise(audio_source)  # Adjust for ambient noise
        while is_listening:  # Only listen while the flag is True
            print("Listening for user response...")
            try:
                audio = recognizer.listen(audio_source, timeout=5)  # Set a timeout
                response = recognizer.recognize_google(audio).lower().strip()  # Normalize input
                with response_lock:
                    global user_response
                    user_response = response
                print(f'User: {response}')
            except sr.UnknownValueError:
                continue  # Ignore unrecognized speech
            except sr.WaitTimeoutError:
                print("Listening timed out, waiting for user response...")
                continue  # Continue listening
            except sr.RequestError as e:
                print(f"Could not request results from the speech recognition service: {e}")
                break  # Exit if there's a request error

def check_user_response(user_input, user_responses):
    """Check user response against possible responses using fuzzy matching."""
    matched_response = process.extractOne(user_input, user_responses.keys())
    if matched_response and matched_response[1] >= 70:  # Match if confidence is 70% or more
        return matched_response[0]  # Return the matched key
    return None

def run_bot(script):
    """Function to run the bot based on the loaded script."""
    global is_listening
    if not script or "dialog" not in script:
        print("Invalid script provided. Please check the script file.")
        return

    for entry in script["dialog"]:
        # Get the line to say and the responses
        bot_message = entry["line"]
        user_responses = entry["user_responses"]

        speak_text(bot_message)  # Speak the bot's message

        # Reset user response
        global user_response
        user_response = ""
        
        # Start listening in the background
        is_listening = True
        listening_thread = threading.Thread(target=get_user_response, daemon=True)
        listening_thread.start()  # Start background listener

        # Wait for user response
        while True:
            time.sleep(1)  # Allow time for user to respond
            with response_lock:
                current_response = user_response  # Capture current response safely

            # Check for valid response
            if current_response:
                print(f"Checking user response: '{current_response}' against defined responses.")
                matched_key = check_user_response(current_response, user_responses)

                if matched_key:
                    # Retrieve the bot's response associated with the matched key
                    bot_responses = user_responses[matched_key]
                    if bot_responses:
                        bot_response = bot_responses[0]  # Use the first response as the default
                        print(f'Bot: {bot_response}')
                        speak_text(bot_response)
                    break  # Exit loop after valid response
                
                print("No predefined response found, proceeding to the next line.")
                break  # Exit if no valid response found

        # Indicate that the bot is moving on to the next response
        time.sleep(1)  # Wait for a moment before proceeding
        is_listening = False  # Stop listening after responding
        listening_thread.join()  # Wait for the listener thread to finish

def main():
    """Main function to start the bot."""
    script_name = input("Enter Script Name to Use: ")
    print(f"Loading script from: scripts/{script_name}.json")
    
    script = load_script(script_name)

    # Start the conversation
    run_bot(script)

if __name__ == "__main__":
    main()
