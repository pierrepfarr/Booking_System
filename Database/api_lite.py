import sys
import sqlite3
import json
import regex as re
import random
import atexit
import os,hashlib
import datetime as dt
import calendar
from collections import namedtuple

sys.path.append('../src')
from actions import to_dt_format

sys.path.append('../src/classes')
from reservation import Reserve

equipment_lst = ['workshop1','workshop2','workshop3','workshop4','"mini microvac1"','"mini microvac2"',
                    'irradiator1', 'irradiator2', '"polymer extruder1"', '"polymer extruder2"',
                    '"high velocity crusher"', '"1.21 gigawatt lightning harvester"']

DB_FILE = "../Database/reservations.db"

def open_db(database_file=DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    curs = conn.cursor()
    sql_create_reservations = """ CREATE TABLE IF NOT EXISTS reservations (
                                    ID VARCHAR(140),
                                    Client VARCHAR(20),
                                    Request TEXT,
                                    Create_dt TEXT,
                                    Start_dt TEXT,
                                    Start_time VARCHAR(140),
                                    End_time VARCHAR(140),
                                    Status VARCHAR(140),
                                    Cost VARCHAR(140),
                                    Refund VARCHAR(140),
                                    Client_ID VARCHAR(140),
                                    Facility TEXT
                                );"""
        
    curs.execute(sql_create_reservations)
    
    curs.execute(
        'CREATE TABLE IF NOT EXISTS clients (Name VARCHAR(140), Hash BLOB, Salt BLOB, Status TEXT, Balance REAL, Role TEXT,ID VARCHAR(140))')        

    equipment_lst = ['workshop1','workshop2','workshop3','workshop4','"mini microvac1"','"mini microvac2"',
                     'irradiator1', 'irradiator2', '"polymer extruder1"', '"polymer extruder2"',
                     '"high velocity crusher"', '"1.21 gigawatt lightning harvester"']

    for item in equipment_lst:
            curs.execute(
                f'CREATE TABLE IF NOT EXISTS {item} (Date TEXT, Time REAL, ID VARCHAR(140))')    

    db = namedtuple('db', 'conn curs')
    db.conn = conn
    db.curs = curs

    return db
    
def db_cleanup():
    db.conn.commit()
    db.curs.close()
    db.conn.close()


""" making and modifying """

def check_login(user,password):
    sql = "select Hash, Salt, Role from clients where Name = ?"
    db.curs.execute(sql,(user,))
    result = db.curs.fetchone()
    if not result:
        return False
    old_hash = result[0]
    salt = result[1]
    salt, new_hash = generate_hash(password,salt)
    if new_hash == old_hash:
        return result[2]
    return False

def create_res(args):
    
    create_date = args['create_date']
    start_date = args['start_date']
    int_st = time_chg(args['res_start'])
    int_end = time_chg(args['res_end'])
    request = args['request'].lower()  
    facility = args['facility']  
    
    is_client = check_client_exist(args['client'])
    is_active = check_client_active(args['client'])

    dt_date = dt.datetime.strptime(start_date,"%Y-%m-%d").date()
    day = calendar.day_name[dt_date.weekday()]

    if day == "Sunday":
        return False
    
    if day == "Saturday":
        if int_st < 10 or int_end > 16:
            return False

    if int_st < 9 or int_end > 18:
        return False

    if is_client == False:
        return "Please Create Client"
    
    if is_active == False:
        return "Your booking ability is not active"

    status = check_available(request,start_date,int_st,int_end)
    
    if status == "Free":
        res = Reserve(args['client'], request, create_date, start_date,
                      args['res_start'], args['res_end'])   
        
        res_list = list_all_reservations()
        new_id = gen_res_id(res.st_dt,res_list)
        res.add_id(new_id)
        
        add_time(request,start_date,int_st,int_end,res.id)

        client_id = get_client_id(args['client'])
        
        sql = "insert into reservations (ID, Client, Request, Create_dt, Start_dt,\
               Start_time, End_time, Status, Cost, Refund,Client_ID,Facility) values (?,?,?,?,?,?,?,?,?,?,?,?)"
    
        db.curs.execute(sql, (res.id,res.client,res.req,res.crt_dt,res.st_dt,
                        res.st_time,res.end_time,res.status,res.cost,0,client_id,facility))
        
        db.conn.commit()

        edit_balance = client_sub_balance(res.client,res.cost)

        return res
    
    return False

def delete_res(res_id):
    sql = "select count(*) from reservations where ID = ?"
    db.curs.execute(sql,(res_id,))
    result = db.curs.fetchone()
    if result[0] == 1:
        sql = "select * from reservations where ID = ?"
        db.curs.execute(sql,(res_id,))
        result = db.curs.fetchone()
        res = Reserve(result[1],result[2],result[3],result[4],result[5],result[6])
        res.cancel()
        
        delete_time(res.req,res.st_dt,res.int_st,res.int_end)
        
        sql = '''UPDATE reservations SET Status = ?, Refund = ? WHERE ID = ?'''
        db.curs.execute(sql,(res.status,res.refund,res_id))
        db.conn.commit()
        
        edit_balance = client_add_balance(res.client,res.refund)

        return True
    
    return False    

def modify_reservation(res_id,args):
    client_id = get_client_id(args['client'])

    sql = "select count(*) from reservations where ID = ?"
    db.curs.execute(sql,(res_id,))
    result = db.curs.fetchone()
    
    if result[0] == 1:
        db.curs.execute( f"select * from reservations where ID = {res_id}")
        result = db.curs.fetchone()
        if client_id != result[10]:
            return False
        
        res = Reserve(result[1],result[2],result[3],result[4],result[5],result[6])
        
        delete_time(res.req,res.st_dt,res.int_st,res.int_end)
        add_back_balance = client_add_balance(res.client,res.cost)
        
        create_date = args['create_date']
        start_date = args['start_date']
        int_st = time_chg(args['res_start'])
        int_end = time_chg(args['res_end'])

        request = args['request'].lower() 
        
        dt_date = dt.datetime.strptime(start_date,"%Y-%m-%d").date()
        day = calendar.day_name[dt_date.weekday()]

        if day == "Sunday":
            return False
        
        if day == "Saturday":
            if int_st < 10 or int_end > 16:
                return False

        if int_st < 9 or int_end > 18:
            return False
        
        status = check_available(request,start_date,int_st,int_end)
        
        if status == "Free":
            res = Reserve(args['client'], request, create_date, start_date,
                          args['res_start'], args['res_end'])   
            

            res.add_id(res_id)
            
            add_time(request,start_date,int_st,int_end,res_id)

            sql = '''UPDATE reservations SET Client = ?, 
                     Request = ?,
                     Create_dt = ?,
                     Start_dt = ?,
                     Start_time = ?,
                     End_time = ?,
                     Status = ?,
                     Cost = ?,
                     Refund = ?
                     WHERE ID = ?'''
            

            db.curs.execute(sql, (res.client,res.req,res.crt_dt,res.st_dt,res.st_time,
                                  res.end_time,res.status,res.cost,0,res.id))
            db.conn.commit()
            
            edit_balance = client_sub_balance(res.client,res.cost)
            
            return res
        
        return False
    
    return False    

def create_hold(args):
    username = args['username']
    password = args['password']
    client_name = args['client_name'] 
    request = args['request']
    start_date = args['start_date']
    start_time = args['start_time']
    end_time = args['end_time']
    int_st = time_chg(start_time)
    int_end = time_chg(end_time)

    dt_date = dt.datetime.strptime(start_date,"%Y-%m-%d").date()
    day = calendar.day_name[dt_date.weekday()]

    if day == "Sunday":
        return False
    
    if day == "Saturday":
        if int_st < 10 or int_end > 16:
            return False

    if int_st < 9 or int_end > 18:
        return False

    valid_login = check_login(username,password)
    
    if valid_login == "hold_admin":
        status = check_available(request,start_date,int_st,int_end)
        if status == "Free":
            add_time(request,start_date,int_st,int_end,f'{username}')
            return True

    return False

def delete_hold(args):
    username = args['username']
    password = args['password']
    client_name = args['client_name'] 
    request = args['request']
    start_date = args['start_date']
    start_time = args['start_time']
    end_time = args['end_time']
    int_st = time_chg(start_time)
    int_end = time_chg(end_time)

    valid_login = check_login(username,password)
    
    if valid_login == "hold_admin":
        sql = f"select Time from {request} where ID = ?"
        hold_id = f'{username}+{client_name}'
        db.curs.execute(sql,(hold_id,))
        
        result = db.curs.fetchone()
        if result[0] == int_st:
            delete_time(request,start_date,int_st,int_end)
            return True
    
    return False

def charge_hold(args):
    
    create_date = args['create_date']
    start_date = args['start_date']
    int_st = time_chg(args['res_start'])
    int_end = time_chg(args['res_end'])
    request = args['request'].lower()    
    facility = args['facility']

    res = Reserve(args['client'], request, create_date, start_date,
                    args['res_start'], args['res_end'],location=facility)   
    
    res_list = list_all_reservations()
    new_id = gen_res_id(res.st_dt,res_list)
    res.add_id(new_id)
    
    client_id = get_client_id(args['client'])
    
    sql = "insert into reservations (ID, Client, Request, Create_dt, Start_dt,\
            Start_time, End_time, Status, Cost, Refund,Client_ID,Facility) values (?,?,?,?,?,?,?,?,?,?,?,?)"

    db.curs.execute(sql, (res.id,res.client,res.req,res.crt_dt,res.st_dt,
                    res.st_time,res.end_time,"Hold",res.cost,0,client_id,facility))
    
    db.conn.commit()

    return res

def get_holds():
    hold_list = []
    teams = "'team1', 'team2', 'team4', 'team5', 'Spencer', 'Peter'"
    for item in equipment_lst:
        sql = f'Select * from {item} where ID IN ({teams}) '
        db.curs.execute(sql)
        result = db.curs.fetchall()
        for res in result:
            hold_str = f'{res[0]},{item},{res[2]}'
            if hold_str not in hold_list:
                hold_list.append(hold_str)
        return hold_list  
    
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

def client_add_balance(client,amount):
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

def client_sub_balance(client,amount):
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

""" getting information """

def get_reservation(res_id):
    db.curs.execute( f"select count(*) from reservations where ID = {res_id}")
    result = db.curs.fetchone()
    if result[0] == 1:
        db.curs.execute( f"select * from reservations where ID = {res_id}")
        result = db.curs.fetchone()
        res = Reserve(result[1],result[2],result[3],result[4],result[5],result[6])
        res.id = result[0]
        if result[8] != "Current":
            res.cancel()
        return res
    
    return False    

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

"""listing"""

def list_all_transactions():
    sql = 'SELECT * from reservations where Status != "Hold"'
    db.curs.execute(sql)
    result = db.curs.fetchall()
    trans_dict = {'reservations':[],'totals':[],"refunds":[],'facility':[],'status':[]}
    for res in result:
        trans_dict['reservations'].append(f'{res[0]}')
        trans_dict['totals'].append(f'{res[8]}')
        trans_dict['refunds'].append(f'{res[9]}')
        trans_dict['facility'].append(f'{res[11]}')
        trans_dict['status'].append(f'{res[7]}')        
    
    return trans_dict

def list_all_reservations():
    db.curs.execute('SELECT rowid, ID from reservations')
    reservations = db.curs.fetchall()
    id_list = []
    for res in reservations:
        id_list.append(res[1])
    return id_list

def list_all_clients():
    db.curs.execute('SELECT Name from clients')
    reservations = db.curs.fetchall()
    client_list = []
    for res in reservations:
        client_list.append(res[0])
    return client_list    

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

def list_transactions(start_dt,end_dt):
    sql_query = "SELECT * FROM reservations WHERE Start_dt BETWEEN ? AND ? AND Status != 'Hold'"
    db.curs.execute(sql_query,(start_dt,end_dt))
    result = db.curs.fetchall()
    trans_dict = {'reservations':[],'totals':[],"refunds":[]}
    trans_dict = {'reservations':[],'totals':[],"refunds":[],'facility':[],'status':[]}
    for res in result:
        trans_dict['reservations'].append(f'{res[0]}')
        trans_dict['totals'].append(f'{res[8]}')
        trans_dict['refunds'].append(f'{res[9]}')
        trans_dict['facility'].append(f'{res[11]}')
        trans_dict['status'].append(f'{res[7]}')        
    
    return trans_dict

def list_reservations(start_dt,end_dt):
    sql_query = "SELECT * FROM reservations WHERE Start_dt BETWEEN ? AND ?"
    db.curs.execute(sql_query,(start_dt,end_dt))
    result = db.curs.fetchall()
    res_list = []
    for res in result:
        res_str = f'{res[0]}'
        res_list.append(res_str)
    return res_list  

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

""" helper functions """

def time_chg(time_str):
    pattern = re.search(r"\d\d:[1-9][0-9]", time_str)
    if pattern != None:
        int_time = int(time_str[0:2]) + .5
        return int_time
    return int(time_str[0:2])

def gen_res_id(date,id_lst):
    dt_date = to_dt_format(date)
    m_num = dt_date.month
    y_num = dt_date.year
    ran_num = random.randint(1, 15000)
    new_id = str(y_num) + str(m_num) + str(ran_num)
    if new_id in id_lst:
        gen_res_id(date,id_lst)

    return new_id

def gen_client_id(name,id_lst):
    ran_num = random.randint(1, 15000)
    new_id = str(name) + str(ran_num)
    if new_id in id_lst:
        gen_res_id(name,id_lst)

    return new_id

def generate_hash(password,salt=None):
    if salt == None:
        salt = os.urandom(32)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000
    )
    return salt, hashed 

