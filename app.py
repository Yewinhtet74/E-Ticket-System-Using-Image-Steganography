from flask import Flask,render_template,redirect,request,session,send_file
import ticket_center as ims
from PIL import Image
import io
import re
import flask as flask
import mycollection as cols
from mycollection import allowed_file,get_airport_data,search_flight,get_a_flight,get_all_flight_no,check_admin_account,get_counter_passcode,\
    close_counter,check_passcode,check_in_ticket,get_check_in_data,add_price,find_counter,get_date_format
import test as tst
from ticket_writing import ticket_image
from flaskext.mysql import MySQL
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
print('Reach app file')
app.secret_key='yeair'

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'airline_database'

mysql = MySQL(app)

@app.route('/')
def index():  # put application's code here
    dis={}
    dis['airport']=get_airport_data()
    dis['start_date'] = datetime.now().date() +relativedelta(days=1)
    dis['end_date'] = datetime.now().date() + relativedelta(months=2,days=1)
    # return render_template('index.html')
    return render_template('home.html',data=dis)
    # return redirect('/findflight')
def get_session_user():
    if session and session.get('admin_username'):
        return session.get('admin_username')
    return None
@app.route('/admin')
def admin():
    if get_session_user():
        return redirect('/admin/dashboard')
    return redirect('/admin/login')
@app.route('/admin/login',methods=['POST','GET'])
def admin_login():
    dis={}
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if check_admin_account(mysql,username,password):
            session['admin_username'] = username
            return redirect('/admin/counter')
        dis={'username_err':'Username may not exists!','password_err':'Password may incorrect!'}
    return render_template('admin_login.html',data=dis)

@app.route('/findcounter', methods=['POST','GET'])
def findcounter():
    dis={}
    if request.method=='POST':
        dis['response']=True
        if 'ticket' not in request.files:
            print('Error',request.files)
            return redirect('/')
        ticket = request.files['ticket']
        if ticket.filename == '':
            print('No selected file')
            return redirect('/')
        if not(ticket and allowed_file(ticket.filename)):
            dis['status'] = False
            dis['info'] = 'Invalid file!'
            dis['info2'] = 'Please try with the original ticket.'
            return render_template('findcounter.html', data=dis)
        in_ticket=ims.ticket_verification(ticket,mysql=mysql)#tk_no,fgh_no,date
        if not(in_ticket):
            dis['status'] = False
            dis['info'] = 'Invalid ticket!'
            dis['info2'] = 'Please try with the original ticket.'
            return render_template('findcounter.html', data=dis)
        print('IN Ticket',in_ticket,in_ticket[1],in_ticket[2])
        cc=find_counter(in_ticket[1],str(in_ticket[2]),mysql)
        dis.update({'flight_no':in_ticket[1],'flight_date':get_date_format(str(in_ticket[2]))})
        print('REsult cc ',cc)
        if cc:
            dis['response']=False
            dis['status']=True
            dis.update(cc)
        else:
            dis['response']=False
            dis['status']=True
            dis['counter']=False
        print('DATAs',dis)
    return render_template('findcounter.html',data=dis)
@app.route('/notice')
def notice():
    dis={}
    return render_template('notice.html',data=dis)
@app.route('/about')
def about():
    dis={}
    return render_template('about.html',data=dis)
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_username',False)
    return redirect('/admin')

@app.route('/admin/dashboard', methods=['POST','GET'])
def admin_dashboard():
    data={}
    if not(get_session_user()):
        return redirect('/admin/login')
    if request.method=='POST':
        flight_no=request.form['flight_no']
        date=request.form['date']
        uncheck_in_data=get_check_in_data(mysql,flight_no,date,checked_in=False)
        checked_in_data=get_check_in_data(mysql,flight_no,date,checked_in=True)
        print('CHECK IN DATA',uncheck_in_data,checked_in_data,uncheck_in_data==[])
        data['uncheck_in_data']=uncheck_in_data
        data['checked_in_data']=checked_in_data
        data['flight_no']=flight_no
        data['date']=date
    data['flights']=get_all_flight_no(mysql)
    data['date_now'] = datetime.now().date()
    data['admin_username']=get_session_user()
    return render_template('admin_dashboard.html',data=data)
