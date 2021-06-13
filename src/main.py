import sys
import atexit

from fastapi import FastAPI, Response
from typing import Optional

sys.path.append('../Database')
import api_lite as api
from models import Item, Client, Login, Hold

app = FastAPI()
api.db = api.open_db()

admin_args = {"name":"Manager","password":"admin","status":"active","balance":0,"role":"admin"}
team1_args = {"name":"team1","password":"password1","status":"active","balance":0,"role":"hold_admin"}
team2_args = {"name":"team2","password":"password2","status":"active","balance":0,"role":"hold_admin"}
team4_args = {"name":"team4","password":"password4","status":"active","balance":0,"role":"hold_admin"}
team5_args = {"name":"team5","password":"password5","status":"active","balance":0,"role":"hold_admin"}
spencer_args = {"name":"Spencer","password":"123","status":"active","balance":0,"role":"hold_admin"}
peter_args = {"name":"Peter","password":"123","status":"active","balance":0,"role":"hold_admin"}

default_admin = api.create_client(admin_args)
team1 = api.create_client(team1_args)
team2 = api.create_client(team2_args)
team4 = api.create_client(team4_args)
team5 = api.create_client(team5_args)
spencer = api.create_client(spencer_args)
peter = api.create_client(peter_args)

@app.get("/")
async def read_root():
    return {"message": "Welcome to MPCS Reservations"}

@app.put("/login")
async def app_login(login: Login):
    args = login.dict()
    user = args['username']
    password = args['password']
    result = api.check_login(user,password)

    if result:
        return {"Result": result}
    else:
        return {"Result": "Not Found"}

@app.post("/hold")
async def post_hold(hold: Hold):
    args = hold.dict()
    result = api.create_hold(args)

    if result:
        return {
                "success": True,
                "message": "Your hold was placed",
                "facility_name": "Team_3_Chicago"
                }
    else:
        return {
                "success": False,
                "message": "Your hold could not be placed",
                }

@app.post("/hold/charge")
async def post_hold_charge(item:Item):
    args = item.dict()
    result = api.charge_hold(args)

    if result:
        return {
                "Status": ["Reservation Held"],
                "ID": [f'{result.id}'],
                "Date": [f'{result.st_dt}'],
                "Cost": [f'{result.cost}'],
                "Facility": [f'{result.location}']
                }
    else:
        return {"Status": ["Your Reservation is Unavailable"]}

@app.delete("/hold")
async def delete_hold(hold: Hold):
    args = hold.dict()
    result = api.delete_hold(args)

    if result:
        return {
                "success": True,
                "message": "Your hold was deleted",
                }
    else:
        return {
                "success": False,
                "message": "Your hold could not be deleted",
                }

@app.get("/hold")
async def get_hold_list():
    hold_list = api.get_holds()
    if hold_list:
        return {'holds_lst': hold_list}
    else:
        return{'holds_lst': ['No holds']}


@app.get("/reservations")
async def get_reservations_list():
    res_list = api.list_all_reservations()
    if res_list:
        return {'ids_lst': res_list}
    else:
        return{'ids_lst': ['No Reservations']}


@app.post("/reservations")
async def post_reservation(item: Item):
    args = item.dict()
    result = api.create_res(args)

    if result == "Please Create Client":
        return {"Status":[result]}

    if result == "Your booking ability is not active":
        return {"Status":[result]}
        
    if result:
        return {
                "Status": ["Reservation Confirmed"],
                "ID": [f'{result.id}'],
                "Date": [f'{result.st_dt}'],
                "Cost": [f'{result.cost}'],
                "Facility": [f'{result.location}']
                }
    else:
        return {"Status": ["Your Reservation is Unavailable"]}

@app.delete("/reservations/{res_id}")
async def delete_reservation(res_id,response: Response):
    result = api.delete_res(res_id)
    
    if result:
        return{'Message': ['The reservation was cancelled']}
    else:
        return{'Message': ['No reservations under that id']}