def list_all_client_ids():
    db.curs.execute('SELECT ID from clients')
    reservations = db.curs.fetchall()
    client_list = []
    for res in reservations:
        client_list.append(res[0])
    return client_list    

def check_client_exist(client):
    sql = "select count(*) from clients where Name = ?"
    db.curs.execute(sql,(client,))
    result = db.curs.fetchone()
    if result[0]==1:
        return True
    return False

def check_client_active(client):
    sql = "select count(*) from clients where Name = ?"
    db.curs.execute(sql,(client,))
    result = db.curs.fetchone()
    if result[0]==1:
        sql = "select Status from clients where Name = ?"
        db.curs.execute(sql,(client,))
        result = db.curs.fetchone()
        status = result[0]
        return status == "Active"
    return False

def check_available(equipment,date,start,end):
    sql = f"SELECT * FROM '{equipment}' WHERE Date = ? AND Time BETWEEN ? AND ?"
    db.curs.execute(sql,(date,start,(end-.5)))
    result = db.curs.fetchall()
    if result:
        return False
    return "Free"    

def check_role_admin(client):
    sql = "select count(*) from clients where Name = ?"
    db.curs.execute(sql,(client,))
    result = db.curs.fetchone()
    if result[0]==1:
        sql = "select Role from clients where Name = ?"
        db.curs.execute(sql,(client,))
        result = db.curs.fetchone()
        role = result[0]
        return role == 'admin'
    
    return False

def add_time(equipment,date,start,end,res_id):
    sql = f"insert into '{equipment}' (Date, Time, ID) values (?,?,?)"
    time = start
    while time < end:
        db.curs.execute(sql,(date,time,res_id))
        time += .5
    db.conn.commit()

def delete_time(equipment,date,start,end):
    sql = f"DELETE from '{equipment}' WHERE Date=? and Time=?"
    time = start
    while time < end:
        db.curs.execute(sql,(date,time))
        time += .5
    db.conn.commit()


if __name__ == '__main__':
    atexit.register(db_cleanup)
