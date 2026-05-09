import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import os


# ── DB Connection ──

def get_connection():   #Make sure to update these to test it
    return pyodbc.connect(
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=localhost,1433;"
        "Database=AirportDB;"
        "UID=sa;"
        "PWD=NewStrongPassword123!;"
        "Encrypt=no;"
    )


# ── Globals ──

conn = None

root = tk.Tk()
root.title("Airport Management System")
root.geometry("900x600")

# -------------------------
# Helper to switch screens
# -------------------------
def show_frame(frame):
    frame.tkraise()

# -------------------------
# DB connect on startup
# -------------------------
try:
    conn = get_connection()
except Exception as e:
    messagebox.showerror("Database Error", f"Could not connect to database:\n{e}")

# -------------------------
# Logic for Screen 1 (Main Menu)
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
# Helper: create a scrollable Treeview table
# -------------------------
def make_tree(parent, columns):
    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True, pady=5)

    tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=110, anchor="center")

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return tree

# -------------------------
# Logic for Screen A (Airport Codes) — Flight Search 2a
# -------------------------
def next_from_airport():
    show_frame(screen_C)

def next_from_flight():
    show_frame(screen_C)
def search_by_airport():
    dep = entry_dep_code.get().strip()
    arr = entry_arr_code.get().strip()
    flight_date = entry_date_a.get().strip()

    if not dep or not arr or not flight_date:
        messagebox.showwarning("Missing Input", "Please fill in all fields.")
        return
    if not conn:
        messagebox.showerror("Database Error", "No database connection.")
        return

    # clear previous results
    for widget in result_frame_a.winfo_children():
        widget.destroy()

    cursor = conn.cursor()

    # ── Direct flights ──
    direct_sql = """
        SELECT f.Number, f.Airline, li.Date,
               fl.Scheduled_dep_time, fl.Scheduled_arr_time,
               dep.Airport_code AS DepCode, arr.Airport_code AS ArrCode
        FROM LEG_INSTANCE li
        JOIN FLIGHT_LEG fl ON fl.Flight_number = li.Flight_number AND fl.Leg_no = li.Leg_no
        JOIN FLIGHT f ON f.Number = fl.Flight_number
        JOIN AIRPORT dep ON dep.Airport_code = fl.Dep_airport_code
        JOIN AIRPORT arr ON arr.Airport_code = fl.Arr_airport_code
        WHERE UPPER(dep.Airport_code) = UPPER(?)
          AND UPPER(arr.Airport_code) = UPPER(?)
          AND li.Date = ?
        ORDER BY f.Number, fl.Leg_no
    """
    try:
        cursor.execute(direct_sql, (dep, arr, flight_date))
        directs = cursor.fetchall()
    except pyodbc.Error as e:
        messagebox.showerror("Query Error", str(e))
        return

    tk.Label(result_frame_a, text="Direct Flights",
             font=("Arial", 13, "bold")).pack(anchor="w")

    if directs:
        tree = make_tree(result_frame_a,
                         ("Airline", "Flight #", "Date", "From", "Dep Time", "To", "Arr Time"))
        for r in directs:
            tree.insert("", "end", values=(
                r.Airline, r.Number, r.Date,
                r.DepCode, r.Scheduled_dep_time,
                r.ArrCode, r.Scheduled_arr_time
            ))
    else:
        tk.Label(result_frame_a, text="No direct flights found.",
                 font=("Arial", 11)).pack(anchor="w")

    # ── Connecting flights (1-hour min layover) ──
    connect_sql = """
        SELECT f1.Number AS FlightNo1, f1.Airline AS Airline1, li1.Date,
               fl1.Scheduled_dep_time AS Dep1, fl1.Scheduled_arr_time AS Arr1,
               dep.Airport_code AS DepCode, mid.Airport_code AS MidCode,
               f2.Number AS FlightNo2, f2.Airline AS Airline2,
               fl2.Scheduled_dep_time AS Dep2, fl2.Scheduled_arr_time AS Arr2,
               arr.Airport_code AS ArrCode
        FROM LEG_INSTANCE li1
        JOIN FLIGHT_LEG fl1 ON fl1.Flight_number = li1.Flight_number
                            AND fl1.Leg_no = li1.Leg_no
        JOIN FLIGHT_LEG fl2 ON fl2.Dep_airport_code = fl1.Arr_airport_code
        JOIN LEG_INSTANCE li2 ON li2.Flight_number = fl2.Flight_number
                              AND li2.Leg_no = fl2.Leg_no
                              AND li2.Date = li1.Date
        JOIN FLIGHT f1 ON f1.Number = fl1.Flight_number
        JOIN FLIGHT f2 ON f2.Number = fl2.Flight_number
        JOIN AIRPORT dep ON dep.Airport_code = fl1.Dep_airport_code
        JOIN AIRPORT mid ON mid.Airport_code = fl1.Arr_airport_code
        JOIN AIRPORT arr ON arr.Airport_code = fl2.Arr_airport_code
        WHERE UPPER(dep.Airport_code) = UPPER(?)
          AND UPPER(arr.Airport_code) = UPPER(?)
          AND li1.Date = ?
          AND DATEDIFF(MINUTE, fl1.Scheduled_arr_time, fl2.Scheduled_dep_time) >= 60
          AND fl1.Arr_airport_code <> fl2.Arr_airport_code
        ORDER BY f1.Number, f2.Number
    """
    try:
        cursor.execute(connect_sql, (dep, arr, flight_date))
        connects = cursor.fetchall()
    except pyodbc.Error as e:
        messagebox.showerror("Query Error", str(e))
        return

    tk.Label(result_frame_a, text="\nConnecting Flights (1-stop)",
             font=("Arial", 13, "bold")).pack(anchor="w")

    if connects:
        tree = make_tree(result_frame_a,
                         ("Leg", "Airline", "Flight #", "Date", "From", "Dep Time", "To", "Arr Time"))
        seen = set()
        for r in connects:
            key = (r.FlightNo1, r.FlightNo2)
            if key in seen:
                continue
            seen.add(key)
            tree.insert("", "end", values=(
                "1", r.Airline1, r.FlightNo1, r.Date,
                r.DepCode, r.Dep1, r.MidCode, r.Arr1
            ))
            tree.insert("", "end", values=(
                "2", r.Airline2, r.FlightNo2, r.Date,
                r.MidCode, r.Dep2, r.ArrCode, r.Arr2
            ))
            tree.insert("", "end", values=("", "", "", "", "", "", "", ""))
    else:
        tk.Label(result_frame_a, text="No connecting flights found.",
                 font=("Arial", 11)).pack(anchor="w")

