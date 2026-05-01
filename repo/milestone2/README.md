===================================================================================
### CS 4347 Database Systems 4/30/2026
### Professor: Chris Davis
### Project Members: Sual Harun, Carla Amelie, Jason Kam, Miles Ratner, Daniel Fox
===================================================================================
### Airport Management Systems Milestone 2 README.md

## Overview
Command-line Python application connecting to Microsoft SQL Server in Docker, implementing all Milestone
2 functional requirements.

-----------------------------------------
## Requirements                Version
- *Python*                     3.9+
- *pyodbc*                     5.0+
- *ODBC Driver for SQL Server* 18
- *Docker Desktop*             Latest
-----------------------------------------

### SETUP INSTRUCTIONS ###
## Step 1 — Install Docker Desktop
Download from https://www.docker.com/products/docker-desktop and make sure it is running.

## Step 2 — Start SQL Server in Docker
*prompt:*
docker run -e ACCEPT_EULA=Y -e SA_PASSWORD=StrongPass123 -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2022-latest

# Wait 30 seconds, then create the database:
*prompt:*
docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost,1433 -U sa -P StrongPass123 -No -Q "CREATE DATABASE AirportDB"

## Step 3 — Load the Data
# Copy CSVs from Canvas into Docker (replace ~/Downloads with your CSV folder):
*prompt:*
docker cp ~/Downloads/. sqlserver:/var/opt/mssql/import/

# Copy and run the Milestone 1 setup script:
*prompt:*
docker cp setup_m1.sql sqlserver:/var/opt/mssql/import/setup_m1.sql
docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost,1433 -U sa -P StrongPass123 -No -d AirportDB -i /var/opt/mssql/import/setup_m1.sql

## Step 4 — Apply Milestone 2 Schema
*prompt:*
docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost,1433 -U sa -P StrongPass123 -No -d AirportDB -Q "DROP TABLE IF EXISTS SEAT; CREATE TABLE SEAT (Airplane_id VARCHAR(20) NOT NULL, Seat_no VARCHAR(5) NOT NULL, Date DATE NOT NULL, Leg_no INT NOT NULL, Customer_name VARCHAR(100) NULL, Cphone VARCHAR(20) NULL, PRIMARY KEY (Airplane_id, Seat_no, Date, Leg_no), FOREIGN KEY (Airplane_id) REFERENCES AIRPLANE(Airplane_id));"

## Step 5 — Install Python Dependencies
*prompt:*
pip3 install pyodbc
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install msodbcsql18

## Step 6 — Run the Application
*prompt:*
python3 airport.py

-----------------------------------------

## Features
1. **Travel Itinerary Search** — direct and one-stop flights by city name or airport code
2. **Flight Details by Number** — all legs, routes, times, and fares
3. **Aircraft Utilization Report** — every airplane with total flights in a date range
4. **Seat Availability Check** — total seats vs bookings for a specific flight and date
5. **Passenger Itinerary Retrieval** — all booked legs for a customer by name

## Notes
- SQL Server password: StrongPass123
- SQL Server runs on localhost port 1433 inside Docker
- Docker Desktop must be running before launching the app
- The Milestone 1 CSV files from Canvas are required for data

## Third-Party Modules
pyodbc — Python ODBC bridge for SQL Server connectivit

## Quick start
1. Install Docker Desktop and start it
2. Run SQL Server in Docker
3. Load data using milestone1/setup_m1.sql
4. pip3 install pyodbc
5. python3 milestone2/airport.py