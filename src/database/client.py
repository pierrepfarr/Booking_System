import sys
import sqlite3
import random
import datetime as dt
import calendar
from collections import namedtuple

""" Client functionality """

def create_client(args):
    name = args['name']
    password = args['password']
    status = args['status']
    balance = args['balance']
    role = args['role']

    exist = check_client_exist(name)
    
    if not exist:
        salt,hash_result = generate_hash(password)
        id_lst = list_all_client_ids()
        new_id = gen_client_id(name,id_lst)
        sql = f"insert into clients (Name, Hash,Salt, Status, Balance,Role,ID) values (?,?,?,?,?,?,?)"
        db.curs.execute(sql,(name,hash_result,salt,status,balance,role,new_id))
        db.conn.commit()
    
        return True
    return False

def client_edit_name(client,new_name):
    check_new_exist = check_client_exist(new_name)
    if check_new_exist:
        return False
    sql = "select count(*) from clients where Name = ?"
    db.curs.execute(sql,(client,))
    result = db.curs.fetchone()
    if result[0] == 1:     
        sql = '''UPDATE clients SET Name = ? WHERE Name = ?'''
        db.curs.execute(sql,(new_name,client))
        db.conn.commit()
        return True
    return False

def add_balance(client,amount):
    sql = "select count(*) from clients where Name = ?"
    db.curs.execute(sql,(client,))
    result = db.curs.fetchone()
    if result[0] == 1:      
        sql = "select Balance from clients where Name = ?"
        db.curs.execute(sql,(client,))
        current_balance = db.curs.fetchone()
        new_balance = current_balance[0] + amount

        sql = '''UPDATE clients SET Balance = ? WHERE Name = ?'''
        db.curs.execute(sql,(new_balance,client))
        db.conn.commit()
        return True
    return False

def sub_balance(client,amount):
    sql = "select count(*) from clients where Name = ?"
    db.curs.execute(sql,(client,))
    result = db.curs.fetchone()
    if result[0] == 1:       
        sql = "select Balance from clients where Name = ?"
        db.curs.execute(sql,(client,))
        current_balance = db.curs.fetchone()
        new_balance = current_balance[0] - amount
        
        sql = '''UPDATE clients SET Balance = ? WHERE Name = ?'''
        db.curs.execute(sql,(new_balance,client))
        db.conn.commit()
        return True
    return False

def client_deactivate(client):
    sql = "select count(*) from clients where Name = ?"
    db.curs.execute(sql,(client,))
    result = db.curs.fetchone()
    if result[0] == 1:    
        sql = '''UPDATE clients SET Status = 'Deactivated' WHERE Name = ?'''
        db.curs.execute(sql,(client,))
        db.conn.commit()
        return True
    return False

def client_activate(client):
    sql = "select count(*) from clients where Name = ?"
    db.curs.execute(sql,(client,))
    result = db.curs.fetchone()
    if result[0] == 1:
        sql = '''UPDATE clients SET Status = 'Active' WHERE Name = ?'''
        db.curs.execute(sql,(client,))
        db.conn.commit()
        return True
    return False


""" Client Queries """

def list_all_clients():
    db.curs.execute('SELECT Name from clients')
    reservations = db.curs.fetchall()
    client_list = []
    for res in reservations:
        client_list.append(res[0])
    return client_list    

def list_client(client,start_dt,end_dt):
    client_id = get_client_id(client)
    sql_query = "SELECT * FROM reservations WHERE Start_dt BETWEEN ? AND ? AND Client_ID = ? AND Status !='Hold'"
    db.curs.execute(sql_query,(start_dt,end_dt,client_id))
    result = db.curs.fetchall()
    trans_list = []
    for res in result:
        res_str = f'Reservation: {res[0]}, Total:{res[8]}, Refunded:{res[9]}, Facility:{res[11]}, Status:{res[7]}'
        trans_list.append(res_str)
    return trans_list

def list_all_client_reservations(client):
    client_id = get_client_id(client)
    sql_query = "SELECT * FROM reservations WHERE Client_ID = ?"
    db.curs.execute(sql_query,(client_id,))
    result = db.curs.fetchall()
    trans_dict = {'reservations':[],'totals':[],"refunds":[],'facility':[],'status':[]}
    for res in result:
        trans_dict['reservations'].append(f'{res[0]}')
        trans_dict['totals'].append(f'{res[8]}')
        trans_dict['refunds'].append(f'{res[9]}')
        trans_dict['facility'].append(f'{res[11]}')
        trans_dict['status'].append(f'{res[7]}')        
    
    return trans_dict


def get_client_balance(client):
    sql = "select count(*) from clients where Name = ?"
    db.curs.execute(sql,(client,))
    result = db.curs.fetchone()
    if result[0] == 1:
        sql = "select Name, Balance from clients where Name = ?"
        db.curs.execute(sql,(client,))
        result = db.curs.fetchone()
        return [result[0],result[1]]
    
    return False

def get_client_id(client):
    valid_client = check_client_exist(client)
    if valid_client:
        sql = "select ID from clients where Name = ?"
        db.curs.execute(sql,(client,))
        result = db.curs.fetchone()
        if result:
            return result[0]
        return False