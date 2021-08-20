import datetime as dt
import requests

from requests.models import Response

server = "http://127.0.0.1:8000"

def to_dt_format(str_date):
    return dt.datetime.strptime(str_date, "%Y-%m-%d").date()

def fetch_login(username:str,password:str):
    my_data = {"username": username,
               "password": password}
    url = server + f"/login"
    response = requests.put(url,json=my_data)
    return response

def make_res(input_list:list):
    my_data = input_list[0]
    url = server + \
        f"/reservations"

    response = requests.post(url, json = my_data)
    return response

def cancel_res(res_id:str):
    url = server + \
        f"/reservations/{res_id}"
    
    response = requests.delete(url)
    return response

def modify_res(input_list:list):
    my_data = input_list[1]
    url = server + \
        f"/reservations/{input_list[0]}"

    response = requests.put(url, json = my_data)
    return response

def get_res(res_id:str):
    url = server + \
        f"/reservations/{res_id}"
    
    response = requests.get(url)
    return response

def list_all_clients(input=None):
    url = server + \
        f"/clients"
    
    response = requests.get(url)
    return response

def list_all_res(input=None):
    url = server + \
        f"/reservations"
    
    response = requests.get(url)
    return response

def list_res_client(client:str):
    url = server + \
    f"/list/all/client/?client={client}"

    response = requests.get(url)
    return response

def list_res_range(input_list:list):
    url = server + \
    f"/list/range/reservations/{input_list[0]}/{input_list[1]}"

    response = requests.get(url)
    return response

def list_all_trans(input=None):
    url = server + \
    f"/list/all/transactions"

    response = requests.get(url)
    return response

def list_trans_range(input_list:list):
    url = server + \
    f"/list/range/transactions/{input_list[0]}/{input_list[1]}"

    response = requests.get(url)
    return response

def create_client(data:dict):
    my_data = data
    url = server + \
        f"/clients/"

    response = requests.post(url, json = my_data)
    return response

def edit_client(input_list:list):
    url = server + \
        f"/clients/{input_list[0]}/?new_name={input_list[1]}"

    response = requests.put(url)
    return response

def add_funds(input_list:list):
    url = server + \
        f"/clients/{input_list[0]}/?add={input_list[1]}"

    response = requests.put(url)
    return response

def activate(client_name:str):
    url = server + \
        f"/clients/{client_name}/?status=Activate"

    response = requests.put(url)
    return response

def deactivate(client_name:str):
    url = server + \
        f"/clients/{client_name}/?status=Deactivate"

    response = requests.put(url)
    return response

def show_funds(client_name:str):
    url = server + \
        f"/clients/{client_name}/?balance=true"

    response = requests.get(url)
    return response

actions = { "Book Reservation":make_res,
            "Cancel Reservation":cancel_res,
            "Modify Reservation":modify_res,
            "Get Reservation Details":get_res,
            "List Clients":list_all_clients,
            "List Reservations All":list_all_res,
            "List Reservations Client":list_res_client,
            "List Reservations Range":list_res_range,
            "List Transactions All":list_all_trans,
            "List Transactions Client":list_res_client,
            "List Transactions Range":list_trans_range,
            "Create Client":create_client,
            "Edit Name": edit_client,
            "Add Balance":add_funds,
            "Activate":activate,
            "Deactivate":deactivate,
            "List Reservations":list_res_client,
            "List Transactions":list_res_client,
            "Show Balance":show_funds
            }