import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import os


# ── DB Connection ──

def get_connection():
    server   = os.getenv("DB_SERVER", "localhost")
    database = os.getenv("DB_NAME",   "AirportDB")
    user     = os.getenv("DB_USER",   "sa")
    password = os.getenv("DB_PASS",   "StrongPass123")

    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)


# ── Main Application ──

class AirportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airport Management System — Flight Search")
        self.root.geometry("900x600")

        # try connecting to DB up front
        try:
            self.conn = get_connection()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to database:\n{e}")
            self.conn = None

        self.show_main_menu()

    # ── Main Menu ──

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_window()

        tk.Label(self.root, text="Flight Search", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self.root, text="Choose a search option:").pack(pady=5)

        self.selected_option = tk.StringVar(value="airport")

        tk.Radiobutton(self.root, text="Search by Airport Codes and Date",
                       variable=self.selected_option, value="airport",
                       font=("Arial", 12)).pack(pady=5)
        tk.Radiobutton(self.root, text="Search by Flight Number and Date",
                       variable=self.selected_option, value="flight",
                       font=("Arial", 12)).pack(pady=5)

        tk.Button(self.root, text="Next", width=20, font=("Arial", 12),
                  command=self.on_next).pack(pady=20)

    def on_next(self):
        choice = self.selected_option.get()
        if choice == "airport":
            self.show_airport_search()
        else:
            self.show_flight_search()

    # ── 2a: Search by Airport Codes + Date ──

    def show_airport_search(self):
        self.clear_window()

        tk.Label(self.root, text="Search by Airport Codes and Date",
                 font=("Arial", 16, "bold")).pack(pady=10)

        form = tk.Frame(self.root)
        form.pack(pady=10)

        tk.Label(form, text="Departure Airport Code:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.dep_entry = tk.Entry(form, font=("Arial", 11), width=10)
        self.dep_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Arrival Airport Code:", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.arr_entry = tk.Entry(form, font=("Arial", 11), width=10)
        self.arr_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="Date (YYYY-MM-DD):", font=("Arial", 11)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.date_entry = tk.Entry(form, font=("Arial", 11), width=12)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Search", width=12, font=("Arial", 11),
                  command=self.run_airport_search).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Back", width=12, font=("Arial", 11),
                  command=self.show_main_menu).pack(side="left", padx=10)

        # results area
        self.result_frame = tk.Frame(self.root)
        self.result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def run_airport_search(self):
        dep = self.dep_entry.get().strip()
        arr = self.arr_entry.get().strip()
        flight_date = self.date_entry.get().strip()

        if not dep or not arr or not flight_date:
            messagebox.showwarning("Missing Input", "Please fill in all fields.")
            return
        if not self.conn:
            messagebox.showerror("Database Error", "No database connection.")
            return

        # clear previous results
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        cursor = self.conn.cursor()

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

        # direct flights table
        tk.Label(self.result_frame, text="Direct Flights",
                 font=("Arial", 13, "bold")).pack(anchor="w")

        if directs:
            tree = self.make_tree(self.result_frame,
                                 ("Airline", "Flight #", "Date", "From", "Dep Time", "To", "Arr Time"))
            for r in directs:
                tree.insert("", "end", values=(
                    r.Airline, r.Number, r.Date,
                    r.DepCode, r.Scheduled_dep_time,
                    r.ArrCode, r.Scheduled_arr_time
                ))
        else:
            tk.Label(self.result_frame, text="No direct flights found.",
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

        tk.Label(self.result_frame, text="\nConnecting Flights (1-stop)",
                 font=("Arial", 13, "bold")).pack(anchor="w")

        if connects:
            tree = self.make_tree(self.result_frame,
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
            tk.Label(self.result_frame, text="No connecting flights found.",
                     font=("Arial", 11)).pack(anchor="w")

    # ── 2b: Search by Flight Number + Date ──

    def show_flight_search(self):
        self.clear_window()

        tk.Label(self.root, text="Search by Flight Number and Date",
                 font=("Arial", 16, "bold")).pack(pady=10)

        form = tk.Frame(self.root)
        form.pack(pady=10)

        tk.Label(form, text="Flight Number:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.fnum_entry = tk.Entry(form, font=("Arial", 11), width=10)
        self.fnum_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Date (YYYY-MM-DD):", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.fdate_entry = tk.Entry(form, font=("Arial", 11), width=12)
        self.fdate_entry.grid(row=1, column=1, padx=5, pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Search", width=12, font=("Arial", 11),
                  command=self.run_flight_search).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Back", width=12, font=("Arial", 11),
                  command=self.show_main_menu).pack(side="left", padx=10)

        self.result_frame = tk.Frame(self.root)
        self.result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def run_flight_search(self):
        flight_no = self.fnum_entry.get().strip()
        flight_date = self.fdate_entry.get().strip()

        if not flight_no or not flight_date:
            messagebox.showwarning("Missing Input", "Please fill in all fields.")
            return
        if not self.conn:
            messagebox.showerror("Database Error", "No database connection.")
            return

        try:
            flight_no = int(flight_no)
        except ValueError:
            messagebox.showwarning("Invalid Input", "Flight number must be a number.")
            return

        for widget in self.result_frame.winfo_children():
            widget.destroy()

        cursor = self.conn.cursor()

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
            tk.Label(self.result_frame,
                     text=f"Flight {rows[0].Number} — {rows[0].Airline}   |   Date: {rows[0].Date}",
                     font=("Arial", 13, "bold")).pack(anchor="w")

            tree = self.make_tree(self.result_frame,
                                 ("Leg", "From", "City", "Dep Time", "To", "City", "Arr Time"))
            for r in rows:
                tree.insert("", "end", values=(
                    r.Leg_no, r.DepCode, r.DepCity,
                    r.Scheduled_dep_time,
                    r.ArrCode, r.ArrCity,
                    r.Scheduled_arr_time
                ))
        else:
            tk.Label(self.result_frame,
                     text=f"No flight found with number {flight_no} on {flight_date}.",
                     font=("Arial", 12)).pack(anchor="w")

    # ── Helper: create a scrollable Treeview table ──

    def make_tree(self, parent, columns):
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


# ── Run ──

if __name__ == "__main__":
    root = tk.Tk()
    app = AirportApp(root)
    root.mainloop()
