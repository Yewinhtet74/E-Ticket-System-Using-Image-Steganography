
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from skimage import io
import cv2 as cv
import json
from ticket_writing import ticket_image
from bitstring import Bits
import uuid
from mycollection import get_city_data,get_date_format

def get_key(mysql):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * FROM aes")
    data = cursor.fetchone()
    cursor.close()
    # mysql.connection.commit()
    key, iv = data
    print('DATas ', type(key), iv)
    return (key,iv)

def get_new_ticket_no(mysql):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT MAX(ticket_no) FROM ticket;")
    count = cursor.fetchall()[0][0]
    cursor.close()
    # mysql.connection.commit()
    count=[count,0][count==None]
    # print('Number of ticket',count)
    return count+1
def get_new_secret_code(mysql):
    code = uuid.uuid4()
    found = check_exist_secret_code(mysql,code)
    # print('FOUND',found)
    # print(code)
    if not(found):
        # print('Code',found)
        return str(code)
    return get_new_secret_code(mysql)
    # print([code,][found])
    # return
def get_flight_info(mysql,flight_no,date):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT departure,arrival,departure_time,arrival_time,flight_time FROM route WHERE flight_no='"+flight_no+"';")
    record = cursor.fetchall()[0]
    cursor.close()

    print('time compare', record[2]<record[3],get_date_format(date),get_date_format(date,1))
    info={'depart_code':record[0],'arrive_code':record[1],'depart_name':get_city_data(record[0])['city'],'arrive_name':get_city_data(record[1])['city'],
          'depart_time':"{:0>5}".format(str(record[2])[:-3]),'arrive_time':"{:0>5}".format(str(record[3])[:-3]),'flight_time':"{:0>5}".format(str(record[4])[:-3]),
          'depart_date':get_date_format(date),'arrive_date':get_date_format(date,record[2]>record[3])}
    # print('Flight Info Record',info,)
    return info
def store_in_database(mysql,data):
    connect=mysql.connect()
    cursor = connect.cursor()
    db_dd=(data['ticket_no'],data['secret_code'],data['name'],data['passport'],data['flight_no'],data['class'],data['date'],data['email'],data['phone'])
    re=cursor.execute('INSERT INTO ticket (ticket_no,secret_code,passenger,passport,flight_no,class,date,email,phone) VALUES (%s, %s, %s,%s, %s,%s, %s,%s, %s)',db_dd)
    connect.commit()
    db_dd=(data['ticket_no'],data['key'],data['iv'])
    re=cursor.execute('INSERT INTO aes2 (ticket_no,secret_key,iv) VALUES (%s, %s, %s)',db_dd)
    connect.commit()
    print('INSERT DB',re)
    cursor.close()

def check_exist_secret_code(mysql,code):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT ticket_no,flight_no,date,check_in from ticket WHERE secret_code='"+str(code)+"';")
    found=cursor.fetchone()
    cursor.close()
    return found

def get_key_by_ticket_no(mysql,ticket_no):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT secret_key,iv from aes2 WHERE ticket_no='"+ticket_no+"';")
    found=cursor.fetchone()
    cursor.close()
    if found:
        print('FOUND',found,found[0],found[1])
        return (found[0],found[1])
    return (None,None)

def ticket_generating(mysql,data):
    print('Generating')
    #retireve key from database
    data['ticket_no']=get_new_ticket_no(mysql)
    data['secret_code']=get_new_secret_code(mysql)
    key,iv=get_key(mysql)
    key=get_random_bytes(16)
    iv=get_random_bytes(16)
    data.update({'key':key,'iv':iv})
    data.update(get_flight_info(mysql,data['flight_no'],data['date']))
    print('Th information got in generating',data)
    #db=Database()
    # dd={'name':'Win Htet ', 'passport':'MH81234', 'ticket_number':'782935', 'depart_code':'RGN', 'depart_name':'Yangon',
    #     'depart_date':'02 JUN 2024 ', 'depart_time':'07:00', 'arrive_code':'BKK', 'arrive_name':'Bangkok', 'arrive_date':'02 JUN 2024',
    #     'arrive_time':'09:00', 'flight':'9M3627', 'classs':'Economy', 'times':'1 Hr 30 Min'}
    sms=''
    # for k,d in dd.items():
    #     sms+=k+':'+d+'\n'
    sms=data['secret_code']
    #key=get_random_bytes(16)
    
    logo_size=(150,150)
    sms=bytes(sms,'utf-8')

    cipher = AES.new(key, AES.MODE_CBC,iv=iv)
    print('IV',cipher.iv)
    # cipher_text = cipher.encrypt(sms)
    cipher_text = cipher.encrypt(pad(sms, AES.block_size))
    iv = cipher.iv
    print('Key',key,'iv',iv,'Cipher text ',cipher_text)
    '''
    import json
    data = {
        'Key' : ''.join([format(i,'08b') for i in key]),
        'IV' : ''.join([format(i,'08b') for i in iv])
    }
    with open("encry_data.json", "w") as file_object:
        json.dump(data, file_object)
    '''
    logo=np.array(Image.open('images/logo.jpg'))
    logo=cv.resize(logo,logo_size)
    logo=logo[:,:,:3]
    mask = np.all(logo==[0,0,0], axis=2)
    logo[mask] = [255,255,255]


    w,h,t=logo.shape

    # cipher_text=cipher_text+'[END]'.encode()
    cipher_text='[START]'.encode()+cipher_text+str(data['ticket_no']).encode()+'[END]'.encode()
    print('Ciphter text is',cipher_text)

    mes_bit= ''.join([format(i,'08b') for i in cipher_text])

    img_f=logo.flatten()

    for ind,bit in enumerate(mes_bit):
        v=bin(img_f[ind])
        # print(ind,img_f[ind],v,['N','Y'][v[-1]==bit],end=' ')
        v=v[:-1]+bit
        img_f[ind]=int(v,2)
        # print(img_f[ind],v,bit)
    logo= img_f.reshape((w,h,t))

    # plt.imshow(img2,cmap='gray')

    #evoucher[450:450+400,100:100+400]=img2
    # io.imshow(evoucher)

    # evoucher=ticket_image(name=dd['name'], passport=dd['passport'], ticket_number=dd['ticket_number'], depart_code=dd['depart_code'],
    #                       depart_name=dd['depart_name'], depart_date=dd['depart_date'], depart_time=dd['depart_time'],
    #                       arrive_code=dd['arrive_code'], arrive_name=dd['arrive_name'], arrive_date=dd['arrive_date'],
    #                       arrive_time=dd['arrive_time'], flight=dd['flight'], classs=dd['classs'], times=dd['times'])
    evoucher=ticket_image(data)
    # io.imshow(evoucher)
    evoucher=np.array(evoucher)
    evoucher[60:60+logo_size[0],60:60+logo_size[1]]=logo
    e_ticket= Image.fromarray(evoucher)
    # print('type of evoucher',type(e_ticket))
    store_in_database(mysql,data)
    
    return evoucher
    # io.imsave('images/tickets/try.png',evoucher)

