import datetime as dt
import regex as re

class Interface:
    """ Interface handler for Reservation System """ 
    
    admin_actions = {"1": "Book Reservation", "2": "Cancel Reservation", "3": "Modify Reservation",
                     "4": "Get Reservation Details", "5": "List Clients", "6": "List Reservations", 
                     "7": "List Transactions", "8":"Create Client", "9":"Edit Client","10":"Dashboard"}
    
    client_actions = {"1": "Book Reservation", "2": "Cancel Reservation", "3": "Modify Reservation",
                     "4": "List Reservations", "5": "List Transactions", "6": "Show Balance", 
                     "7": "Add Balance", "8":"Edit Name"}
    
    equipment_lst = ['workshop1','workshop2', 'workshop3','workshop4','mini microvac1', 'mini microvac2',
                     'irradiator1', 'irradiator2', 'polymer extruder1', 'polymer extruder2',
                     'high velocity crusher', '1.21 gigawatt lightning harvester']

    def __init__(self):
        self.welcome = "Welcome to MPCS Reservation System!"
        self.again = 'y'
        self.user = "admin"
        self.role = "admin"
        self.admin_choice_prompts = {"Book Reservation":self.prompt_make,
                                     "Cancel Reservation":self.prompt_cancel,
                                     "Modify Reservation":self.prompt_modify,
                                     "Get Reservation Details":self.prompt_get_res,
                                     "List Clients":self.prompt_list_clients,
                                     "List Reservations All":self.prompt_list_res_all,
                                     "List Reservations Client":self.prompt_list_res_client,
                                     "List Reservations Range":self.prompt_list_res_range,
                                     "List Transactions All":self.prompt_list_trans_all,
                                     "List Transactions Client":self.prompt_list_trans_client,
                                     "List Transactions Range":self.prompt_list_trans_range,
                                     "Create Client":self.prompt_create_client,
                                     "Edit Name": self.prompt_edit_client,
                                     "Add Balance":self.prompt_add_funds,
                                     "Activate":self.prompt_activate,
                                     "Deactivate":self.prompt_deactivate,
                                     "Toggle Funds":self.prompt_toggle,
                                     "Toggle Login":self.prompt_toggle,
                                     "Show Toggles":self.prompt_show_toggles
                                     }
        
        self.client_choice_prompts = {"Book Reservation":self.prompt_make,
                                     "Cancel Reservation":self.prompt_cancel,
                                     "Modify Reservation":self.prompt_modify,
                                     "List Reservations":self.prompt_list_res_client,
                                     "List Transactions":self.prompt_list_trans_client,
                                     "Show Balance":self.prompt_show_funds,                                      
                                     "Add Balance":self.prompt_add_funds,     
                                     "Edit Name":self.prompt_edit_client                                
                                     }        


    def prompt_loop(self,options):
        print('\n')
        for i in range(1,len(options)+1):
            print(f'{i}.{options[i-1]}')
        
        while True:
            choice = input("Enter a number: ")
            try:
                if int(choice) in range(1,len(options)+1):
                    break
                else:
                    print(f'Please chose 1-{len(options)}!')
                    continue
            except:
                print(f'Please chose 1-{len(options)}!')
                continue
        
        return options[int(choice)-1]
    
        #prompt for login
    def prompt_login(self):

        username = input("Please Input A Username: ")
        password = input("Please Input A Password: ")
        return username,password

    #script for for admin
    def prompt_admin(self):
        print("Select which action would you like to perform: ")
        
        for i in range(1,11):
            print(f'{i}.{self.admin_actions[str(i)]}')
            
        while True:
            choice = input("Enter a number: ")
            try:
                if int(choice) in range(1,11):
                    break
                else:
                    print("Please choose 1-10!")
                    continue
            except:
                 print("Please choose 1-10!")
                 continue
        
        if int(choice) in [6,7]:
            sub_choice = self.prompt_loop(['List All','List for a client','List for a date range'])
            
            if sub_choice == "List All":
                return self.admin_actions[choice] + ' All'
            
            if sub_choice == "List for a client":
                return self.admin_actions[choice] + ' Client'

            if sub_choice == "List for a date range":
                return self.admin_actions[choice] + ' Range'

        if int(choice) == 9:
            sub_choice = self.prompt_loop(['Edit Name','Add Balance','Activate','Deactivate'])
            
            if sub_choice == "Edit Name":
                return "Edit Name"
            
            if sub_choice == "Add Balance":
                return "Add Balance"

            if sub_choice == "Activate":
                return "Activate"

            if sub_choice == "Deactivate":
                return "Deactivate"        

        if int(choice) == 10:
            sub_choice = self.prompt_loop(['Toggle Funds','Toggle Login','Show Toggles'])
            
            if sub_choice == "Toggle Funds":
                return "Toggle Funds"
            
            if sub_choice == "Toggle Login":
                return "Toggle Login"

            if sub_choice == "Show Toggles":
                return "Show Toggles"         

        return self.admin_actions[choice]
 
    def prompt_client(self):
        print("Select which action would you like to perform:")
        
        for i in range(1,9):
            print(f'{i}.{self.client_actions[str(i)]}')
        
        while True:
            choice = input("Enter a number:")
            try:
                if int(choice) in range(1,10):
                    break

                else:
                    print("Please choose 1-8!")
                    continue
            except:
                 print("Please choose 1-8!")
                 continue
            
        return self.client_actions[choice]
       

    #prompt if the user wants to continue
    def prompt_more(self):
        while True:
            choice = input("Would you like to continue? [y/n] ")
            if choice in ['y','n']:
                break
            else:
                print("Please choose y or n")
                continue
        self.again = choice   


    # needs error handling and client exist check for admin
    def prompt_make(self):
        data = {}

        if self.role == "admin":
            client = input("Enter the client name: ")
            data['client'] = client

        else:
            data['client'] = self.user

        request = self.valid_request()
        data['request'] = request
        
        create_date = input("Enter what day you are making this reservation: ")
        create_date = self.valid_date(create_date)
        data['create_date'] = create_date
        
        start_date = input("Enter what day this reservations is for: ")
        start_date = self.valid_date(start_date)
        data['start_date'] = start_date

        res_start = input("Enter what time the reservation starts: ")
        res_start = self.valid_time(res_start)
        data['res_start'] = res_start

        res_end = input("Enter what time the reservation ends: ")
        res_end = self.valid_time(res_end)
        data['res_end'] = res_end

        return [data]


    def prompt_cancel(self):
        reservation_id = input("Enter ID of reservations you would like to cancel: ")
        return reservation_id

    def prompt_modify(self):
        data = {}
        
        reservation_id = input("Enter ID of reservations you would like to modify: ")
        res_id = reservation_id

        if self.role == "admin":
            client = input("Enter the client name: ")
            data['client'] = client

        else:
            data['client'] = self.user

        request = self.valid_request()
        data['request'] = request
        
        create_date = input("Enter what day you are making this reservation: ")
        create_date = self.valid_date(create_date)
        data['create_date'] = create_date
        
        start_date = input("Enter what day this reservations is for: ")
        start_date = self.valid_date(start_date)
        data['start_date'] = start_date

        res_start = input("Enter what time the reservation starts: ")
        res_start = self.valid_time(res_start)
        data['res_start'] = res_start

        res_end = input("Enter what time the reservation ends: ")
        res_end = self.valid_time(res_end)
        data['res_end'] = res_end

        return [res_id,data]

    def prompt_get_res(self):
        reservation_id = input("Enter ID of reservations you would like to review: ")
        return reservation_id

    def prompt_list_clients(self):
        return None

    def prompt_list_res_all(self):
        return None

    def prompt_list_res_client(self):
        if self.role == "admin":
            client_name = input("Enter Client Name: ")
        else:
            client_name = self.user
        return client_name

    def prompt_list_res_range(self):
        start_date = input("Enter start date: ")
        start_date = self.valid_date(start_date)
        end_date = input("Enter end date: ")
        end_date = self.valid_date(end_date)
        return [start_date,end_date]
    
    def prompt_list_trans_all(self):
        return None

    def prompt_list_trans_client(self):
        if self.role == "admin":
            client_name = input("Enter Client Name: ")
        else:
            client_name = self.user
        return client_name


    def prompt_list_trans_range(self):
        start_date = input("Enter start date: ")
        start_date = self.valid_date(start_date)
        end_date = input("Enter end date: ")
        end_date = self.valid_date(end_date)
        return [start_date,end_date]
    
    def prompt_create_client(self):
        data = {}
        
        client_name = input("Enter Client Name: ")
        data["name"] = client_name
        
        password = input("Enter a password: ")
        data['password'] = password

        data['status'] = "Active"

        balance = input("Enter a starting balance: ")
        balance = self.valid_funds(balance)
        data['balance'] = balance

        role = self.valid_role()
        data['role'] = role
        
        return data

    def prompt_edit_client(self):
        
        if self.role == "admin":
            client_name = input("Enter the client name: ")

        else:
            client_name = self.user

        new_name = input("Enter new name:")

        return [client_name,new_name]
    
    def prompt_get_balance(self):
        return None

    def prompt_add_funds(self):
        if self.role == "admin":
            client_name = input("Enter the client name: ")

        else:
            client_name = self.user    
        
        funds = input("Enter amount you'd like to add: ")
        funds = self.valid_funds(funds)
        
        return [client_name,funds]

    def prompt_show_funds(self):
        if self.role == "admin":
            client_name = input("Enter the client name: ")

        else:
            client_name = self.user
        
        return client_name    


    def prompt_activate(self):
        client_name = input("Enter Client Name: ")
        return client_name
    
    def prompt_deactivate(self):
        client_name = input("Enter Client Name: ")
        return client_name

    def prompt_output(self):
        while True:
            choice = input("Would you like to output to csv? [y/n] ")
            if choice in ['y','n']:
                break
            else:
                print("Please choose y or n")
                continue
        return choice
    
    def prompt_toggle(self):
        while True:
            choice = input("What would you like to set the toggle to? [y/n] ")
            if choice in ['y','n']:
                break
            else:
                print("Please choose y or n")
                continue
        return choice    

    def prompt_show_toggles(self):
        return None

    def valid_date(self,date):
        valid = self.check_date(date)

        if valid:
            return date
        else:
            new_input = input('Enter a date '"YYYY-MM-DD"': ')
            return self.valid_date(new_input)

    def valid_time(self,time):
        valid = self.check_time(time)
        if valid:
            return time
        else:
            new_input = input('Enter a military time: ')
            return self.valid_time(new_input)
    
    
    def valid_funds(self,number):
        try:
            valid = self.check_funds(number)
            if valid:
                return number
            else:
                funds = input("Enter a round amount 1-25000: ")
                return self.valid_funds(funds)
        except:
                funds = input("Enter a round amount 1-25000: ")
                return self.valid_funds(funds)

    def valid_request(self):
        while True:
            request = input("Enter what you would like to book: ")
            valid = self.check_request(request)
            if valid:
                break
            else:
                print("Please choose a valid machine")
                continue
        return request 


    def valid_role(self):
        while True:
            request = input("Enter a role: ")
            valid = self.check_role(request)
            if valid:
                break
            else:
                print("Please choose client or admin")
                continue
        return request 

    def check_date(self,date):
        try:
            dt_date = dt.datetime.strptime(date,"%Y-%m-%d").date()
            if dt_date:
                return True
        except:
            return False

    def check_funds(self,number):
        try:
            return int(number) > 0 and int(number) < 25000
        except:
            return False
    def check_request(self,request):
        return request in self.equipment_lst

    def check_time(self,time):
        pattern = re.search(r"[0-1]\d:[0,3]0", time)
        if pattern:
            return True
        else:
            return False 

    def check_role(self,role):
        return role in ["client","admin"]