"""
CS-4347 Airport Management System — Milestone 2
Command-line host application (Python + pyodbc → MS SQL Server)

Features:
  1. Flight Search
     1a. Travel itinerary between two airports (direct + 1-stop connecting)
     1b. Flight details by flight number
  2. Infrastructure Reports
     2a. Aircraft Utilization Report (by time period)
  3. Passenger & Booking Queries
     3a. Seat Availability Check (flight + date)
     3b. Passenger Itinerary Retrieval ("my trips")
"""

import pyodbc
import sys
import os
from datetime import datetime, date
from queries.flight_search_by_number import search_flight_by_number
from queries.seat_availability import check_seat_availability

# ─────────────────────────────────────────────
# CONNECTION
# ─────────────────────────────────────────────

def get_connection():
    """
    Returns a pyodbc connection.  Reads optional env vars so credentials
    are not hard-coded:
        DB_SERVER   (default: localhost)
        DB_NAME     (default: AirportDB)
        DB_USER     (default: sa)
        DB_PASS     (default: StrongPass123)
    """
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


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def hr(char="─", width=70):
    print(char * width)

def section(title):
    hr()
    print(f"  {title}")
    hr()

def ask(prompt, required=True):
    while True:
        val = input(f"  {prompt}: ").strip()
        if val or not required:
            return val
        print("  [!] This field is required.")

def pause():
    input("\n  Press Enter to continue...")


# ─────────────────────────────────────────────
# 1a. TRAVEL ITINERARY  (direct + 1-stop)
# ─────────────────────────────────────────────

def flight_search_itinerary(conn):
    section("Flight Search — Travel Itinerary")
    print("  Search by city name OR three-letter airport code.")
    origin_input = ask("Origin (city or code)")
    dest_input   = ask("Destination (city or code)")

    cursor = conn.cursor()

    # ── Direct flights ──────────────────────────────────────────────────
    direct_sql = """
        SELECT
            f.Number        AS FlightNo,
            f.Airline,
            f.Weekdays,
            dep.Airport_code AS DepCode,
            dep.City         AS DepCity,
            dep.State        AS DepState,
            arr.Airport_code AS ArrCode,
            arr.City         AS ArrCity,
            arr.State        AS ArrState,
            fl.Leg_no,
            fl.Scheduled_dep_time,
            fl.Scheduled_arr_time
        FROM FLIGHT_LEG fl
        JOIN FLIGHT  f   ON f.Number         = fl.Flight_number
        JOIN AIRPORT dep ON dep.Airport_code  = fl.Dep_airport_code
        JOIN AIRPORT arr ON arr.Airport_code  = fl.Arr_airport_code
        WHERE
            (UPPER(dep.Airport_code) = UPPER(?) OR UPPER(dep.City) LIKE UPPER(?))
            AND
            (UPPER(arr.Airport_code) = UPPER(?) OR UPPER(arr.City) LIKE UPPER(?))
        ORDER BY f.Number, fl.Leg_no
    """

    like = f"%{origin_input}%"
    like2 = f"%{dest_input}%"
    cursor.execute(direct_sql, (origin_input, like, dest_input, like2))
    directs = cursor.fetchall()

    print(f"\n  ── Direct Flights ({'found' if directs else 'none found'}) ──")
    if directs:
        for r in directs:
            print(f"  Flight {r.FlightNo} ({r.Airline}) | Leg {r.Leg_no} | "
                  f"{r.DepCode} {r.DepCity} {r.Scheduled_dep_time} → "
                  f"{r.ArrCode} {r.ArrCity} {r.Scheduled_arr_time} | "
                  f"Operates: {r.Weekdays or 'daily'}")
    else:
        print("  No direct flights found between those airports.")

    # ── One-stop connecting flights ──────────────────────────────────────
    connect_sql = """
        SELECT
            f1.Number          AS FlightNo1,
            f1.Airline         AS Airline1,
            f1.Weekdays        AS Weekdays1,
            dep.Airport_code   AS DepCode,
            dep.City           AS DepCity,
            fl1.Leg_no         AS LegNo1,
            fl1.Scheduled_dep_time AS Dep1,
            fl1.Scheduled_arr_time AS Arr1,
            mid.Airport_code   AS MidCode,
            mid.City           AS MidCity,
            f2.Number          AS FlightNo2,
            f2.Airline         AS Airline2,
            f2.Weekdays        AS Weekdays2,
            fl2.Leg_no         AS LegNo2,
            fl2.Scheduled_dep_time AS Dep2,
            fl2.Scheduled_arr_time AS Arr2,
            arr.Airport_code   AS ArrCode,
            arr.City           AS ArrCity
        FROM FLIGHT_LEG fl1
        JOIN FLIGHT_LEG fl2 ON fl2.Dep_airport_code = fl1.Arr_airport_code
        JOIN FLIGHT  f1  ON f1.Number         = fl1.Flight_number
        JOIN FLIGHT  f2  ON f2.Number         = fl2.Flight_number
        JOIN AIRPORT dep ON dep.Airport_code  = fl1.Dep_airport_code
        JOIN AIRPORT mid ON mid.Airport_code  = fl1.Arr_airport_code
        JOIN AIRPORT arr ON arr.Airport_code  = fl2.Arr_airport_code
        WHERE
            (UPPER(dep.Airport_code) = UPPER(?) OR UPPER(dep.City) LIKE UPPER(?))
            AND
            (UPPER(arr.Airport_code) = UPPER(?) OR UPPER(arr.City) LIKE UPPER(?))
            AND fl1.Arr_airport_code <> fl2.Arr_airport_code
        ORDER BY f1.Number, fl1.Leg_no, f2.Number, fl2.Leg_no
    """

    cursor.execute(connect_sql, (origin_input, like, dest_input, like2))
    connects = cursor.fetchall()

    print(f"\n  ── One-Stop Connecting Flights ({'found' if connects else 'none found'}) ──")
    if connects:
        seen = set()
        for r in connects:
            key = (r.FlightNo1, r.LegNo1, r.FlightNo2, r.LegNo2)
            if key in seen:
                continue
            seen.add(key)
            print(f"  Leg 1 → Flight {r.FlightNo1} ({r.Airline1}) Leg {r.LegNo1}: "
                  f"{r.DepCode} {r.DepCity} {r.Dep1} → {r.MidCode} {r.MidCity} {r.Arr1}")
            print(f"  Leg 2 → Flight {r.FlightNo2} ({r.Airline2}) Leg {r.LegNo2}: "
                  f"{r.MidCode} {r.MidCity} {r.Dep2} → {r.ArrCode} {r.ArrCity} {r.Arr2}")
            print()
    else:
        print("  No one-stop connecting flights found.")

    pause()


