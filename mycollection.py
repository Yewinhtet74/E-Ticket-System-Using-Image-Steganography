ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
import json
from datetime import datetime,timedelta
import uuid
def ones():
    print('HIIII')
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def find_counter(flight_no,date,mysql):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * FROM airline_database.checkincounter where flight_no='"+flight_no+"' and date='"+date+"';")
    d = cursor.fetchone()
    cursor.execute("SELECT departure,departure_time FROM airline_database.route where flight_no='"+flight_no+"';")
    depart = cursor.fetchone()
    print(d,depart)
    res={}
    if d:   res['counter_no']=d[2]
    if depart:  
        res['departure_code']=depart[0]
        res['departure_time']="{:0>5}".format(str(depart[1]+timedelta(hours=-2))[:-3])
        res.update(get_city_data(depart[0]))
    return res
def get_city_data(city_code):
    codes=json.load(open('city_code.json','r'))
    return codes[city_code]
def get_airport_data():
    codes=json.load(open('city_code.json','r'))
    return codes

def get_date_format(date,days=0):
    months = ['JAN', 'FEB', 'MAR', "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    # d = '2024-03-01'
    [year, month, day] = date.split('-')
    return f"{([day,int(day)+days][days]):0>2}"+' '+months[int(month)-1]+' '+year

def date_to_week(date):
    dt = datetime.strptime(date[2:], '%y-%m-%d')
    return dt.weekday()+1

def search_flight(mysql,data):
    cursor = mysql.connect().cursor()
    date=['',' and day='+str(date_to_week(data['date']))][bool(data['date'])]
    clas=['',' and '+data['class'].lower()+'_seat!=0'][bool(data['class'])]
    query="SELECT departure,arrival,day,departure_time,arrival_time,first_seat,business_seat,premium_seat,economy_seat,flight_no,p.plane_no FROM route AS r INNER JOIN plane AS p ON r.plane_no=p.plane_no WHERE departure LIKE '%"+data['depart']+"%' and arrival LIKE '%"+data['arrive']+"%'"+clas+date+"  ORDER BY departure_time;"
    print(query)
    cursor.execute(query)
    record = cursor.fetchall()
    cursor.close()
    dt=[]
    for d in record:
        print(d)
        dt.append({'depart_code':d[0],'arrive_code':d[1],'depart_name':get_city_data(d[0])['city'],'arrive_name':get_city_data(d[1])['city'],
                   'depart_time':"{:0>5}".format(str(d[3])[:-3]),'arrive_time':"{:0>5}".format(str(d[4])[:-3]),
                   'depart_date':get_date_format(data['date']),'arrive_date':get_date_format(data['date'],d[3]>d[4]),
                   'first_seat':d[5],'business_seat':d[6],'premium_seat':d[7],'economy_seat':d[8],'flight_no':d[9],'plane_no':d[10]})
    print(dt)
    return dt

def get_a_flight(mysql,flight_no,date):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT departure,arrival,departure_time,arrival_time,first_seat,business_seat,premium_seat,economy_seat FROM route AS r INNER JOIN plane AS p ON r.plane_no=p.plane_no WHERE flight_no='"+flight_no+"';")
    d = cursor.fetchone()
    flight={'depart_code':d[0],'arrive_code':d[1],'depart_name':get_city_data(d[0])['city'],'arrive_name':get_city_data(d[1])['city'],
                   'depart_time':"{:0>5}".format(str(d[2])[:-3]),'arrive_time':"{:0>5}".format(str(d[3])[:-3]),
                   'depart_dates':get_date_format(date,d[2]>d[3]),'arrive_date':get_date_format(date,d[2]>d[3]),
                    'first_seat':d[4],'business_seat':d[5],'premium_seat':d[6],'economy_seat':d[7]}
    print(d,flight)
    return flight

def get_all_flight_no(mysql):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT flight_no FROM airline_database.route;")
    d = cursor.fetchall()
    return d
def check_admin_account(mysql,user,pwd):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT EXISTS (SELECT * FROM airline_database.adminaccount where username='"+user+"' and password='"+pwd+"');")
    d = cursor.fetchone()
    return d[0]
def passcode_exit(mysql,flight_no,date,counter):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT passcode FROM airline_database.checkincounter WHERE flight_no='"+flight_no+"' AND date='"+date+"'; ")
    d = cursor.fetchone()
    if d:   d=d[0]
    return d
def  create_passcode(mysql,flight_no,date,counter_no):
    connect=mysql.connect()
    cursor = connect.cursor()
    code = str(uuid.uuid4())[:8]
    print('passcode is',code)
    re=cursor.execute('INSERT INTO checkincounter (flight_no,date,counter_no,passcode) VALUES (%s, %s, %s,%s)',(flight_no,date,counter_no,code))
    connect.commit()
    return code

def  create_new_passcode(mysql,flight_no,date,counter_no):
    connect=mysql.connect()
    cursor = connect.cursor()
    code = str(uuid.uuid4())[:8]
    print('passcode is',code)
    re=cursor.execute("UPDATE checkincounter set counter_no="+counter_no+",passcode='"+code+"' WHERE flight_no='"+flight_no+"' and date='"+date+"';")
    connect.commit()
    return code

def get_counter_passcode(mysql,flight_no,date,counter_no):
    print('passcode exit ',passcode_exit(mysql,flight_no,date,counter_no))
    if passcode_exit(mysql,flight_no,date,counter_no):
        return create_new_passcode(mysql,flight_no,date,counter_no)
    else:
        return create_passcode(mysql,flight_no,date,counter_no)

def close_counter(mysql,flight_no,date):
    connect=mysql.connect()
    cursor = connect.cursor()
    cursor.execute("DELETE FROM checkincounter WHERE flight_no='"+flight_no+"' and date='"+date+"';")
    connect.commit()

def check_passcode(mysql,passcode):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT flight_no,date FROM airline_database.checkincounter WHERE passcode='"+passcode+"';")
    d = cursor.fetchone()
    return d

def check_in_ticket(mysql, ticket_no):
    connect=mysql.connect()
    cursor = connect.cursor()
    tim = datetime.now().strftime('%H:%M:%S')
    qury="UPDATE ticket SET check_in='"+tim+"' WHERE ticket_no="+str(ticket_no)+";"
    print(qury)
    try:
        cursor.execute(qury)
        connect.commit()
    except e:
        print(e)
        return False
    return True

def get_check_in_data(mysql,flight_no,date,checked_in=True):
    connect=mysql.connect()
    cursor = connect.cursor()
    cursor.execute("SELECT passenger,passport,ticket_no,class,check_in FROM airline_database.ticket WHERE flight_no='"+flight_no+"' and date='"+date+"' and check_in IS "+['','NOT '][checked_in]+"NULL ORDER BY check_in DESC;")
    d = cursor.fetchall()
    data=[]
    for i in range(len(d)):
        data.append({'no':i+1,'name':d[i][0],'passport':d[i][1],'ticket_no':f"{(d[i][2]):0>8}",'class':d[i][3],'time':d[i][4]})
    return data
def get_plane_price(source,desti,plane_no):
    with open("price_of_route.json", "r") as file:
        data = json.load(file)
        city_code=[desti, source][source in data]
        # print(source,desti,plane_no,data[city_code][str(plane_no)])
        result={}
        for key,value in data[city_code][str(plane_no)].items():
            result.update({key+'_price':value})
        return result
def add_price(record):
    # print(record)
    for i in range(len(record)):
        record[i].update(get_plane_price(record[i]['depart_code'],record[i]['arrive_code'],record[i]['plane_no']))
        # record[i].update({'first_price':5})
    # print(record)