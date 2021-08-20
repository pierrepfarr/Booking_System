import sys
import pytest
import json

from fastapi.testclient import TestClient

sys.path.append('../src')
import database as api
from main import app
sys.path.append('../src/classes')
from reservation import Reserve

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message":"Welcome to MPCS Reservations"}

def test_get_reservations_list_empty_lst(mocker):
    # mocker.patch('Database.api_lite')
    spy = mocker.spy(api, 'list_all_reservations')
    response = client.get("/reservations")
    print(response.json())
    assert response.status_code == 200
    assert spy.call_count == 1

def test_get_reservations_list_nonempty_lst(mocker):
    expected = ['res1']
    mocker.patch(
        'api_lite.list_all_reservations', 
        return_value=expected
    )
    response = client.get("/reservations")
    assert response.json() == {'ids_lst': expected}
    assert response.status_code == 200

def test_post_reservation(mocker):
    expected = Reserve('Pierre','workshop1','2021-04-08','2021-04-10','13:00','14,00')
    expected.id = 'test'
    mocker.patch(
        'api_lite.create_res', 
        return_value=expected
    )       
    my_data = {
            "client": 'Pierre',
            "request": 'workshop1',
            "create_date": '2021-04-08',
            "start_date": '2021-04-10',
            "res_start": '13:00',
            "res_end": '14:00'}

    my_data = json.dumps(my_data)
    response = client.post("/reservations",data=my_data)
    assert response.status_code == 200
    assert response.json()['Status'] == ["Reservation Confirmed"]
    assert response.json()['Cost'] == ['99']

def test_delete_reservations(mocker):
    expected = True
    mocker.patch(
        'api_lite.delete_res', 
        return_value=expected
    )   
    response = client.delete("/reservations/1") 
    assert response.json()['Message'] == ['The reservation was cancelled']

def test_modify_reservations(mocker):
    expected = Reserve('Pierre','workshop2','2021-04-08','2021-04-10','13:00','14,00')
    expected.id = 'test'
    mocker.patch(
        'api_lite.modify_reservation', 
        return_value=expected
    )       
    my_data = {
            "client": 'Pierre',
            "request": 'workshop2',
            "create_date": '2021-04-08',
            "start_date": '2021-04-10',
            "res_start": '13:00',
            "res_end": '14:00'}

    my_data = json.dumps(my_data)
    response = client.put("/reservations/1",data=my_data)
    assert response.status_code == 200
    assert response.json()['Status'] == ["Reservation Modified"]
    assert response.json()['Cost'] == ['99']

def test_get_reservation(mocker):
    expected = Reserve('Pierre','workshop1','2021-04-08','2021-04-10','13:00','14,00')
    expected.id = 'test'
    expected.refund = '0'
    
    mocker.patch(
        'api_lite.get_reservation', 
        return_value=expected
    )  
    response = client.get("/reservations/1")
    assert response.status_code == 200
    assert response.json()['Status'] == ["Current"]
    assert response.json()['ID'] == ["test"]
    assert response.json()['Cost'] == ['99']

def test_get_reservation_fail(mocker):
    expected = False
    
    mocker.patch(
        'api_lite.get_reservation',
        return_value=expected
    )  
    response = client.get("/reservations/1")
    assert response.status_code == 200
    assert response.json()['Message'] == ["No reservations under that id"]

def test_get_clients_list(mocker):
    expected = ['test_client']
    
    mocker.patch(
        'api_lite.list_all_clients', 
        return_value=expected
    )  
    response = client.get("/clients")
    assert response.status_code == 200
    assert response.json()['ids_lst'] == ['test_client']

def test_get_clients_list_empty(mocker):
    expected = []
    
    mocker.patch(
        'api_lite.list_all_clients', 
        return_value=expected
    )  
    response = client.get("/clients")
    assert response.status_code == 200
    assert response.json()['ids_lst'] == ['No clients']

def test_get_client_balance(mocker):
    expected = ['test',2000]
    
    mocker.patch(
        'api_lite.get_client_balance', 
        return_value=expected
    )  
    response = client.get("/clients/1/?balance=true")
    assert response.status_code == 200
    assert response.json()['Client'] == ['test']
    assert response.json()['Balance'] == [2000]

