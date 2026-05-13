# CS-4347 Database Systems — Airport Management System

Team project implementing an Airport Management System using Python + Microsoft SQL Server.

## Project Structure

```
├── milestone1/
│   └── setup_m1.sql        # Table creation + CSV data import
│
├── milestone2/
│   ├── MileStone2_combined.py   # Main command-line application
|   ├── MileStone3.py   # Main GUI aaplication
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
- Docker - https://www.docker.com/products/docker-desktop

#### FILES TO RUN: 
    milestone1/setup_m1.sql
    milestone2/MileStone2_combined.py
    milestone2/Milestone3

SETUP:
1) Start Docker Desktop

    Make sure Docker Desktop is installed and running.

2) Start SQL Server container
   
    `docker run -e ACCEPT_EULA=Y -e SA_PASSWORD=StrongPass123 -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2022-latest`

4) Create the DB
   
    `docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost,1433 -U sa -P StrongPass123 -No -Q "CREATE DATABASE AirportDB"`

6) Load Milestone 1 data
   
    `docker cp <path_to_csv_folder>/. sqlserver:/var/opt/mssql/import/
docker cp <path_to_setup_m1.sql>/setup_m1.sql sqlserver:/var/opt/mssql/import/setup_m1.sql
docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost,1433 -U sa -P StrongPass123 -No -d AirportDB -i /var/opt/mssql/import/setup_m1.sql`

8) Apply Milestone 2 schema (SEAT table)
   
    `docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost,1433 -U sa -P StrongPass123 -No -d AirportDB -Q "DROP TABLE IF EXISTS SEAT; CREATE TABLE SEAT (Airplane_id VARCHAR(20) NOT NULL, Seat_no VARCHAR(5) NOT NULL, Date DATE NOT NULL, Leg_no INT NOT NULL, Customer_name VARCHAR(100) NULL, Cphone VARCHAR(20) NULL, PRIMARY KEY (Airplane_id, Seat_no, Date, Leg_no), FOREIGN KEY (Airplane_id) REFERENCES AIRPLANE(Airplane_id));"`

FOR COMMAND LINE FUNCTION: 
10) Install Python dependency
    
    `pip3 install pyodbc`

12) run MileStone2_combined.py
    
    `python3 milestone2/MileStone2_combined.py`
FOR GUI FUNCTION:
13) Ensure you have tkinter (python) for GUI to function
14) Run Milestone3.py
15) Proceed through the screen choices by providing the required information and hitting next or another specialized button to progress

    (make sure your cmd prompt is in the same directory as where you put milestone2)


The program itself will direct you how to use it; choose a menu item and follow the instructions. 
You can also run the functions from cmd prompt directly. 
