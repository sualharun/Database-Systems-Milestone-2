# CS-4347 Database Systems — Airport Management System

Team project implementing an Airport Management System using Python + Microsoft SQL Server.

## Project Structure

```
├── milestone1/
│   └── setup_m1.sql        # Table creation + CSV data import
│
├── milestone2/
│   ├── MileStone2_combined.py   # Main command-line application
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
- SQL Server (mssql) for VS code (most recent)

FILES TO RUN: 
`milestone1/setup_m1.sql`
`milestone2/MileStone2_combined.py`

SETUP:
- setup database using setup_m1.sql
- then run MileStone2_combined.py
  
  `python3 milestone2/MileStone2_combined.py`

  (make sure your cmd prompt is in the same directory as where you put milestone2)


The program itself will direct you how to use it; choose a menu item and follow the instructions. 
You can also run the functions from cmd prompt directly. 