# ─────────────────────────────────────────────
# 1b. FLIGHT DETAILS BY FLIGHT NUMBER
# ─────────────────────────────────────────────

def run_flight_search_by_number(conn):
    section("Flight Search — By Flight Number")
    flight_no = ask("Flight number")
    search_flight_by_number(flight_no)
    pause()


# ─────────────────────────────────────────────
# 2. AIRCRAFT UTILIZATION REPORT
# ─────────────────────────────────────────────

def aircraft_utilization_report(conn):
    section("Infrastructure Report — Aircraft Utilization")
    print("  List every airplane with total flights assigned in a date range.\n")

    start_str = ask("Start date (YYYY-MM-DD)")
    end_str   = ask("End date   (YYYY-MM-DD)")

    try:
        datetime.strptime(start_str, "%Y-%m-%d")
        datetime.strptime(end_str,   "%Y-%m-%d")
    except ValueError:
        print("  [!] Invalid date format. Use YYYY-MM-DD.")
        pause()
        return

    cursor = conn.cursor()
    sql = """
        SELECT
            a.Airplane_id,
            at.Type_name,
            at.Company,
            a.Total_no_of_seats,
            COUNT(li.Flight_number) AS TotalFlights
        FROM AIRPLANE a
        JOIN AIRPLANE_TYPE at ON at.Type_name   = a.Type_name
        LEFT JOIN LEG_INSTANCE li
            ON  li.Airplane_id = a.Airplane_id
            AND li.Date BETWEEN ? AND ?
        GROUP BY
            a.Airplane_id,
            at.Type_name,
            at.Company,
            a.Total_no_of_seats
        ORDER BY TotalFlights DESC, a.Airplane_id
    """
    cursor.execute(sql, (start_str, end_str))
    rows = cursor.fetchall()

    if not rows:
        print("  No airplanes found.")
        pause()
        return

    print(f"\n  {'Airplane ID':<20} {'Type':<12} {'Company':<20} {'Seats':>6} {'Flights':>8}")
    hr("─", 70)
    for r in rows:
        print(f"  {r.Airplane_id:<20} {r.Type_name:<12} {r.Company:<20} "
              f"{r.Total_no_of_seats:>6} {r.TotalFlights:>8}")
    print(f"\n  Total aircraft listed: {len(rows)}")
    pause()