def ticket_verification(img,mysql):
    width=900;height=800
    logo_size=(150,150)
    print('type of img',type(img))
    img=Image.open(img)
    (w,h)=img.size
    if w!=width or h!=height:
        print('Ticket has wrong format')
        return 0
    img=np.array(img)
    print('type of img2',type(img),'shape of img',img.shape)
    img=img[60:60+logo_size[0],60:60+logo_size[1]]
    
    msg=''
    ixd=0
    img_f=img.flatten()
    bbit=[]

    ms=''
    while ms[-7:]!='[START]' and ixd<=img_f.shape[0]-8:
        bits=[bin(i)[-1] for i in img_f[ixd:ixd+8]]
        bits=''.join(bits)
        bbit.append(bits)
        ms+=bits
        ii=ms[-8*7:]
        end=''
        for i in range(0,len(ii),8):
            end+=chr(int(ii[i:i+8],2))
        if end=='[START]':print('break');break
        #msg+=chr(int(bits,2))
        ixd+=8
    ixd+=8
    if ixd>=img_f.shape[0]:
        print('Ticket didnt have data')
        return 0
    while msg[-5:]!='[END]' and ixd<=img_f.shape[0]-8:
        bits=[bin(i)[-1] for i in img_f[ixd:ixd+8]]
        bits=''.join(bits)
        bbit.append(bits)
        msg+=bits
        ii=msg[-8*5:]
        end=''
        for i in range(0,len(ii),8):
            end+=chr(int(ii[i:i+8],2))
        if end=='[END]':print('break');break
        #msg+=chr(int(bits,2))
        ixd+=8
    #print('message from image',msg)
        # print('Cihter text start',msg[:7])
        # if msg[:7]!='[START]':
        #     print('Ticket has no START')
        #     return 0

    sss=msg[:-8*5]
    # def bitstring_to_bytes(s):
    #     v = int(s, 2)
    #     b = bytearray()
    #     while v:
    #         b.append(v & 0xff)
    #         v >>= 8
    #     return bytes(b[::-1])
    #sss=bitstring_to_bytes(sss)
    sss=bytes(int(sss[i : i + 8], 2) for i in range(0, len(sss), 8))
    print('MESSAGE BACK',sss,)
    ticket_no=str(sss[48:], encoding='utf-8')
    sss=sss[:48]
    print('ticket no',ticket_no,'sss',sss)
    '''
    data=json.load(open('encry_data.json','r'))
    key=bytes(int(data['Key'][i : i + 8], 2) for i in range(0, len(data['Key']), 8))
    iv=bytes(int(data['IV'][i : i + 8], 2) for i in range(0, len(data['IV']), 8))
    key, iv = get_key(mysql)
    '''
    (key,iv)=get_key_by_ticket_no(mysql,ticket_no)
    if key==None or iv==None: return 0
    
    decrypt_cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    print('Key',key,'iv',iv,'Cipher text ',sss)
    try:
        sms_back = decrypt_cipher.decrypt(sss).decode()
        # print(sms_back)
        sms_back=sms_back.strip()
        print('SMS is',sms_back,len(sms_back))
    except:
        print('Undecodable cipher')
        return 0
    f=check_exist_secret_code(mysql,sms_back)
    print('Secret code found in ticket number',f)
    return f
    
