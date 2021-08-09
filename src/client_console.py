import sys
from random import choice
import json
import argparse
import pandas as pd
import datetime as dt
import regex as re
from tabulate import tabulate

from classes.interface import Interface
from actions import fetch_login,actions

def main(logins,funds):

    interface = Interface()

    print(interface.welcome)

    username,password = interface.prompt_login()
    login_status = fetch_login(username,password).json()

    if login_status["Result"] == "Not Found":
        print("Your login was unsuccessful, please try again")
        return

    interface.role = login_status["Result"]
    interface.user = username

    if logins == "n" and interface.role =="client":
        print("Currently in admins only mode")
        return
    
    while interface.again == "y":    
        
        if interface.role == "admin":
            print('\n')
            choice = interface.prompt_admin()
            print('\n')
            action_input = interface.admin_choice_prompts[choice]()
            if choice == "Toggle Funds":
                global funds_flag 
                if action_input == "y":
                    funds_flag = "y"
                if action_input == "n":
                    funds_flag ="n"

            elif choice == "Toggle Login":
                global logins_flag 
                if action_input == "y":
                    logins_flag = "y"
                if action_input == "n":
                    logins_flag ="n"

            elif choice == "Show Toggles":

                print(f"Allow logins: {logins_flag}")
                print(f"Allow New Funds: {funds_flag}")
            else:    
                response = actions[choice](action_input).json()
            
                if choice == "Edit Name":
                    if response["Message"] == ["Client updated"]:
                        interface.user = action_input[1]
                if choice == "Book Reservation":
                    print(action_input[1])
                    try:
                        if response["success"] == True:
                            action_input[0]['facility'] = response['facility_name']
                            response = actions["Charge Hold"](action_input[0]).json()
                    except:
                        pass
                
                print('\n')
                print(tabulate(response,headers="keys"))

        if interface.role == "client":
            print('\n')
            choice = interface.prompt_client()
            print('\n')
            if choice == "Add Balance" and funds == "n":
                print("You are currently unable to add funds")
                continue
            action_input = interface.client_choice_prompts[choice]()
            if choice == "Book Reservation":
                action_input[1] = False
            response = actions[choice](action_input).json()
            
            if choice == "Edit Name":
                if response["Message"] == ["Client updated"]:
                    interface.user = action_input[1]
            
            print('\n')
            print(tabulate(response,headers="keys"))
        
        if interface.role == "admin":
            if choice not in ["Toggle Funds","Toggle Login","Show Toggles"]:
                print('\n')
                output_choice = interface.prompt_output()
                
                if output_choice == "y":
                    df = pd.DataFrame.from_dict(response)
                    df.to_csv("output.csv")


        print('\n')
        interface.prompt_more()
    
    print("logging out")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interface for Booking App")
    parser.add_argument('--allow_logins', metavar='allow_logins', choices=[
                    'y','n'], help="allow logins flag")
    args = parser.parse_args()
    
    if args.allow_logins != None:
        logins_flag = args.allow_logins
    else:
        logins_flag = 'y'
    
    funds_flag = 'y'

    running = "yes"

    while running == "yes":
        main(logins=logins_flag,funds=funds_flag)
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