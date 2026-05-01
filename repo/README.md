# CS-4347 Database Systems — Airport Management System

Team project implementing an Airport Management System using Python + Microsoft SQL Server.

## Project Structure

```
├── milestone1/
│   └── setup_m1.sql        # Table creation + CSV data import
│
├── milestone2/
│   ├── airport.py          # Main command-line application
│   └── readme.md          # Build & run instructions
│
└── data/
    └── (CSV files from eLearning — not committed to Git)
```
## How to Run

System requirements: 
- pyodbc - https://pypi.org/project/pyodbc/
      - pip3 install pyodbc
- python 3.14
- SQL Server (mssql) for VS code

FILES TO RUN: 
`milestone1/setup_m1.sql`
`milestone2/MileStone2_combined.py`

SETUP:
- setup database using setup_m1.sql
- then run MileStone2_combined.py
  python3 milestone2/MileStone2_combined.py
  (make sure your cmd prompt is in the same directory as where you put milestone2)


## Milestones

### Milestone 1
Creates all database tables and imports CSV data from Canvas into SQL Server.

### Milestone 2
Command-line Python app with the following features:
1. Flight Search — Travel itinerary between two airports (direct + 1-stop)
2. Flight Search — By flight number
3. Aircraft Utilization Report
4. Seat Availability Check
5. Passenger Itinerary Retrieval ("my trips")

## Team Members
- Sual Harun
- [Add teammates]
