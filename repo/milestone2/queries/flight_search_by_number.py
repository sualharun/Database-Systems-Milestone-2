# flight_search_by_number.py
# Sual Harun — Flight Search by Flight Number (1b)
# from db_connection import get_connection  # shared connection helper used for local server to connect

import pyodbc
import os


def get_connection():
    """
    Returns a pyodbc connection to the MS SQL Server database.
    Reads optional env vars so credentials are not hard-coded:
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


def search_flight_by_number(flight_number):
    """
    Given a flight number, return the details of that flight including
    all legs (departure/arrival airports, cities, states, scheduled times)
    and available fares.
    """
    # open a connection to the SQL Server database
    conn = get_connection()
    cursor = conn.cursor()  # cursor to send queries and get results

    # validate that flight_number is an integer
    try:
        flight_number = int(flight_number)
    except ValueError:
        print(f"Invalid flight number: '{flight_number}'. Must be an integer.")
        conn.close()
        return

    # Query FLIGHT joined with FLIGHT_LEG and AIRPORT tables
    # to get full details: airline, weekdays, and each leg's
    # departure/arrival airport codes, cities, states, and times
    cursor.execute("""
        SELECT
            f.Number,                       -- flight number (PK)
            f.Airline,                      -- airline operating the flight
            f.Weekdays,                     -- days of the week it operates
            fl.Leg_no,                      -- leg number within the flight
            dep.Airport_code AS DepCode,    -- departure airport code
            dep.City         AS DepCity,    -- departure city
            dep.State        AS DepState,   -- departure state
            arr.Airport_code AS ArrCode,    -- arrival airport code
            arr.City         AS ArrCity,    -- arrival city
            arr.State        AS ArrState,   -- arrival state
            fl.Scheduled_dep_time,          -- scheduled departure time
            fl.Scheduled_arr_time           -- scheduled arrival time
        FROM FLIGHT f
        JOIN FLIGHT_LEG fl ON fl.Flight_number = f.Number
        JOIN AIRPORT dep   ON dep.Airport_code = fl.Dep_airport_code
        JOIN AIRPORT arr   ON arr.Airport_code = fl.Arr_airport_code
        WHERE f.Number = ?
        ORDER BY fl.Leg_no
    """, (flight_number,))  # pyodbc swaps the ? with the flight_number value

    rows = cursor.fetchall()  # fetch all matching leg rows

    # if nothing returns, the flight number does not exist
    if not rows:
        print(f"\nNo flight found with number {flight_number}.")
        conn.close()
        return

    # print flight header info (same across all legs)
    print(f"\nFlight {rows[0].Number} — {rows[0].Airline}")
    print(f"Operates on weekdays: {rows[0].Weekdays or 'daily'}")
    print("-" * 60)

    # print each leg's route details
    for r in rows:
        print(f"  Leg {r.Leg_no}: "
              f"{r.DepCode} ({r.DepCity}, {r.DepState}) {r.Scheduled_dep_time}"
              f"  ->  "
              f"{r.ArrCode} ({r.ArrCity}, {r.ArrState}) {r.Scheduled_arr_time}")

    # also query the FARE table for available fare options on this flight
    cursor.execute("""
        SELECT
            Code,           -- fare code (e.g. 'Y', 'B', 'F')
            Amount,         -- fare price in dollars
            Restrictions    -- any restrictions on the fare
        FROM FARE
        WHERE Flight_number = ?
        ORDER BY Amount
    """, (flight_number,))

    fares = cursor.fetchall()

    if fares:
        print(f"\nAvailable fares:")
        for fare in fares:
            print(f"  [{fare.Code}]  ${fare.Amount:,.0f}  —  {fare.Restrictions}")

    conn.close()  # always close the connection when done


# allow running this module directly from the command line
if __name__ == "__main__":
    flight_num = input("Enter flight number: ").strip()
    search_flight_by_number(flight_num)
