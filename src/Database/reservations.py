import sys
import sqlite3
import random
import datetime as dt
import calendar
import utils 
import client

sys.path.append('../src/classes')
from collections import namedtuple
from reservation_cls import Reserve
""" Reservation Functionality """

def create_res(args):
    create_date = args['create_date']
    start_date = args['start_date']
    int_st = time_chg(args['res_start'])
    int_end = time_chg(args['res_end'])
    request = args['request'].lower()  
    facility = args['facility']  
    
    is_client = utils.is_client_exist(args['client'])
    is_active = utils.is_client_active(args['client'])

    dt_date = utils.to_dt_format(start_date)
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

    status = utils.is_available(request,start_date,int_st,int_end)
    
    if status == "Free":
        res = Reserve(args['client'], request, create_date, start_date,
                      args['res_start'], args['res_end'])   
        
        res_list = list_all_reservations()
        new_id = utils.gen_res_id(res.st_dt,res_list)
        res.add_id(new_id)
        
        utils.add_time(request,start_date,int_st,int_end,res.id)

        client_id = client.get_client_id(args['client'])
        
        sql = "insert into reservations (ID, Client, Request, Create_dt, Start_dt,\
               Start_time, End_time, Status, Cost, Refund,Client_ID,Facility) values (?,?,?,?,?,?,?,?,?,?,?,?)"
    
        db.curs.execute(sql, (res.id,res.client,res.req,res.crt_dt,res.st_dt,
                        res.st_time,res.end_time,res.status,res.cost,0,client_id,facility))
        
        db.conn.commit()

        edit_balance = client.sub_balance(res.client,res.cost)

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
        
        utils.delete_time(res.req,res.st_dt,res.int_st,res.int_end)
        
        sql = '''UPDATE reservations SET Status = ?, Refund = ? WHERE ID = ?'''
        db.curs.execute(sql,(res.status,res.refund,res_id))
        db.conn.commit()
        
        edit_balance = client.add_balance(res.client,res.refund)

        return True
    return False    

def modify_reservation(res_id,args):
    client_id = client.get_client_id(args['client'])

    sql = "select count(*) from reservations where ID = ?"
    db.curs.execute(sql,(res_id,))
    result = db.curs.fetchone()
    
    if result[0] == 1:
        db.curs.execute( f"select * from reservations where ID = {res_id}")
        result = db.curs.fetchone()
        if client_id != result[10]:
            return False
        
        res = Reserve(result[1],result[2],result[3],result[4],result[5],result[6])
        
        utils.delete_time(res.req,res.st_dt,res.int_st,res.int_end)
        add_back_balance = client.add_balance(res.client,res.cost)
        
        create_date = args['create_date']
        start_date = args['start_date']
        int_st = time_chg(args['res_start'])
        int_end = time_chg(args['res_end'])
        request = args['request'].lower() 
        dt_date = utils.to_dt_format(start_date)
        day = calendar.day_name[dt_date.weekday()]

        if day == "Sunday":
            return False
        if day == "Saturday":
            if int_st < 10 or int_end > 16:
                return False
        if int_st < 9 or int_end > 18:
            return False
        
        status = utils.is_available(request,start_date,int_st,int_end)
        
        if status == "Free":
            res = Reserve(args['client'], request, create_date, start_date,
                          args['res_start'], args['res_end'])   
            
            res.add_id(res_id)
            utils.add_time(request,start_date,int_st,int_end,res_id)

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
            
            edit_balance = client.sub_balance(res.client,res.cost)
            
            return res
        return False
    return False 


""" Reservation Queries """

def list_all_reservations():
    db.curs.execute('SELECT rowid, ID from reservations')
    reservations = db.curs.fetchall()
    id_list = []
    for res in reservations:
        id_list.append(res[1])
    return id_list

def list_reservations(start_dt,end_dt):
    sql_query = "SELECT * FROM reservations WHERE Start_dt BETWEEN ? AND ?"
    db.curs.execute(sql_query,(start_dt,end_dt))
    result = db.curs.fetchall()
    res_list = []
    for res in result:
        res_str = f'{res[0]}'
        res_list.append(res_str)
    return res_list  


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