# test_sqllite.py
import pytest
import Database.api_lite as api
from src.classes.reservation import Reserve


# create a temporary database
@pytest.fixture
def temp_db():
    # set up the in-memory database with test data
    api.db = api.open_db(':memory:')
    api.db.curs.execute("select count(*) from reservations")
    print(f" ### Top of temp_db for reservations: the database has {api.db.curs.fetchone()[0]} rows.")

    api.db.curs.execute('DELETE FROM reservations')
    api.db.curs.execute("select count(*) from reservations")
    print(f" ### Deleted: the database has {api.db.curs.fetchone()[0]} rows.")

    sample_data = {"id": "12345",
                   "client": 'Claire',
                   "request": 'workshop1',
                   "create_date": '2021-05-10',
                   "start_date": '2021-05-18',
                   "res_start": '13:00',
                   "res_end": '14:00',
                   "status": 'Confirmed',
                   "cost": '250',
                   "refund": '0',
                   "client_id": '123',
                   "facility": 'Team_03_Chicago'}

    sql = "insert into reservations (ID, Client, Request, Create_dt, Start_dt,\
               Start_time, End_time, Status, Cost, Refund, Client_ID, Facility) values (?,?,?,?,?,?,?,?,?,?,?,?)"

    api.db.curs.execute(sql, (sample_data['id'], sample_data['client'], sample_data['request'],
                              sample_data['create_date'], sample_data['start_date'],
                              sample_data['res_start'], sample_data['res_end'], sample_data['status'],
                              sample_data['cost'], sample_data['refund'], sample_data['client_id'],
                              sample_data['facility']))

    api.db.curs.execute("select count(*) from reservations")
    print(f" ### the database reservations table has {api.db.curs.fetchone()[0]} rows.")

    # inputs for sample clients table
    sample_client = {"name": "Claire",
                     "password": "cw",
                     "status": "client",
                     "balance": "100",
                     "role": "client",
                     "id": "007"}
    test_password = 'cw'
    salt, hash_result = api.generate_hash(test_password)

    sql = "insert into clients (Name, Hash,Salt, Status, Balance,Role,ID) values (?,?,?,?,?,?,?)"
    api.db.curs.execute(sql, (sample_client['name'], hash_result, salt, sample_client['status'],
                              sample_client['balance'], sample_client['role'], sample_client['id']))
    api.db.curs.execute("select count(*) from clients")
    print(f" ### the database clients table has {api.db.curs.fetchone()[0]} rows.")

    api.db.curs.execute('DELETE FROM clients')
    api.db.curs.execute("select count(*) from clients")
    print(f" ### Deleted: the database has {api.db.curs.fetchone()[0]} rows on Clients table.")

    print("  ### yielding ###")
    yield api.db.conn

    print("  ### starting cleanup ###")
    api.db_cleanup()
    print("  ### cleanup complete ###")


def test_connection(temp_db):
    # Test to make sure that there are 1 item in the database
    api.db.curs = temp_db.cursor()
    assert len(list(api.db.curs.execute('SELECT * FROM reservations'))) == 1


def test_create_client(temp_db):
    api.db.curs = temp_db.cursor()
    args = {"name": "Phoebe",
            "password": "pw",
            "status": "client",
            "balance": "100",
            "role": "client",
            "id": "0018"}
    response = api.create_client(args)
    print(response)
    api.db.curs.execute("select count(*) from clients")
    count = api.db.curs.fetchone()[0]
    assert count == 1


# this is testing the create res function
def test_create_res(temp_db):
    api.db.curs = temp_db.cursor()
    args = {
        "create_date": '2021-06-03',
        "start_date": '2021-06-15',
        "res_start": '10:00',
        "res_end": '11:00',
        "facility": 'Team_03_Chicago',
        "request": 'workshop2',
        "client": 'Phoebe'
    }
    api.client_activate(args['client'])
    res = api.create_res(args)
    print(res)
    api.db.curs.execute("select count(*) from reservations")
    count = api.db.curs.fetchone()[0]
    assert count == 1


# this test is testing if we can add successful list the reservation
def test_list_reservation(temp_db):

    res_list = api.list_all_reservations()
    print('res_list')
    print(res_list)
    assert res_list[0] == '12345'  # number of reservation we have right now


def test_delete_reservation(temp_db):

    response = api.delete_res('12345')
    print(response)
    assert response == True


