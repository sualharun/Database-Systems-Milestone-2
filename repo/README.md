# CS-4347 Database Systems — Airport Management System

Team project implementing an Airport Management System using Python + Microsoft SQL Server.

## Project Structure

```
├── milestone1/
│   └── setup_m1.sql        # Table creation + CSV data import
│
├── milestone2/
│   ├── airport.py          # Main command-line application
│   └── readme.pdf          # Build & run instructions
│
└── data/
    └── (CSV files from Canvas — not committed to Git)
```

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

## How to Run

See `milestone2/readme.pdf` for full setup instructions.

**Quick start:**
1. Install Docker Desktop and start it
2. Run SQL Server in Docker
3. Load data using `milestone1/setup_m1.sql`
4. `pip3 install pyodbc`
5. `python3 milestone2/airport.py`

## Team Members
- Sual Harun
- [Add teammates]
