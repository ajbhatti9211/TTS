import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ttkthemes import ThemedTk  # For enhanced UI themes
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
                    scripts[script_name] = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error reading script file: {filename}")
    return scripts

# Function to save a script to a separate file
def save_script(script_name, script_data):
    if not os.path.exists('scripts'):
        os.makedirs('scripts')
    filepath = f'scripts/{script_name}.json'
    with open(filepath, 'w') as f:
        json.dump(script_data, f, indent=4)

# Initialize script data
all_scripts = load_scripts()

# Function to add new script
def add_script():
    script_name = simpledialog.askstring("Input", "Enter Script Name:")
    if script_name and script_name not in all_scripts:
        full_script = simpledialog.askstring("Input", "Enter Full Script (Each line on a new line):")
        if full_script:
            script_lines = full_script.split("\n")
            all_scripts[script_name] = {
                "dialog": []  # Initialize with a list to hold dialog entries
            }
            for line in script_lines:
                all_scripts[script_name]["dialog"].append({
                    "line": line,
                    "user_responses": {},  # Ensure it's a dictionary
                })
            save_script(script_name, all_scripts[script_name])
            messagebox.showinfo("Success", f"Script '{script_name}' added successfully!")
        else:
            messagebox.showerror("Error", "Invalid Script Content.")
    elif script_name in all_scripts:
        messagebox.showerror("Error", "Script with this name already exists.")
    else:
        messagebox.showerror("Error", "Invalid Script Name.")

# Function to train lines sequentially
def train_lines(script_name, script_lines):
    load_question(0, script_name, script_lines)

# Function to load the current question
def load_question(index, script_name, script_lines):
    if index < len(script_lines):
        line_data = script_lines[index]
        display_line_and_train(script_name, line_data, index, len(script_lines), script_lines)
    else:
        save_script(script_name, all_scripts[script_name])
        messagebox.showinfo("Training Complete", "The entire script has been trained!")

# Function to display line and start training
def display_line_and_train(script_name, line_data, index, total_lines, script_lines):
    # Clear the window before loading new content
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Set the title for the window
    root.title(f"Training Line: {line_data['line']}")

    # Style Configuration
    s = ttk.Style()
    s.configure('TButton', font=('Helvetica', 10), relief='flat', padding=6, background='#007BFF', foreground='white')
    s.map('TButton', background=[('active', '#0056b3')], relief=[('pressed', 'flat')])

    # Display Line Content
    tk.Label(main_frame, text=f"{line_data['line']}", font=("Arial", 14, "bold")).pack(pady=10)

    # Probable Inputs Section
    input_label = tk.Label(main_frame, text="Enter Probable User Inputs (comma separated):", font=("Arial", 12))
    input_label.pack(pady=5)
    
    input_entry = ttk.Entry(main_frame, width=50)
    input_entry.pack(pady=5)

    # Function to handle adding probable input
    def add_probable_input():
        probable_input = input_entry.get().strip()
        if probable_input:
            inputs = [inp.strip().lower() for inp in probable_input.split(',')]
            input_entry.delete(0, tk.END)

            # Grouping responses under comma-separated keys
            for inp in inputs:
                if inp not in line_data['user_responses']:
                    line_data['user_responses'][inp] = []
            
            ask_for_bot_response(script_name, line_data, inputs, index, script_lines)
        else:
            messagebox.showerror("Error", "Probable Input cannot be empty.")

    # Save and Next Action
    def save_and_next():
        # Save the current responses and load next question
        save_script(script_name, all_scripts[script_name])  # Update JSON file
        next_index = index + 1
        load_question(next_index, script_name, script_lines)

    # Function to add bot response for grouped inputs
    def ask_for_bot_response(script_name, line_data, probable_inputs, index, script_lines):
        response_window = tk.Toplevel(root)
        response_window.title(f"Add Response for Inputs: {', '.join(probable_inputs)}")
        response_window.geometry("500x200")

        tk.Label(response_window, text=f"Add Response for: {', '.join(probable_inputs)}", font=("Arial", 12)).pack(pady=5)
        response_entry = ttk.Entry(response_window, width=50)
        response_entry.pack(pady=5)

        def add_response():
            response = response_entry.get().strip()
            if response:
                for inp in probable_inputs:
                    if inp in line_data['user_responses']:
                        line_data['user_responses'][inp].append(response)
                messagebox.showinfo("Success", "Response added successfully!")
                response_window.destroy()
            else:
                messagebox.showerror("Error", "Response cannot be empty.")

        ttk.Button(response_window, text="Add Response", command=add_response).pack(pady=10)

    # Styled Button
    ttk.Button(main_frame, text="Add Probable Input", command=add_probable_input).pack(pady=10)

    # Navigation Buttons
    ttk.Button(main_frame, text="Back", command=lambda: go_to_previous_line(script_name, index)).pack(side=tk.LEFT, padx=5)
    ttk.Button(main_frame, text="Save and Next", command=save_and_next).pack(side=tk.LEFT, padx=5)

# Function to go to the previous line
def go_to_previous_line(script_name, index):
    if index > 0:
        previous_index = index - 1
        display_line_and_train(script_name, all_scripts[script_name]["dialog"][previous_index], previous_index, len(all_scripts[script_name]["dialog"]), all_scripts[script_name]["dialog"])

# Display Current Script Data
def display_all_scripts():
    script_text = ""
    for script_name, script_content in all_scripts.items():
        script_text += f"Script: {script_name}\n"
        for entry in script_content["dialog"]:
            script_text += f"  Line: {entry['line']}\n"
            if isinstance(entry['user_responses'], dict):  # Ensure it's a dictionary
                for inp, responses in entry['user_responses'].items():
                    script_text += f"    User Input: {inp} -> Bot Responses: {', '.join(responses)}\n"
        script_text += "\n"
    
    if script_text:
        messagebox.showinfo("All Scripts", script_text)
    else:
        messagebox.showinfo("All Scripts", "No scripts added yet.")

# Create the main window
root = ThemedTk(theme="radiance")  # Changed theme for better aesthetics
root.title("Enhanced Call Center Bot Script Manager")
root.geometry("800x600")

# Create a frame for scrolling
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Function to ask for the script name to train
def ask_for_script_name_to_train():
    script_name = simpledialog.askstring("Input", "Enter the Script Name to Train:")
    if script_name and script_name in all_scripts:
        train_lines(script_name, all_scripts[script_name]["dialog"])
    else:
        messagebox.showerror("Error", "Script not found.")

# Add buttons to the main frame
ttk.Button(main_frame, text="Add New Script", command=add_script).pack(pady=5)
ttk.Button(main_frame, text="Show All Scripts", command=display_all_scripts).pack(pady=5)
ttk.Button(main_frame, text="Train Script", command=ask_for_script_name_to_train).pack(pady=5)

# Run the main loop
root.mainloop()