@app.route('/admin/counter', methods=['POST','GET'])
def admin_counter():
    data={}
    if not(get_session_user()):
        return redirect('/admin/login')
    if request.method=='POST':
        flight_no=request.form['flight_no']
        date=request.form['date']
        counter_no=request.form['counter']
        # print('Counter data',flight_no,date,counter_no)
        data['passcode']=get_counter_passcode(mysql,flight_no,date,counter_no)
        data['flight_no']=flight_no
        data['date']=date
        data['counter_no']=counter_no

        data['flight']=get_a_flight(mysql,flight_no,date)
        # print(data['flight'])

    data['flights']=get_all_flight_no(mysql)
    data['date_now'] = datetime.now().date()
    data['admin_username']=get_session_user()
    return render_template('admin_counter.html',data=data)

@app.route('/admin/close_counter/<flight_no>/<date>')
def admin_close_counter(flight_no,date):
    d=close_counter(mysql,flight_no,date)
    print('Delete check in',d)
    return redirect('/admin/counter')
@app.route('/checkin',methods=['POST','GET'])
def check_in():
    dis={}
    if request.method=='POST':
        dis['response']=True
        if 'ticket' not in request.files:
            print('Error')
            return redirect('/')
        print('Request.Files',request.files)
        ticket = request.files['ticket']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if ticket.filename == '':
            print('No selected file')
            return redirect('/')
        if not(ticket and allowed_file(ticket.filename)):
            dis['status'] = False
            dis['info'] = 'Invalid file!'
            dis['info2'] = 'Please upload the original ticket.'
            return render_template('check_in.html', data=dis)
        passcode=request.form['passcode']
        in_ticket=ims.ticket_verification(ticket,mysql=mysql)#tk_no,fgh_no,date
        if not(in_ticket):
            dis['status'] = False
            dis['info'] = 'Invalid ticket!'
            dis['info2'] = 'Please upload the original ticket.'
            return render_template('check_in.html', data=dis)
        if in_ticket[3]!=None:
            dis['status'] = False
            dis['info'] = 'Your ticket already checked in!'
            dis['info2'] = 'Please return to counter staff.'
            return render_template('check_in.html', data=dis)
        dd=check_passcode(mysql,passcode)#fgh_no,date
        print('Just checking',in_ticket,dd)
        if not(dd):
            dis['status'] = False
            dis['info'] = 'Passcode unavailable!'
            dis['info2'] = 'Please enter the right passcode at the counter.'
            return render_template('check_in.html', data=dis)
        if in_ticket[1]!=dd[0]:
            dis['status'] = False
            dis['info'] = 'You are on the wrong counter!'
            dis['info2'] = 'Please move to the right counter.'
            return render_template('check_in.html', data=dis)
        if in_ticket[2]!=dd[1]:
            dis['status'] = False
            dis['info'] = 'Flight date are wrong!'
            dis['info2'] = 'Please double check the flight date.'
            return render_template('check_in.html', data=dis)
        res=check_in_ticket(mysql,in_ticket[0])
        print('Check in successful?',res)
        if not(res):
            dis['status'] = False
            dis['info'] = 'There is an error in check in process!'
            dis['info2'] = 'Please contact the counter staff.'
            return render_template('check_in.html', data=dis)
        dis['status']=True
        dis['info']='You have been checked in successfully!'
        dis['info2']='Please return to counter staff.'
        return render_template('check_in.html',data=dis)
    return render_template('check_in.html',data=dis)