def back_to_main():
    show_frame(screen_main)

# -------------------------
# Logic for Screen B (Flight Number) — Flight Search 2b
# -------------------------
def search_by_flight():
    flight_no = entry_flight.get().strip()
    flight_date = entry_date_b.get().strip()

    if not flight_no or not flight_date:
        messagebox.showwarning("Missing Input", "Please fill in all fields.")
        return
    if not conn:
        messagebox.showerror("Database Error", "No database connection.")
        return

    try:
        flight_no = int(flight_no)
    except ValueError:
        messagebox.showwarning("Invalid Input", "Flight number must be a number.")
        return

    # clear previous results
    for widget in result_frame_b.winfo_children():
        widget.destroy()

    cursor = conn.cursor()

    sql = """
        SELECT f.Number, f.Airline, li.Date,
               fl.Scheduled_dep_time, fl.Scheduled_arr_time,
               dep.Airport_code AS DepCode, dep.City AS DepCity,
               arr.Airport_code AS ArrCode, arr.City AS ArrCity,
               fl.Leg_no
        FROM FLIGHT f
        JOIN FLIGHT_LEG fl ON fl.Flight_number = f.Number
        JOIN LEG_INSTANCE li ON li.Flight_number = f.Number AND li.Leg_no = fl.Leg_no
        JOIN AIRPORT dep ON dep.Airport_code = fl.Dep_airport_code
        JOIN AIRPORT arr ON arr.Airport_code = fl.Arr_airport_code
        WHERE f.Number = ? AND li.Date = ?
        ORDER BY fl.Leg_no
    """
    try:
        cursor.execute(sql, (flight_no, flight_date))
        rows = cursor.fetchall()
    except pyodbc.Error as e:
        messagebox.showerror("Query Error", str(e))
        return

    if rows:
        tk.Label(result_frame_b,
                 text=f"Flight {rows[0].Number} — {rows[0].Airline}   |   Date: {rows[0].Date}",
                 font=("Arial", 13, "bold")).pack(anchor="w")

        tree = make_tree(result_frame_b,
                         ("Leg", "From", "City", "Dep Time", "To", "City", "Arr Time"))
        for r in rows:
            tree.insert("", "end", values=(
                r.Leg_no, r.DepCode, r.DepCity,
                r.Scheduled_dep_time,
                r.ArrCode, r.ArrCity,
                r.Scheduled_arr_time
            ))
    else:
        tk.Label(result_frame_b,
                 text=f"No flight found with number {flight_no} on {flight_date}.",
                 font=("Arial", 12)).pack(anchor="w")

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

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

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
# SCREEN A — Airport Code Search (Flight Search 2a)
# -------------------------
tk.Label(screen_airport, text="Search by Airport Codes and Date",
         font=("Arial", 14, "bold")).pack(pady=10)

form_a = tk.Frame(screen_airport)
form_a.pack(pady=10)

