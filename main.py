import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import statusresolver

# Create the main application window
root = tk.Tk()
root.title("Absent Status Resolver")

# Set the window size
root.geometry("300x200")

# Create a label for the date picker
label = tk.Label(root, text="Select a date:")
label.pack(pady=10)

# Create a DateEntry widget (date picker)
date_picker = DateEntry(root, width=12, background='darkblue',
                        foreground='white', borderwidth=2)
date_picker.pack(pady=10)

# Function to be called when the button is clicked
def on_submit():
    selected_date = date_picker.get_date()  # Get the selected date
    formatted_date = selected_date.strftime("%m/%d/%Y")
    statusresolver.ProcessDate(formatted_date)

# Create a button to submit the date
submit_button = tk.Button(root, text="Submit Date", command=on_submit)
submit_button.pack(pady=10)

def on_quit():
    exit()

quit_button = tk.Button(root, text="Exit", command=on_quit)
quit_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()