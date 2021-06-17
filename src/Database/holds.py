import sys
import sqlite3
import random
import datetime as dt
import calendar
import utils 
import client
import reservations

sys.path.append('../src/classes')
from collections import namedtuple
from reservation_cls import Reserve

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

    dt_date = utils.to_dt_format(start_date)
    day = calendar.day_name[dt_date.weekday()]

    if day == "Sunday":
        return False
    
    if day == "Saturday":
        if int_st < 10 or int_end > 16:
            return False

    if int_st < 9 or int_end > 18:
        return False

    valid_login = utils.is_valid_login(username,password)
    
    if valid_login == "hold_admin":
        status = utils.is_available(request,start_date,int_st,int_end)
        if status == "Free":
            utils.add_time(request,start_date,int_st,int_end,f'{username}')
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

    valid_login = utils.is_valid_login(username,password)
    
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