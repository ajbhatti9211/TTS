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
                line: {"user_responses": [], "bot_responses": []} for line in script_lines
            }
            save_script(script_name, all_scripts[script_name])
            messagebox.showinfo("Success", f"Script '{script_name}' added successfully!")
        else:
            messagebox.showerror("Error", "Invalid Script Content.")
    elif script_name in all_scripts:
        messagebox.showerror("Error", "Script with this name already exists.")
    else:
        messagebox.showerror("Error", "Invalid Script Name.")

# Function to train the script line by line
def train_script():
    selected_script = simpledialog.askstring("Input", "Enter Script Name to Train:")
    if selected_script in all_scripts:
        current_script = all_scripts[selected_script]
        script_lines = list(current_script.keys())
        train_lines(selected_script, current_script, script_lines)
    else:
        messagebox.showerror("Error", "Script does not exist.")

# Function to train lines sequentially
def train_lines(script_name, current_script, script_lines):
    def next_line(index):
        if index < len(script_lines):
            line = script_lines[index]
            line_data = current_script[line]
            display_line_and_train(script_name, line, line_data, index, len(script_lines), script_lines)
        else:
            save_script(script_name, all_scripts[script_name])
            messagebox.showinfo("Training Complete", "The entire script has been trained!")

    # Start training from the first line
    next_line(0)

# Function to display line and start training
def display_line_and_train(script_name, line, line_data, index, total_lines, script_lines):
    window = tk.Toplevel()
    window.transient(root)  # Keep it on top of the root window
    window.title(f"Training Line: {line}")
    window.geometry("600x400")
    
    # Style Configuration
    s = ttk.Style()
    s.configure('TButton', font=('Helvetica', 10), relief='flat', padding=6, background='#4CAF50', foreground='white')
    s.map('TButton', background=[('active', '#66BB6A')], relief=[('pressed', 'flat')])
    
    # Display Line Content
    tk.Label(window, text=f"{line}", font=("Arial", 14, "bold")).pack(pady=10)
    
    # Probable Inputs Section
    input_label = tk.Label(window, text="Enter Probable User Inputs:", font=("Arial", 12))
    input_label.pack(pady=5)
    
    input_entry = ttk.Entry(window, width=50)
    input_entry.pack(pady=5)

    def add_probable_input():
        probable_input = input_entry.get().strip()
        if probable_input:
            line_data['user_responses'].append(probable_input)
            input_entry.delete(0, tk.END)
            decision_after_input(script_name, line, line_data, probable_input, index, script_lines)
        else:
            messagebox.showerror("Error", "Probable Input cannot be empty.")

    # Decision After Input
    def decision_after_input(script_name, line, line_data, probable_input, index, script_lines):
        decision_window = tk.Toplevel(window)
        decision_window.title("Choose Next Step")
        decision_window.geometry("400x200")
        
        tk.Label(decision_window, text=f"Choose Next Step for '{probable_input}'", font=("Arial", 12, "bold")).pack(pady=10)
        
        def add_rebuttal():
            ask_for_rebuttal(script_name, line, line_data, probable_input)
            decision_window.destroy()
        
        def continue_to_next_line():
            decision_window.destroy()
            window.destroy()
            next_index = index + 1
            train_lines(script_name, all_scripts[script_name], script_lines[next_index:])

        def add_more_inputs():
            decision_window.destroy()

        # Smooth Styled Buttons
        ttk.Button(decision_window, text="Add Rebuttal", command=add_rebuttal).pack(side=tk.LEFT, padx=5)
        ttk.Button(decision_window, text="Continue to Next Line", command=continue_to_next_line).pack(side=tk.LEFT, padx=5)
        ttk.Button(decision_window, text="Add Another Probable Input", command=add_more_inputs).pack(side=tk.LEFT, padx=5)

    def ask_for_rebuttal(script_name, line, line_data, probable_input):
        rebuttal_window = tk.Toplevel(window)
        rebuttal_window.title(f"Add Rebuttal for Input: {probable_input}")
        rebuttal_window.geometry("500x200")

        tk.Label(rebuttal_window, text=f"Add Rebuttal for '{probable_input}'", font=("Arial", 12)).pack(pady=5)
        rebuttal_entry = ttk.Entry(rebuttal_window, width=50)
        rebuttal_entry.pack(pady=5)

        def add_rebuttal():
            rebuttal = rebuttal_entry.get().strip()
            if rebuttal:
                line_data['bot_responses'].append(rebuttal)
                messagebox.showinfo("Success", f"Rebuttal added for '{probable_input}'")
                rebuttal_window.destroy()
            else:
                messagebox.showerror("Error", "Rebuttal cannot be empty.")

        ttk.Button(rebuttal_window, text="Add Rebuttal", command=add_rebuttal).pack(pady=10)

    # Styled Button
    ttk.Button(window, text="Add Probable Input", command=add_probable_input).pack(pady=10)

    window.mainloop()

# Display Current Script Data
def display_all_scripts():
    script_text = ""
    for script_name, script_content in all_scripts.items():
        script_text += f"Script: {script_name}\n"
        for line, data in script_content.items():
            script_text += f"  {line}\n"
            script_text += f"    User Responses: {', '.join(data['user_responses'])}\n"
            script_text += f"    Bot Responses: {', '.join(data['bot_responses'])}\n"
        script_text += "\n"
    
    if script_text:
        messagebox.showinfo("All Scripts", script_text)
    else:
        messagebox.showinfo("All Scripts", "No scripts added yet.")

# Create the main window
root = ThemedTk(theme="ubuntu")
root.title("Enhanced Call Center Bot Script Manager")
root.geometry("400x300")

# Buttons for script management
ttk.Button(root, text="Add New Script", command=add_script).pack(pady=5)
ttk.Button(root, text="Train Script", command=train_script).pack(pady=5)
ttk.Button(root, text="Show All Scripts", command=display_all_scripts).pack(pady=5)

# Start the main loop
root.mainloop()
