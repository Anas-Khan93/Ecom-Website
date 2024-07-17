import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

dataBase = mysql.connector.connect(
    
     host= os.getenv("HOST", default=""),
     user = os.getenv("USER", default=""),
    passwd = os.getenv("PASSWORD", default="")
)

cursorObject = dataBase.cursor()

cursorObject.execute("CREATE DATABASE interviewaiDB")

print("DATABASE CREATED !")