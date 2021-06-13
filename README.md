# Assignment 1

# Virtual environment and dependency management

We use poetry (https://python-poetry.org/docs/) to manage our project's packaging and dependency.

1. Install poetry:

osx / linux / bashonwindows install instructions
```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```
windows powershell install instructions
```bash
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
```
2. Install dependencies
```bash
source $HOME/.poetry/env
```
```bash
poetry install
```
3. Activate virtual environment:
```bash
poetry shell
```
4. Run the scripts like usual in the right folder:

Go to ./src to run client_console.py: See Usage

Go to ./src to run fastapi:
```bash
uvicorn main:app --reload
```
Go to ./tests to run pytest:
```bash
pytest
```

## Description

Contained is our MPCS reservation management system. 

## Usage and How it Works
Run out of src/ uvicorn main:app --reload and uncomment/change the server location if you want to run locally

If not you can run the program and it will try to interact with our linux machine.

### client_console - is our command line interface that prompts the user to input commands.

The console begins requesting a login, the programs starts with a default user that has the details

-- username: Manager 

-- password: admin

follow the prompted inputs to interact with the program

The manager must create new clients/users if they wish to make bookings for those parties.

All dates should be input in "YYYY-MM-DD" form and all times should be input as 24hr times ex. 1:00 PM = 13:00

 list of request options  
  - workshop 1-4 ex. workshop1 or workshop2
  - mini microvac 1-2 ex. mini microvac1
  - irradiator 1-2 ex. irradiator1
  - polymer extruder ex. polymer extruder1
  - high velocity crusher
  - 1.21 gigawatt lighting harvester

If you wish to disable client logins at runtime run the file with the command args --allow_logins n

If you wish to run the program allowing for remote hold request to be place use command args --allow_holds y

### main.py - our FastAPI app file

This is our FastAPI app that listens for requests and sends calls to our database.

example to run

run out of src/
uvicorn main:app --reload


### api_lite.py - our database and logic

This is our business logic handles queries and that stores reservations in the reservations table and store our space object data in the spaces table.

### specialized_client.py 
Our command line interface for the specialized clients:

Has two users:

Spencer, password: 123

Peter, password: 123

Can follow this command line format when making inputs: 
"Enter client name: "
"Enter request (eg: workshop1): "
"Enter start_date (YYYY-MM-DD): "
"Enter start_time (HH:MM): "
"Enter end_time (HH:MM): "

## Tests

To run our tests you can run pytest out of the /tests directory or run python -m pytest ../tests out of the /src directory

To run an indiviual test file you can run pytest --filename ex. pytest test_api.py

## Docs

you can view FastAPI swagger docs by navigating to the server and the "http://linux3.cs.uchicago.edu:51223"/docs endpoint

details of the API can be found in the Api.pdf file

## Notes/Features To Point Out

-- New toggle Dashboard for admin

-- Dynamic toggle of client login and add funds

-- New clientside validation for inputs (role,time,request,funds)

-- New console tests

-- New hold functionality

-- Improved information output

-- Made sure client info follows name changes

-- Better error handling

-- Seperate cancelled reservations from reservations and transactions













