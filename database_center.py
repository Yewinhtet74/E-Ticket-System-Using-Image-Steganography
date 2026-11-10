
'''
from flaskext.mysql import MySQL
mysql = MySQL()
mysql.init_app(app)
cursor = mysql.get_db().cursor()

import pandas as pd

import numpy as np
import mysql.connector as sql
class Database:
    def __init__(self):
        db=sql.connect(host='localhost',user='root',password='root',database='airline_database')
        if db.is_connected:
            print('Database Connected Successfully')
    
#cursor = db.cursor()
            
db=Database()
'''