@app.put("/reservations/{res_id}")
async def modify_reservation(res_id,item: Item):
    args = item.dict()
    result = api.modify_reservation(res_id,args)

    if result:
        return {
                "Status": ["Reservation Modified"],
                "ID": [f'{result.id}'],
                "Date": [f'{result.st_dt}'],
                "Cost": [f'{result.cost}'],
                "Facility": [f'{result.location}']
                }
    else:
        return {"Status": ["Your Reservation is Unavailable"]}

@app.get("/reservations/{res_id}")
async def get_reservation(res_id):

    result= api.get_reservation(res_id)

    if result:
        return {
                "Status": [f'{result.status}'],
                "ID": [f'{result.id}'],
                "Date": [f'{result.st_dt}'],
                "Cost": [f'{result.cost}'],
                "Refund": [f'{result.refund}'] 
                }
    else:
        return{'Message': ['No reservations under that id']}


@app.get("/clients")
async def get_clients_list():
    client_list = api.list_all_clients()
    if client_list:
        return {'ids_lst': client_list}
    else:
        return{'ids_lst': ['No clients']}

@app.get("/clients/{client}")
async def get_client_balance(client,balance:Optional[str] = None):
    if balance == "true":
        result = api.get_client_balance(client)
    if result:
        return {'Client': [result[0]],
                'Balance': [result[1]]}
    else:
        return{'Message': ['No client']}


@app.post("/clients")
async def post_client(client: Client):
    args = client.dict()
    result = api.create_client(args)

    if result:
        return {"Status": ["Client Created"]}
    else:
        return {"Status": ["Cannot Create This Client"]}

@app.put("/clients/{client}")
async def update_client(client,new_name:Optional[str] = None,add:Optional[float] = None,
                        sub:Optional[float] = None,status:Optional[str] = None):

    result = False

    if new_name and not (add or sub or status):
        result = api.client_edit_name(client,new_name)

    if add and not (new_name or sub or status):
        result = api.client_add_balance(client,add)

    if sub and not (new_name or add or status):
        result = api.client_sub_balance(client,sub)

    if status and not (new_name or add or sub):
        if status == "Activate":
            result = api.client_activate(client)
        
        if status == "Deactivate":
            result = api.client_deactivate(client)

    if result:
        return {"Message": ["Client updated"]}
    else:
        return {"Message": ["Client cannot be updated"]}



@app.get("/list/all/{lst_type}")
async def list_all_request(lst_type, client:Optional[str] = None):
    
    if lst_type == "client":
        if client:
            result = api.list_all_client_reservations(client)
            if result:
                return {
                        "Reservations": result['reservations'],
                        "Totals": result['totals'],
                        "Refunds": result['refunds'],
                        "Facility": result['facility'],
                        "Status": result['status']
                        }
            else:
                return{"Message":["No results found"]}
        else:
            return {"Message":["No client was listed"]}

    if lst_type == "transactions":
        result = api.list_all_transactions()
        if result:
            return {
                    "Reservations": result['reservations'],
                    "Totals": result['totals'],
                    "Refunds": result['refunds'],
                    "Facility": result['facility'],
                    "Status": result['status']

                    }
        else:
            return{"Message":["No Results Found"]}
        


@app.get("/list/range/{lst_type}/{start_dt}/{end_dt}")
async def list_range_request(lst_type, start_dt, end_dt,client:Optional[str] = None):

    if lst_type == "client":
        if client:
            result = api.list_client(client,start_dt,end_dt)
            if result:
                return {"result_list": result}
            else:
                return{"Message":["No Results Found"]}
        else:
            return {"Message":["No Client was listed"]}

    if lst_type == "transactions":
        result = api.list_transactions(start_dt,end_dt)
        if result:
            return {
                    "Reservations": result['reservations'],
                    "Totals": result['totals'],
                    "Refunds": result['refunds'],
                    "Facility": result['facility'],
                    "Status": result['status']

                    }
        else:
            return{"Message":["No Results Found"]}
    
    if lst_type == "reservations":
        result = api.list_reservations(start_dt,end_dt)
        if result:
            return {"Reservations": result}
        else:
            return{"Message":["No Results Found"]}



if __name__ == '__main__':
    atexit.register(api.db_cleanup)