tk.Label(form_a, text="Departure Airport Code:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_dep_code = tk.Entry(form_a, font=("Arial", 11), width=10)
entry_dep_code.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_a, text="Arrival Airport Code:", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_arr_code = tk.Entry(form_a, font=("Arial", 11), width=10)
entry_arr_code.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form_a, text="Date (YYYY-MM-DD):", font=("Arial", 11)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
entry_date_a = tk.Entry(form_a, font=("Arial", 11), width=12)
entry_date_a.grid(row=2, column=1, padx=5, pady=5)

btn_frame_a = tk.Frame(screen_airport)
btn_frame_a.pack(pady=10)

tk.Button(btn_frame_a, text="Search", width=12, font=("Arial", 11),
          command=search_by_airport).pack(side="left", padx=10)

tk.Button(btn_frame_a, text="Next", width=12, font=("Arial", 11),
          command=next_from_airport).pack(side="left", padx=10)

tk.Button(btn_frame_a, text="Back", width=12, font=("Arial", 11),
          command=back_to_main).pack(side="left", padx=10)


result_frame_a = tk.Frame(screen_airport)
result_frame_a.pack(fill="both", expand=True, padx=10, pady=10)

# -------------------------
# SCREEN B — Flight Number Search (Flight Search 2b)
# -------------------------
tk.Label(screen_flight, text="Search by Flight Number and Date",
         font=("Arial", 14, "bold")).pack(pady=10)

form_b = tk.Frame(screen_flight)
form_b.pack(pady=10)

tk.Label(form_b, text="Flight Number:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_flight = tk.Entry(form_b, font=("Arial", 11), width=10)
entry_flight.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_b, text="Date (YYYY-MM-DD):", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_date_b = tk.Entry(form_b, font=("Arial", 11), width=12)
entry_date_b.grid(row=1, column=1, padx=5, pady=5)

btn_frame_b = tk.Frame(screen_flight)
btn_frame_b.pack(pady=10)

tk.Button(btn_frame_b, text="Search", width=12, font=("Arial", 11),
          command=search_by_flight).pack(side="left", padx=10)

tk.Button(btn_frame_b, text="Next", width=12, font=("Arial", 11),
          command=next_from_flight).pack(side="left", padx=10)

tk.Button(btn_frame_b, text="Back", width=12, font=("Arial", 11),
          command=back_to_main_B).pack(side="left", padx=10)


result_frame_b = tk.Frame(screen_flight)
result_frame_b.pack(fill="both", expand=True, padx=10, pady=10)

# -------------------------
# SCREEN C — SQL Query
# -------------------------

def run_aircraft_utilization():
    reg = entry_airplane_id.get().strip()
    start = entry_start_date.get().strip()
    end = entry_end_date.get().strip()

    if not reg or not start or not end:
        messagebox.showwarning("Missing Input", "Please fill in all fields.")
        return

    if not conn:
        messagebox.showerror("Database Error", "No database connection.")
        return

    # Clear previous results
    for widget in result_frame_C.winfo_children():
        widget.destroy()

    cursor = conn.cursor()

    sql = """
        SELECT 
            A.Airplane_id AS Registration,
            AT.Type_name AS AirplaneType,
            COUNT(LI.Leg_no) AS TotalFlights
        FROM AIRPLANE A
        LEFT JOIN AIRPLANE_TYPE AT
            ON A.Type_name = AT.Type_name
        LEFT JOIN LEG_INSTANCE LI
            ON A.Airplane_id = LI.Airplane_id
            AND LI.Date BETWEEN ? AND ?
        WHERE A.Airplane_id = ?
        GROUP BY A.Airplane_id, AT.Type_name
    """

    try:
        cursor.execute(sql, (start, end, reg))
        rows = cursor.fetchall()
    except pyodbc.Error as e:
        messagebox.showerror("Query Error", str(e))
        return

    tk.Label(result_frame_C, text="Aircraft Utilization Report",
             font=("Arial", 14, "bold")).pack(anchor="w")

    if rows:
        tree = make_tree(result_frame_C,
                         ("Registration", "Airplane Type", "Total Flights"))
        for r in rows:
            tree.insert("", "end", values=(r.Registration, r.AirplaneType, r.TotalFlights))
    else:
        tk.Label(result_frame_C, text="No data found for this airplane.",
                 font=("Arial", 12)).pack(anchor="w")


# -------------------------
# SCREEN C — Aircraft Utilization Report
# -------------------------
tk.Label(screen_C, text="Aircraft Utilization Report",
         font=("Arial", 16, "bold")).pack(pady=10)

form_C = tk.Frame(screen_C)
form_C.pack(pady=10)

tk.Label(form_C, text="Airplane Registration #:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_airplane_id = tk.Entry(form_C, font=("Arial", 11), width=15)
entry_airplane_id.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_C, text="Start Date (YYYY-MM-DD):", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_start_date = tk.Entry(form_C, font=("Arial", 11), width=15)
entry_start_date.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form_C, text="End Date (YYYY-MM-DD):", font=("Arial", 11)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
entry_end_date = tk.Entry(form_C, font=("Arial", 11), width=15)
entry_end_date.grid(row=2, column=1, padx=5, pady=5)

btn_frame_C = tk.Frame(screen_C)
btn_frame_C.pack(pady=10)

tk.Button(btn_frame_C, text="Create Report", width=15, font=("Arial", 11),
          command=run_aircraft_utilization).pack(side="left", padx=10)

tk.Button(btn_frame_C, text="Next", width=12, font=("Arial", 11),
          command=next_from_C).pack(side="left", padx=10)

tk.Button(btn_frame_C, text="Back", width=12, font=("Arial", 11),
          command=back_from_C).pack(side="left", padx=10)

result_frame_C = tk.Frame(screen_C)
result_frame_C.pack(fill="both", expand=True, padx=10, pady=10)


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