@app.route('/findflight', methods=['POST','GET'])
def find_flight():  # put application's code here
    # return render_template('index.html')
    dis={}
    if request.method=='POST':
        data={}
        data['depart']=request.form['depart']
        data['arrive']=request.form['arrive']
        data['date']=request.form['date']
        data['class']=request.form['class']
        print('FORM DATA', data)
        dis.update(data)
        record=search_flight(mysql,data)
        add_price(record)
        print('ROUTES',record,type(record)==list)
        dis['routes']=record
    dis['airport']=get_airport_data()
    dis['start_date'] = datetime.now().date() +relativedelta(days=1)
    dis['end_date'] = datetime.now().date() + relativedelta(months=2,days=1)
    print('DATAss',dis)
    return render_template('route.html',data=dis)

@app.route('/first_step/<flight_no>/<depart_date>/<clas>/<price>', methods=['POST','GET'])
def first_step(flight_no,depart_date,clas,price):
    print(flight_no,depart_date,clas)
    dis=get_a_flight(mysql,flight_no,depart_date)
    dis['flight_no']=flight_no
    dis['depart_date']=depart_date
    dis['class']=clas
    dis['price']=price
    return render_template('first_step.html',data=dis)

@app.route('/final_step/<flight_no>/<depart_date>/<clas>/<price>', methods=['POST'])
def final_step(flight_no,depart_date,clas,price):
    #check passport len
    print(flight_no,depart_date,clas)
    dis=get_a_flight(mysql,flight_no,depart_date)
    dis['flight_no']=flight_no
    dis['depart_date']=depart_date
    dis['class']=clas
    dis['price']=price
    if request.method=='POST':
        dis['name']=request.form['name']
        dis['passport']=request.form['passport']
        dis['email']=request.form['email']
        dis['phone']=request.form['phone']
        print('Info',dis)
        # if not  re.match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', ):

        #return redirect('/first_step/'+dis['flight_no']+'/'+dis['depart_date']+'/'+dis['class']+'/'+dis['price'])
    return render_template('final_step.html',data=dis)


@app.route('/get_ticket', methods=['POST','GET'])
def get_ticket():
    if request.method != 'POST':
        return redirect('/')
    data = {}
    data['name'] = request.json.get('passenger_name')
    data['passport'] = request.json.get('passport')
    data['email'] = request.json.get('email')
    data['phone'] = request.json.get('phone_no')
    data['flight_no'] = request.json.get('flight_no')
    data['date'] = request.json.get('date')
    data['class'] = request.json.get('class')
    print('Th information got ', data)
    ticket = ims.ticket_generating(mysql=mysql, data=data)
    print('type of ticket', type(ticket))
    e_ticket = Image.fromarray(ticket)
    output = io.BytesIO()
    e_ticket.save(output, format='PNG')
    image_data = output.getvalue()

    # Validate image data (implement your validation logic)

    response = flask.make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    response.headers['Content-Disposition'] = 'attachment; filename=E_tcket.png'  # Example filename
    return response
    # return redirect('/')


@app.route('/get_ticket2', methods=['POST','GET'])
def get_ticket2():
    print('1111111111',request.json.get('passenger_name'))
    data = {}
    data['name'] = ''
    data['passport'] = ''
    data['email'] = 'gf'
    data['phone'] = '0'
    data['flight_no'] = 'YE0101'
    data['date'] = '2024-03-01'
    data['class'] = 'Business'
    print('Th information got ', data)
    # ticket = ims.ticket_generating(mysql=mysql, data=data)
    # print('type of ticket', type(ticket))
    # e_ticket = Image.fromarray(ticket)
    # output = io.BytesIO()
    # e_ticket.save(output, format='PNG')
    # image_data = output.getvalue()

    # Validate image data (implement your validation logic)

    # response = flask.make_response(image_data)
    # response.headers['Content-Type'] = 'image/png'
    # response.headers['Content-Disposition'] = 'attachment; filename=E_tcket.png'  # Example filename
    # return response
    # return redirect('/')


@app.route('/upload', methods=['POST'])
def upload_file():
    print('in upload file')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect('/')
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            # flash('No selected file')
            return redirect('/')
        if file and allowed_file(file.filename):
            res=ims.ticket_verification(file,mysql=mysql)
            print('Ticket is',['NO','YES'][res])
            return redirect('/')
        
if __name__ == '__main__':
    app.run(debug=False, threaded=True)