def test_get_client_balance_fail(mocker):
    expected = False
    
    mocker.patch(
        'api_lite.get_client_balance', 
        return_value=expected
    )  
    response = client.get("/clients/1/?balance=true")
    assert response.status_code == 200
    assert response.json()['Message'] == ['No client']

def test_post_client(mocker):
    expected = True
    mocker.patch(
        'api_lite.create_client', 
        return_value=expected
    )  
    my_data = { "name":"Pierre",
                "password":"test",
                "status":"active",
                "balance":2000,
                "role":"client"
                }
    my_data = json.dumps(my_data)
    response = client.post("/clients",data=my_data)
    assert response.status_code == 200
    assert response.json()['Status'] == ['Client Created']

def test_post_client_fail(mocker):
    expected = False
    mocker.patch(
        'api_lite.create_client', 
        return_value=expected
    )  
    my_data = { "name":"Pierre",
                "password":"test",
                "status":"active",
                "balance":2000,
                "role":"client"
                }
    my_data = json.dumps(my_data)
    response = client.post("/clients",data=my_data)
    assert response.status_code == 200
    assert response.json()['Status'] == ['Cannot Create This Client']

def test_update_name(mocker):
    expected = True
    mocker.patch(
        'api_lite.client_edit_name', 
        return_value=expected
    )  
    response = client.put("/clients/test/?new_name=test")
    assert response.status_code == 200
    assert response.json()['Message'] == ['Client updated']

def test_update_name_fail(mocker):
    expected = False
    mocker.patch(
        'api_lite.client_edit_name', 
        return_value=expected
    )  
    response = client.put("/clients/1")
    assert response.status_code == 200
    assert response.json()['Message'] == ['Client cannot be updated']

def test_update_add(mocker):
    expected = True
    
    mocker.patch(
        'api_lite.client_add_balance', 
        return_value=expected
    )  
    response = client.put("/clients/1/?add=2000")
    assert response.status_code == 200
    assert response.json()['Message'] == ['Client updated']

def test_update_add_fail(mocker):
    expected = False
    mocker.patch(
        'api_lite.client_add_balance', 
        return_value=expected
    )  
    response = client.put("/clients/1")
    assert response.status_code == 200
    assert response.json()['Message'] == ['Client cannot be updated']

def test_update_sub(mocker):
    expected = True
    
    mocker.patch(
        'api_lite.client_edit_name', 
        return_value=expected
    )  
    response = client.put("/clients/1/?sub=2000")
    assert response.status_code == 200
    assert response.json()['Message'] == ['Client updated']

def test_update_sub_fail(mocker):
    expected = False
    mocker.patch(
        'api_lite.client_edit_name', 
        return_value=expected
    )  
    response = client.put("/clients/1")
    assert response.status_code == 200
    assert response.json()['Message'] == ['Client cannot be updated']

def test_list_all_client_res(mocker):
    expected = {'reservations':['test'],'totals':['0'],"refunds":['0'],"facility":['test_chi'],"status":["confirmed"]}
    
    mocker.patch(
        'api_lite.list_all_client_reservations', 
        return_value=expected
    )  
    response = client.get("/list/all/client/?client=test")
    assert response.status_code == 200
    assert response.json()['Reservations'] == ["test"]
    assert response.json()['Totals'] == ["0"]
    assert response.json()['Refunds'] == ['0']

def test_list_all_transactions(mocker):
    expected = {'reservations':['test'],'totals':['0'],"refunds":['0'],"facility":['test_chi'],"status":["confirmed"]}
    
    mocker.patch(
        'api_lite.list_all_transactions', 
        return_value=expected
    )  
    response = client.get("/list/all/transactions")
    assert response.status_code == 200
    assert response.json()['Reservations'] == ["test"]
    assert response.json()['Totals'] == ["0"]
    assert response.json()['Refunds'] == ['0']

def test_list_client_nonempty_lst(mocker):
    expected = ['test_lst_value']
    mocker.patch(
        'api_lite.list_client', 
        return_value=expected
    )  

    response = client.get("/list/range/client/2021-04-10/2021-04-11/?client=Test")
    assert response.status_code == 200
    assert response.json()['result_list'] == expected   