# ─────────────────────────────────────────────
# 3a. SEAT AVAILABILITY CHECK
# ─────────────────────────────────────────────

def run_seat_availability(conn):
    section("Passenger & Booking — Seat Availability Check")
    flight_no = ask("Flight number")
    date_str  = ask("Date (YYYY-MM-DD)")
    check_seat_availability(flight_no, date_str)
    pause()


# ─────────────────────────────────────────────
# 3b. PASSENGER ITINERARY ("my trips")
# ─────────────────────────────────────────────

def passenger_itinerary(conn):
    section("Passenger & Booking — Passenger Itinerary Retrieval")
    print("  Search by customer name (partial match supported).\n")
    name = ask("Customer name (or partial name)")

    cursor = conn.cursor()
    sql = """
        SELECT
            s.Customer_name,
            s.Cphone,
            s.Date,
            s.Leg_no,
            s.Seat_no,
            s.Airplane_id,
            li.Flight_number,
            fl.Dep_airport_code,
            dep.City            AS DepCity,
            fl.Arr_airport_code,
            arr.City            AS ArrCity,
            li.Dep_time,
            li.Arr_time,
            at.Type_name        AS AircraftType
        FROM SEAT s
        JOIN LEG_INSTANCE li  ON  li.Airplane_id   = s.Airplane_id
                               AND li.Leg_no        = s.Leg_no
                               AND li.Date          = s.Date
        JOIN FLIGHT_LEG   fl  ON  fl.Flight_number  = li.Flight_number
                               AND fl.Leg_no        = li.Leg_no
        JOIN AIRPORT      dep ON  dep.Airport_code  = fl.Dep_airport_code
        JOIN AIRPORT      arr ON  arr.Airport_code  = fl.Arr_airport_code
        JOIN AIRPLANE     a   ON  a.Airplane_id     = s.Airplane_id
        JOIN AIRPLANE_TYPE at ON  at.Type_name      = a.Type_name
        WHERE UPPER(s.Customer_name) LIKE UPPER(?)
        ORDER BY s.Date, li.Flight_number, s.Leg_no
    """
    cursor.execute(sql, (f"%{name}%",))
    rows = cursor.fetchall()

    if not rows:
        print(f"\n  No bookings found for customer matching '{name}'.")
        pause()
        return

    # Group by customer
    customers = {}
    for r in rows:
        key = (r.Customer_name, r.Cphone)
        customers.setdefault(key, []).append(r)

    for (cname, cphone), legs in customers.items():
        print(f"\n  Passenger: {cname}   Phone: {cphone or 'N/A'}")
        hr("─", 60)
        for r in legs:
            print(f"  {r.Date}  Flight {r.Flight_number}  Leg {r.Leg_no}  "
                  f"Seat {r.Seat_no}  [{r.AircraftType}]")
            print(f"           {r.Dep_airport_code} ({r.DepCity}) {r.Dep_time}  →  "
                  f"{r.Arr_airport_code} ({r.ArrCity}) {r.Arr_time}")

    pause()


# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────

MENU = """
  CS-4347 Airport Management System — Milestone 2
  ─────────────────────────────────────────────────
  1. Flight Search — Travel Itinerary (direct + 1-stop)
  2. Flight Search — By Flight Number
  3. Infrastructure Report — Aircraft Utilization
  4. Seat Availability Check
  5. Passenger Itinerary Retrieval ("my trips")
  0. Exit
"""

def main():
    print("\n  Connecting to database...")
    try:
        conn = get_connection()
        print("  Connected.\n")
    except Exception as e:
        print(f"  [ERROR] Could not connect to database:\n  {e}")
        print("\n  Make sure DB_SERVER, DB_NAME, DB_USER, DB_PASS are set correctly.")
        sys.exit(1)

    dispatch = {
        "1": flight_search_itinerary,
        "2": run_flight_search_by_number,
        "3": aircraft_utilization_report,
        "4": run_seat_availability,
        "5": passenger_itinerary,
    }

    while True:
        print(MENU)
        choice = input("  Enter choice: ").strip()
        if choice == "0":
            print("\n  Goodbye.\n")
            break
        elif choice in dispatch:
            try:
                dispatch[choice](conn)
            except pyodbc.Error as e:
                print(f"\n  [DB ERROR] {e}")
                pause()
        else:
            print("  Invalid choice.\n")

    conn.close()


if __name__ == "__main__":
    main()
