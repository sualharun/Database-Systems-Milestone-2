DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql += 'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id))
    + '.' + QUOTENAME(OBJECT_NAME(parent_object_id))
    + ' DROP CONSTRAINT ' + QUOTENAME(name) + ';'
FROM sys.foreign_keys;
EXEC sp_executesql @sql;

DROP TABLE IF EXISTS SEAT;
DROP TABLE IF EXISTS LEG_INSTANCE;
DROP TABLE IF EXISTS CAN_LAND;
DROP TABLE IF EXISTS FARE;
DROP TABLE IF EXISTS FLIGHT_LEG;
DROP TABLE IF EXISTS FLIGHT;
DROP TABLE IF EXISTS AIRPLANE;
DROP TABLE IF EXISTS AIRPLANE_TYPE;
DROP TABLE IF EXISTS AIRPORT;

CREATE TABLE AIRPORT (
    Airport_code CHAR(3) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    City VARCHAR(50) NOT NULL,
    State VARCHAR(5) NOT NULL
);

CREATE TABLE AIRPLANE_TYPE (
    Type_name VARCHAR(10) PRIMARY KEY,
    Company VARCHAR(50) NOT NULL,
    Max_seats INT NOT NULL
);

CREATE TABLE AIRPLANE (
    Airplane_id VARCHAR(20) PRIMARY KEY,
    Total_no_of_seats INT NOT NULL,
    Type_name VARCHAR(10) NOT NULL,
    FOREIGN KEY (Type_name) REFERENCES AIRPLANE_TYPE(Type_name)
);

CREATE TABLE FLIGHT (
    Number INT PRIMARY KEY,
    Airline VARCHAR(50) NOT NULL,
    Weekdays VARCHAR(7)
);

CREATE TABLE FLIGHT_LEG (
    Flight_number INT NOT NULL,
    Leg_no INT NOT NULL,
    Dep_airport_code CHAR(3) NOT NULL,
    Arr_airport_code CHAR(3) NOT NULL,
    Scheduled_dep_time TIME NOT NULL,
    Scheduled_arr_time TIME NOT NULL,
    PRIMARY KEY (Flight_number, Leg_no),
    FOREIGN KEY (Flight_number) REFERENCES FLIGHT(Number),
);

CREATE TABLE FARE (
    Flight_number INT NOT NULL,
    Code VARCHAR(20) NOT NULL,
    Amount INT NOT NULL,
    Restrictions VARCHAR(200) NOT NULL,
    PRIMARY KEY (Flight_number, Code),
    FOREIGN KEY (Flight_number) REFERENCES FLIGHT(Number)
);

CREATE TABLE CAN_LAND (
    Airport_code CHAR(3) NOT NULL,
    Type_name VARCHAR(10) NOT NULL,
    PRIMARY KEY (Airport_code, Type_name),
    FOREIGN KEY (Airport_code) REFERENCES AIRPORT(Airport_code),
    FOREIGN KEY (Type_name) REFERENCES AIRPLANE_TYPE(Type_name)
);

CREATE TABLE LEG_INSTANCE (
    Flight_number INT NOT NULL,
    Leg_no INT NOT NULL,
    Date DATE NOT NULL,
    No_of_avail_seats INT NOT NULL,
    Airplane_id VARCHAR(20) NOT NULL,
    Dep_time TIME NOT NULL,
    Arr_time TIME NOT NULL,
    PRIMARY KEY (Flight_number, Leg_no, Date),
    FOREIGN KEY (Flight_number, Leg_no)
        REFERENCES FLIGHT_LEG(Flight_number, Leg_no),
    FOREIGN KEY (Airplane_id)
        REFERENCES AIRPLANE(Airplane_id)
);

CREATE TABLE SEAT (
    Airplane_id VARCHAR(20) NOT NULL,
    Seat_no VARCHAR(5) NOT NULL,
    Class   VARCHAR(20) NOT NULL, 
    PRIMARY KEY (Airplane_id, Seat_no),
    FOREIGN KEY (Airplane_id) REFERENCES AIRPLANE(Airplane_id)
);
BULK INSERT AIRPORT
FROM '/var/opt/mssql/import/AIRPORT.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');

BULK INSERT AIRPLANE_TYPE
FROM '/var/opt/mssql/import/AIRPLANE_TYPE.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');

BULK INSERT AIRPLANE
FROM '/var/opt/mssql/import/AIRPLANE.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');

BULK INSERT FLIGHT
FROM '/var/opt/mssql/import/FLIGHT.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');

BULK INSERT FLIGHT_LEG
FROM '/var/opt/mssql/import/FLIGHT_LEG.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');

BULK INSERT FARE
FROM '/var/opt/mssql/import/FARE.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');

BULK INSERT CAN_LAND
FROM '/var/opt/mssql/import/CAN_LAND.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');

BULK INSERT LEG_INSTANCE
FROM '/var/opt/mssql/import/LEG_INSTANCE.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');

SELECT TOP 10 * FROM AIRPORT;
SELECT TOP 10 * FROM AIRPLANE_TYPE;
SELECT TOP 10 * FROM AIRPLANE;
SELECT TOP 10 * FROM FLIGHT;
SELECT TOP 10 * FROM FLIGHT_LEG;
SELECT TOP 10 * FROM FARE;
SELECT TOP 10 * FROM CAN_LAND;
SELECT TOP 10 * FROM LEG_INSTANCE;