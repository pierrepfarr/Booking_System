import sys
from random import choice
import json
import argparse
import pandas as pd
import datetime as dt
import regex as re
from tabulate import tabulate

from classes.interface import Interface
from actions import fetch_login, make_hold, cancel_hold
from models import Hold


team3 = {"port":"51223",
         "machine":"linux3"}


def main(logins,holds):
    if holds == "n":
        interface = Interface()
    if holds == "y":
        interface = Interface(holds=True)

    print(interface.welcome)

    username,password = interface.prompt_login()
    login_status = fetch_login(username,password).json()

    if login_status["Result"] == "Not Found":
        print("Your login was unsuccessful, please try again")
        return

    interface.role = login_status["Result"]
    interface.user = username

    if interface.role !='hold_admin':
        print("Hold_Admin role required")
        return

    while interface.again == "y":  
      if interface.role == 'hold_admin':
        choice = prompt_choice()
        hold = promp_hold_data(username,password)

        if int(choice) == 1:
            response = make_hold(hold, team3)
            if response.json()["success"] == True:
                result = response.json()
                print(result["message"])
                print(result["facility_name"])
            else:
                print("Your hold could not be placed")
        
        if int(choice) == 2:
            response = cancel_hold(hold, team3)
            if response.json()["success"] == True:
                result = response.json()
                print(result["message"])
            else:
                print("Your hold could not be deleted")
  
    print("Logging out")

def prompt_choice():
    while True:
            print(f"1. Make a hold \n2. Delete a hold\n")
            choice = input("Enter your choice: ")
            try:
                if int(choice) in range(1,3):
                    break
                else:
                    print("Please choose 1 or 2!")
                    continue
            except:
                 print("Please choose 1 or 2!")
                 continue
    return choice 

def promp_hold_data(username, password):
    client_name = input("Enter client name: ")
    request = input("Enter request (eg: workshop1): ")
    start_date = input("Enter start_date (YYYY-MM-DD): ")
    start_time = input("Enter start_time (HH:MM): ")
    end_time = input("Enter end_time (HH:MM): ")
    hold = Hold(username=username, password=password, client_name=client_name, request=request, start_date=start_date, start_time=start_time, end_time=end_time).dict()
    return hold

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interface for Booking App")
    parser.add_argument('--allow_logins', metavar='allow_logins', choices=[
                    'y','n'], help="allow logins flag")
    parser.add_argument('--allow_holds', metavar='allow_holds', choices=[
                'y','n'], help="allow holds flag")
    args = parser.parse_args()
    
    if args.allow_logins != None:
        logins_flag = args.allow_logins
    else:
        logins_flag = 'y'
    
    if args.allow_holds != None:
        holds_flag = args.allow_holds
    else:
        holds_flag = 'n'


    running = "yes"

    while running == "yes":
        main(logins=logins_flag,holds=holds_flag)
        print('\n')
        while True:
            new_login = input("Would you like to login into a new account? [y/n]: ")
            if new_login in ['y','n']:
                break
            else:
                print("Please choose y or n")
                continue
        if new_login == 'n':
            running = "no"