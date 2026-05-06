import tkinter as tk

def next_action():
    choice = selected_option.get()
    label.config(text=f"You selected: {choice}")

root = tk.Tk()
root.title("Radio Buttons and Next")

# Label
label = tk.Label(root, text="Choose an option")
label.pack(pady=10)

# Variable to store radio selection
selected_option = tk.StringVar(value="None")

# Radio buttons
radio_one = tk.Radiobutton(root, text="Search by Airport Codes", variable=selected_option, value="Enter Airport Codes and Date:")
radio_one.pack(pady=5)

radio_two = tk.Radiobutton(root, text="Select by Flight Number", variable=selected_option, value="Enter Flight Number and Date:")
radio_two.pack(pady=5)

# Next button
next_button = tk.Button(root, text="Next", width=20, command=next_action)
next_button.pack(pady=20)

root.mainloop()
