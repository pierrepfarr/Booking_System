# Reservation System

## Description

This is a simple reservation system with a command line interface that uses an API to communicate with a SQLite database. Purpose was to practice OOP, learn about API creation, and working with multiple layers.

# Usage and How it Works

## Dependencies
I am using poetry (https://python-poetry.org/docs/) to manage project packages and dependencies. Check out the lock file for further detail.

## FastAPI (main.py)
Run out of src/ uvicorn main:app --reload and uncomment/change the server location if you want to run locally

You can change the server address in actions.py

## Client_Console 

is our command line interface that prompts the user to input commands.

The console begins requesting a login, the programs starts with a default user that has the details

-- username: Manager 

-- password: admin

follow the prompted inputs to interact with the program

The manager must create new clients/users if they wish to make bookings for those parties.

All dates should be input in "YYYY-MM-DD" form and all times should be input as 24hr times ex. 1:00 PM = 13:00

 list of request options  
  - lab 1-4 ex. lab1 or lab2
  - microcentrifuge 1-2 ex. microcentrifuge1
  - irradiator 1-2 ex. irradiator1
  - polymer extruder ex. polymer extruder1
  - high velocity crusher
  - 1.21 gigawatt lighting harvester

If you wish to disable client logins at runtime run the file with the command args --allow_logins n

If you wish to run the program allowing for remote hold request to be place use command args --allow_holds y

## Database (database folder)

The business logic handles queries and that stores reservations information.

## Tests

To run the test suite

```bash
$Home/tests pytest 
```
or 

```bash
$Home/src python -m pytest 
```

## Docs

You can view FastAPI swagger docs by navigating to the server and the /docs endpoint