def test_list_client_empty_lst(mocker):
    expected = []
    mocker.patch(
        'api_lite.list_client', 
        return_value=expected
    )  
    response = client.get("/list/range/client/2021-04-10/2021-04-11/?client=Test")
    assert response.status_code == 200
    assert response.json()['Message'] == ["No Results Found"]

def test_list_transactions_nonempty_lst(mocker):
    expected = {'reservations':['test'],'totals':['0'],"refunds":['0'],"facility":['test_chi'],"status":["confirmed"]}
    mocker.patch(
        'api_lite.list_transactions', 
        return_value=expected
    )  
    response = client.get("/list/range/transactions/2021-04-10/2021-04-11")
    assert response.status_code == 200
    assert response.json()['Reservations'] == ["test"]
    assert response.json()['Totals'] == ["0"]
    assert response.json()['Refunds'] == ['0']

def test_list_transactions_empty_lst(mocker):
    expected = []
    mocker.patch(
        'api_lite.list_transactions', 
        return_value=expected
    )  
    response = client.get("/list/range/transactions/2021-04-10/2021-04-11")
    assert response.status_code == 200
    assert response.json()['Message'] == ["No Results Found"]

def test_list_reservations_nonempty_lst(mocker):
    expected = ['test']
    mocker.patch(
        'api_lite.list_reservations', 
        return_value=expected
    )  
    response = client.get("/list/range/reservations/2021-04-10/2021-04-11")
    assert response.status_code == 200
    assert response.json()["Reservations"] == ['test']

def test_list_reservations_empty_lst(mocker):
    expected = []
    mocker.patch(
        'api_lite.list_reservations', 
        return_value=expected
    )  
    response = client.get("/list/range/reservations/2021-04-10/2021-04-11")
    assert response.status_code == 200
    assert response.json()['Message'] == ["No Results Found"]

def test_post_hold(mocker):
    expected = True
    mocker.patch(
        'api_lite.create_hold', 
        return_value=expected
    )       
    my_data = {
            "username": 'team3',
            "password": 'test',
            "client_name":"Pierre",
            "request": 'shop1',
            "start_date": '2021-04-10',
            "start_time": '13:00',
            "end_time": '14:00'}

    my_data = json.dumps(my_data)
    response = client.post("/hold",data=my_data)
    assert response.status_code == 200
    assert response.json()['success'] == True
    assert response.json()['message'] == "Your hold was placed"


def test_post_hold_fail(mocker):
    expected = False
    mocker.patch(
        'api_lite.create_hold', 
        return_value=expected
    )       
    my_data = {
            "username": 'team3',
            "password": 'test',
            "client_name":"Pierre",
            "request": 'shop1',
            "start_date": '2021-04-10',
            "start_time": '13:00',
            "end_time": '14:00'}

    my_data = json.dumps(my_data)
    response = client.post("/hold",data=my_data)
    assert response.status_code == 200
    assert response.json()['success'] == False
    assert response.json()['message'] == "Your hold could not be placed"
   

def test_delete_hold(mocker):
    expected = True
    mocker.patch(
        'api_lite.delete_hold', 
        return_value=expected
    )       
    my_data = {
            "username": 'team3',
            "password": 'test',
            "client_name":"Pierre",
            "request": 'shop1',
            "start_date": '2021-04-10',
            "start_time": '13:00',
            "end_time": '14:00'}

    my_data = json.dumps(my_data)
    response = client.delete("/hold",data=my_data)
    assert response.status_code == 200
    assert response.json()['success'] == True
    assert response.json()['message'] == "Your hold was deleted"

def test_delete_hold_fail(mocker):
    expected = False
    mocker.patch(
        'api_lite.delete_hold', 
        return_value=expected
    )       
    my_data = {
            "username": 'team3',
            "password": 'test',
            "client_name":"Pierre",
            "request": 'shop1',
            "start_date": '2021-04-10',
            "start_time": '13:00',
            "end_time": '14:00'}

    my_data = json.dumps(my_data)
    response = client.delete("/hold",data=my_data)
    assert response.status_code == 200
    assert response.json()['success'] == False
    assert response.json()['message'] == "Your hold could not be deleted"
    
