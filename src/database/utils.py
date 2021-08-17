import sys
import sqlite3
import regex as re
import random
import os,hashlib
import datetime as dt
from collections import namedtuple

sys.path.append('../src/classes')
from reservation_cls import Reserve

equipment_lst = ['workshop1','workshop2','workshop3','workshop4','"mini microvac1"','"mini microvac2"',
                    'irradiator1', 'irradiator2', '"polymer extruder1"', '"polymer extruder2"',
                    '"high velocity crusher"', '"1.21 gigawatt lightning harvester"']

DB_FILE = "../src/reservations.db"

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


def to_dt_format(str_date):
    return dt.datetime.strptime(str_date, "%Y-%m-%d").date()

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


def get_client_ids(db):
    db.curs.execute('SELECT ID from clients')
    reservations = db.curs.fetchall()
    client_list = []
    for res in reservations:
        client_list.append(res[0])
    return client_list  

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

def is_valid_login(db,user,password):
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

def is_available(db,equipment,date,start,end):
    sql = f"SELECT * FROM '{equipment}' WHERE Date = ? AND Time BETWEEN ? AND ?"
    db.curs.execute(sql,(date,start,(end-.5)))
    result = db.curs.fetchall()
    if result:
        return False
    return "Free"    

def is_admin(db,client):
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

def is_client_exist(db,client):
    sql = "select count(*) from clients where Name = ?"
    db.curs.execute(sql,(client,))
    result = db.curs.fetchone()
    if result[0]==1:
        return True
    return False

def is_client_active(db,client):
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


def add_time(db,equipment,date,start,end,res_id):
    sql = f"insert into '{equipment}' (Date, Time, ID) values (?,?,?)"
    time = start
    while time < end:
        db.curs.execute(sql,(date,time,res_id))
        time += .5
    db.conn.commit()

def delete_time(db,equipment,date,start,end):
    sql = f"DELETE from '{equipment}' WHERE Date=? and Time=?"
    time = start
    while time < end:
        db.curs.execute(sql,(date,time))
        time += .5
    db.conn.commit()