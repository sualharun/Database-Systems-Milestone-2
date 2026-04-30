import pyodbc

def get_connection():   #Make sure to update these to test it
    return pyodbc.connect(
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=localhost,1433;"
        "Database=AirportDB;"
        "UID=sa;"
        "PWD=YourPasswordHere;"
        "Encrypt=no;"
    )

def aircraft_utilization_report(start_date, end_date):
    """
    Returns a list of dictionaries:
    [
        { "Airplane_id": ..., "Type_name": ..., "Total_Flights": ... },
        ...
    ]
    """
    query = """
        SELECT 
            A.Airplane_id,
            AT.Type_name,
            COUNT(LI.Leg_no) AS Total_Flights
        FROM AIRPLANE A
        LEFT JOIN AIRPLANE_TYPE AT
            ON A.Type_name = AT.Type_name
        LEFT JOIN LEG_INSTANCE LI
            ON A.Airplane_id = LI.Airplane_id
            AND LI.Date BETWEEN ? AND ?
        GROUP BY A.Airplane_id, AT.Type_name
        ORDER BY Total_Flights DESC;
    """

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, (start_date, end_date))

    results = []
    for row in cursor.fetchall():
        results.append({
            "Airplane_id": row.Airplane_id,
            "Type_name": row.Type_name,
            "Total_Flights": row.Total_Flights
        })

    conn.close()
    return results

def print_aircraft_utilization(start_date, end_date):
    """
    Pretty-prints the Aircraft Utilization Report.
    """
    data = aircraft_utilization_report(start_date, end_date)

    print("\n=== Aircraft Utilization Report ===")
    print(f"Date Range: {start_date} → {end_date}\n")
    print(f"{'Airplane ID':<15}{'Type':<20}{'Total Flights':<15}")
    print("-" * 50)

    for row in data:
        type_name = row['Type_name'] if row['Type_name'] else "Unknown"
        print(f"{row['Airplane_id']:<15}{type_name:<20}{row['Total_Flights']:<15}")

if __name__ == "__main__":
    print_aircraft_utilization("2025-01-01", "2025-12-31")

