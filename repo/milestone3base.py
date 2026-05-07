import tkinter as tk

root = tk.Tk()
root.title("Multi-Screen GUI")

# -------------------------
# Helper to switch screens
# -------------------------
def show_frame(frame):
    frame.tkraise()

# -------------------------
# Logic for Screen 1
# -------------------------
def next_action():
    choice = selected_option.get()

    if choice == "None":
        label.config(text="Please select an option first")
    elif choice == "Enter Airport Codes and Date:":
        show_frame(screen_airport)
    elif choice == "Enter Flight Number and Date:":
        show_frame(screen_flight)

# -------------------------
# Logic for Screen A (Airport Codes)
# -------------------------
def check_airport_inputs():
    code = entry_code.get()
    date = entry_date.get()
    result_label_A.config(text=f"Entered: {code}, {date}")

def next_from_airport():
    show_frame(screen_C)

def back_to_main():
    show_frame(screen_main)

# -------------------------
# Logic for Screen B (Flight Number)
# -------------------------
def check_flight_input():
    flight = entry_flight.get()
    result_label_B.config(text=f"Entered Flight: {flight}")

def next_from_flight():
    show_frame(screen_C)

def back_to_main_B():
    show_frame(screen_main)

# -------------------------
# Logic for Screen C
# -------------------------
def create_report():
    value = entry_report.get()
    result_label_C.config(text=f"Report created for: {value}")

def next_from_C():
    show_frame(screen_D)

def back_from_C():
    show_frame(screen_main)

# -------------------------
# Logic for Screen D (Buy a Seat)
# -------------------------
def next_from_D():
    show_frame(screen_E)

def back_from_D():
    show_frame(screen_C)

# -------------------------
# Logic for Screen E (Back only)
# -------------------------
def back_from_E():
    show_frame(screen_D)

# -------------------------
# Create frames
# -------------------------
screen_main = tk.Frame(root)
screen_airport = tk.Frame(root)
screen_flight = tk.Frame(root)
screen_C = tk.Frame(root)
screen_D = tk.Frame(root)
screen_E = tk.Frame(root)

for frame in (screen_main, screen_airport, screen_flight, screen_C, screen_D, screen_E):
    frame.grid(row=0, column=0, sticky="nsew")

# -------------------------
# MAIN SCREEN (Radio Buttons)
# -------------------------
label = tk.Label(screen_main, text="Choose an option")
label.pack(pady=10)

selected_option = tk.StringVar(value="None")

radio_one = tk.Radiobutton(
    screen_main,
    text="Search by Airport Codes",
    variable=selected_option,
    value="Enter Airport Codes and Date:"
)
radio_one.pack(pady=5)

radio_two = tk.Radiobutton(
    screen_main,
    text="Select by Flight Number",
    variable=selected_option,
    value="Enter Flight Number and Date:"
)
radio_two.pack(pady=5)

next_button = tk.Button(screen_main, text="Next", width=20, command=next_action)
next_button.pack(pady=20)

# -------------------------
# SCREEN A — Airport Code Search
# -------------------------
label_airport = tk.Label(screen_airport, text="Enter Airport Codes and Date")
label_airport.pack(pady=10)

entry_code = tk.Entry(screen_airport, width=30)
entry_code.pack(pady=5)
entry_code.insert(0, "Airport Code (e.g., DFW)")

entry_date = tk.Entry(screen_airport, width=30)
entry_date.pack(pady=5)
entry_date.insert(0, "Date (YYYY-MM-DD)")

check_button_A = tk.Button(screen_airport, text="Check", width=20, command=check_airport_inputs)
check_button_A.pack(pady=10)

next_airport = tk.Button(screen_airport, text="Next", width=20, command=next_from_airport)
next_airport.pack(pady=10)

back_button_A = tk.Button(screen_airport, text="Back", width=20, command=back_to_main)
back_button_A.pack(pady=10)

result_label_A = tk.Label(screen_airport, text="")
result_label_A.pack(pady=10)

# -------------------------
# SCREEN B — Flight Number Search
# -------------------------
label_flight = tk.Label(screen_flight, text="Enter Flight Number")
label_flight.pack(pady=10)

entry_flight = tk.Entry(screen_flight, width=30)
entry_flight.pack(pady=5)
entry_flight.insert(0, "Flight Number (e.g., AA123)")

check_button_B = tk.Button(screen_flight, text="Check", width=20, command=check_flight_input)
check_button_B.pack(pady=10)

next_flight = tk.Button(screen_flight, text="Next", width=20, command=next_from_flight)
next_flight.pack(pady=10)

back_button_B = tk.Button(screen_flight, text="Back", width=20, command=back_to_main_B)
back_button_B.pack(pady=10)

result_label_B = tk.Label(screen_flight, text="")
result_label_B.pack(pady=10)

# -------------------------
# SCREEN C — Final Screen
# -------------------------
label_C = tk.Label(screen_C, text="Final Screen: Create Report")
label_C.pack(pady=10)

entry_report = tk.Entry(screen_C, width=30)
entry_report.pack(pady=5)
entry_report.insert(0, "Enter report name")

create_button = tk.Button(screen_C, text="Create Report", width=20, command=create_report)
create_button.pack(pady=10)

next_C = tk.Button(screen_C, text="Next", width=20, command=next_from_C)
next_C.pack(pady=10)

back_C = tk.Button(screen_C, text="Back", width=20, command=back_from_C)
back_C.pack(pady=10)

result_label_C = tk.Label(screen_C, text="")
result_label_C.pack(pady=10)

# -------------------------
# SCREEN D — Buy a Seat + Back
# -------------------------
label_D = tk.Label(screen_D, text="Screen D")
label_D.pack(pady=10)

buy_button = tk.Button(screen_D, text="Buy a Seat", width=20, command=next_from_D)
buy_button.pack(pady=10)

back_D = tk.Button(screen_D, text="Back", width=20, command=back_from_D)
back_D.pack(pady=10)

result_label_D = tk.Label(screen_D, text="")
result_label_D.pack(pady=10)

# -------------------------
# SCREEN E — Back Only
# -------------------------
label_E = tk.Label(screen_E, text="Screen E")
label_E.pack(pady=20)

back_E = tk.Button(screen_E, text="Back", width=20, command=back_from_E)
back_E.pack(pady=10)

# -------------------------
# Start on main screen
# -------------------------
show_frame(screen_main)

root.mainloop()
