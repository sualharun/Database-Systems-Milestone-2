# CS-4347 Database Systems — Airport Management System (ARGON)

Team project implementing an Airport Management System using Python + Microsoft SQL Server.
This file contains the Build info, design patterns, and Quick start guide.

## Project Structure 

```
├── milestone1/
│   └── setup_m1.sql        # Table creation + CSV data import
│
├── milestone2/
│   ├── MileStone2_combined.py   # Main command-line application
|   ├── MileStone3base.py   # Main GUI aaplication
│   └── readme.md          # Build & run instructions (and design patterns)
│
└── data/
    └── (CSV files from eLearning — not committed to Git)
```
## Quick Start Guide: 
1. Ensure you have all requirments
    1. All system requirements
    2. CSV files
    3. Database created intended for said CVS files (guide for that below in How to Run section)
    4. Connnected python to said DB (change connection script in both .py files)
2. Run setup_m1.sql (to populate and create DB baed on CSV)
3. Run Milestone2_combined.py for command line functionality
4. Run Milestone3base.py for GUI functionality
       1. Once running, progress through by inputing required info (taken from CSV), hitting specialized button (if there is one) and then next
       2. You can go back if you want, but to progress you must use next 

## Design Patterns
Our Airport Management System was developed using the Python programming language with tkinter for creating a GUI interface, and pyodbc to interact with the MSSQL Server database hosted in a Docker container. We have used Docker for hosting our database since each team member will have the same configuration without needing to worry about their hardware situation. Screens are created using a stacked frame structure, and only one connection to the database is made across all screens, which made it easy for us to maintain code simplicity and distribution among team members.

Python was chosen as our language as it is a relatively simple, well-documented, and flexible language with tools and features that made integrating SQL databases relatively simple. The pyodbc tool enabled us to connect to our database, while Tkinter was used to design and build the user GUI.
    
As for the GUI itself, some of the functions required of us in the project needed to be performed in sequence, so we designed our wizard as a sequence of branching screens that can be shifted between using next and back buttons. When needed, we used radio buttons when the user needs to make a choice on which screen to traverse to next, and text entry fields to receive input from the user to check the database. The Treeview widget was used to display results of these queries. 

A standard relational schema is shown in this UML diagram:
```
AIRPLANE (Airplane_id, Type_name)
    |
    --> AIRPLANE_TYPE (Type_name, Max_seats, Weight)

AIRPLANE (Airplane_id)
    |
    --> LEG_INSTANCE (Flight_number, Leg_no, Date, Airplane_id)

FLIGHT (Number, Airline)
    |
    --> FLIGHT_LEG (Flight_number, Leg_no, Dep_airport_code, Arr_airport_code)
```

## How to Run (Build Info)

System requirements: 
- pyodbc - https://pypi.org/project/pyodbc/
      - pip3 install pyodbc
- python 3.14
- SQL Server (mssql) for VS code (most recent)
- Docker - https://www.docker.com/products/docker-desktop4
- tkinter - python GUI framework 

#### FILES TO RUN: 
    milestone1/setup_m1.sql
    milestone2/MileStone2_combined.py
    milestone2/Milestone3

BUILD INTRS:
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

##### FOR COMMAND LINE FUNCTION: 
10) Install Python dependency
    
    `pip3 install pyodbc`

12) run MileStone2_combined.py
    
    `python3 milestone2/MileStone2_combined.py`

##### FOR GUI FUNCTION:
13) Ensure you have tkinter (python) for GUI to function
14) Run Milestone3.py
    `python3 milestone2/milestone3base.py`
16) Proceed through the screen choices by providing the required information and hitting next or another specialized button to progress

    (make sure your cmd prompt is in the same directory as where you put milestone2)

The program itself will direct you how to use it; choose a menu item and follow the instructions. 
You can also run the functions from cmd prompt directly. 
