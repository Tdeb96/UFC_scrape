import pandas as pd
from sqlalchemy import create_engine
import mysql.connector as mysql
import pymysql

#mysql password
passw = ""

#Import the data from Data_cleaning
fights = pd.read_csv('./Data/20201207fights.csv')
athletes = pd.read_csv('./Data/20201207athletes.csv')


#Establish connection
connection = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = passw
)

#Create cursor class, used to execute SQL statements
cursor = connection.cursor()

# Create a new database named "UFC"
cursor.execute("CREATE DATABASE UFC")

#Used to write the data to SQL in one go
engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                       .format(user="root",
                               pw=passw,
                               db="UFC"))

#Append the pandas dataframes to the SQL database
fights.to_sql('fights', con = engine, if_exists = 'append', chunksize = 1000, index = False)
athletes.to_sql('athletes', con = engine, if_exists = 'append', chunksize = 1000, index = False)
