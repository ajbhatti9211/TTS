import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

# Function to load existing scripts from separate files
def load_scripts():
    scripts = {}
    if not os.path.exists('scripts'):
        os.makedirs('scripts')
    for filename in os.listdir('scripts'):
        if filename.endswith('.json'):
            script_name = filename.replace('.json', '')
            with open(f'scripts/{filename}', 'r') as f:
                try:
                    scripts[script_name] = json.load(f).get(script_name, {})
                except json.JSONDecodeError:
                    print(f"Error reading script file: {filename}")
    return scripts

# Function to save a script to a separate file
def save_script(script_name, script_data):
    if not os.path.exists('scripts'):
        os.makedirs('scripts')
    filepath = f'scripts/{script_name}.json'
    with open(filepath, 'w') as f:
        json.dump({script_name: script_data}, f, indent=4)

# Initialize script data
all_scripts = load_scripts()

# Function to add new script
def add_script():
    script_name = simpledialog.askstring("Input", "Enter Script Name:")
    if script_name and script_name not in all_scripts:
        all_scripts[script_name] = {}
        messagebox.showinfo("Success", f"Script '{script_name}' added successfully!")
    elif script_name in all_scripts:
        messagebox.showerror("Error", "Script with this name already exists.")
    else:
        messagebox.showerror("Error", "Invalid Script Name.")

# Function to add new line to a specific script
def add_script_line():
    selected_script = simpledialog.askstring("Input", "Enter Script Name to Add Line:")
    if selected_script in all_scripts:
        question = simpledialog.askstring("Input", "Enter Script Question/Line:")
        if question:
            all_scripts[selected_script][question] = {
                "user_responses": [],
                "bot_responses": []
            }
            add_responses(selected_script, question)
        else:
            messagebox.showerror("Error", "Invalid Question/Line.")
    else:
        messagebox.showerror("Error", "Script does not exist.")

# Function to add user responses and bot responses
def add_responses(script, question):
    while True:
        user_response = simpledialog.askstring("Input", f"Enter User Response for '{question}' (Leave blank to stop):")
        if not user_response:
            break
        
        bot_response = simpledialog.askstring("Input", f"Enter Bot Response for '{user_response}':")
        if bot_response:
            all_scripts[script][question]["user_responses"].append(user_response)
            all_scripts[script][question]["bot_responses"].append(bot_response)
        else:
            messagebox.showerror("Error", "Invalid Bot Response.")

    messagebox.showinfo("Success", f"Responses for '{question}' added successfully!")
    save_script(script, all_scripts[script])

# Display Current Script Data
def display_all_scripts():
    script_text = ""
    for script_name, script_content in all_scripts.items():
        script_text += f"Script: {script_name}\n"
        for question, data in script_content.items():
            script_text += f"  Question: {question}\n"
            script_text += f"    User Responses: {', '.join(data['user_responses'])}\n"
            script_text += f"    Bot Responses: {', '.join(data['bot_responses'])}\n"
        script_text += "\n"
    
    if script_text:
        messagebox.showinfo("All Scripts", script_text)
    else:
        messagebox.showinfo("All Scripts", "No scripts added yet.")

# Create the main window
root = tk.Tk()
root.title("Call Center Bot Script Manager")

# Buttons for script management
add_script_button = tk.Button(root, text="Add New Script", command=add_script)
add_script_button.pack(pady=5)

add_script_line_button = tk.Button(root, text="Add New Script Line", command=add_script_line)
add_script_line_button.pack(pady=5)

show_all_scripts_button = tk.Button(root, text="Show All Scripts", command=display_all_scripts)
show_all_scripts_button.pack(pady=5)

# Start the main loop
root.mainloop()
