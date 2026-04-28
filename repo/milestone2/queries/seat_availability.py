# seat_availability.py
# from db_connection import get_connection  # shared connection helper used for local server to connect

def check_seat_availability(flight_number, date):
    # open a connection to the SQL Server database
    conn = get_connection()
    cursor = conn.cursor()  # cursor to send queries and get results

    # Use query for LEG_INSTANCE for the specific flight and date
    # and join AIRPLANE to obtain total seats for assigned plane
    # No_of_avail_seats is already stored in LEG_INSTANCE from given schema
    # The ? placeholders are interacted with by pyodbc to fill them
    cursor.execute("""
        SELECT
            a.Total_no_of_seats,   -- max seats that airplane can hold
            li.No_of_avail_seats   -- seats not being used on this specific flight and date
        FROM LEG_INSTANCE li
        JOIN AIRPLANE a ON li.Airplane_id = a.Airplane_id
        WHERE li.Flight_number = ? AND li.Date = ?
    """, (flight_number, date))  # pyodbc swaps puts these values in the '?' respectively

    row = cursor.fetchone()  # we only expect one result (one flight instance per flight + date)
    conn.close()             # always close the connection when done

    # if nothing returns, then flight DNE on specified date
    if not row:
        print(f"No flight number {flight_number} was found on {date}.")
        return

    # calc seats taken by subtracting available seats from total amount of seats
    total = row.Total_no_of_seats
    available = row.No_of_avail_seats
    taken = total - available  # derived value of taken seats

    # print reseults
    print(f"\nSeat Availability for Flight {flight_number} on {date}:") # Prepare to print info
    print("-" * 32) # Construct table for readability
    print(f"Total seats   : {total}")
    print(f"Seats taken   : {taken}")
    print(f"Available     : {available}")
    print("The specified flight is full." if available == 0 else "Seats are available on the specified flight.")