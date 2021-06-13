import datetime as dt
import regex as re
from regex.regex import sub

class Reserve:
    """ all the information pertaining to a reservation """

    pricing = {'workshop': 99, 'mini microvac': 2000,
               'irradiator': 2200, 'polymer extruder': 500,
               'high velocity crusher': 10000, '1.21 gigawatt lightning harvester': 8800}

    def __init__(self, client, req, crt_dt, st_dt, st_time, end_time,location="Team_3_Chicago"):
        self.client = client
        self.req = req
        self.crt_dt = crt_dt
        self.st_dt = st_dt
        self.advance = self.num_advance(st_dt,crt_dt)
        self.st_time = st_time
        self.end_time = end_time
        self.int_st = self.time_chg(st_time)
        self.int_end = self.time_chg(end_time)
        self.status = "Current"
        self.cost = self.calc_cst()
        self.location = location

    def calc_cst(self):
        hours = self.int_end - self.int_st
        key = self.req_key(self.req)
        rate = self.pricing[key]
        cost = hours * rate
        if self.advance >= 14:
            cost = cost * .75
        if 'shop' not in self.req:
            self.dwn_pmt = cost * .5
        else:
            self.dwn_pmt = 0
        return cost

    def req_key(self, test_str):
        x = re.match(r"\D+", test_str)
        return x.group(0)

    def add_id(self, new_id):
        self.id = new_id

    def cancel(self):
        start_dt_fmt = self.to_dt_format(self.st_dt)
        cancel_dt = dt.date.today()
        notice = (start_dt_fmt - cancel_dt).days

        if notice >= 7:
            refund = self.dwn_pmt * .75
        elif notice >= 2:
            refund = self.dwn_pmt * .5
        else:
            refund = 0
        self.status = "Cancelled"
        self.refund = refund

    def to_dt_format(self,str_date):
        return dt.datetime.strptime(str_date, "%Y-%m-%d").date()

    def num_advance (self,start_dt,create_dt):
        start_dt_fmt = self.to_dt_format(start_dt)
        create_dt_fmt = self.to_dt_format(create_dt)
        return (start_dt_fmt - create_dt_fmt).days
    
    def time_chg(self,time_str):
        pattern = re.search(r"\d\d:[1-9][0-9]", time_str)
        if pattern != None:
            int_time = int(time_str[0:2]) + .5
            return int_time
        return int(time_str[0:2])

    def __repr__(self):
        if not self.id:
            self.id = ''
        return (f'Reservation: {self.id}, Client: {self.client} ' +
                f'Request: {self.req}, Start: {self.st_time} ' +
                f'End: {self.end_time}, Status: {self.status}')