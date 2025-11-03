from flask import Flask
import os
from dotenv import load_dotenv
import pyodbc

# Load .env variables
load_dotenv()

# Read DB configs
SERVER = os.getenv("MSSQL_SERVER", r"localhost\SQLEXPRESS")
DATABASE = os.getenv("MSSQL_DATABASE", "connection_db")
TRUSTED = os.getenv("MSSQL_TRUSTED_CONNECTION", "yes").lower() in ("1", "true", "yes")
#print(SERVER,DATABASE,TRUSTED,a)

# Build connection string
if TRUSTED:
    CONN_STR = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
        )
else:
    # Use if you have SQL login credentials instead of Windows Authentication
    USERNAME = os.getenv("MSSQL_USERNAME")
    PASSWORD = os.getenv("MSSQL_PASSWORD")
    CONN_STR = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};"
        "Encrypt=yes;TrustServerCertificate=yes;"
    )

def connect_to_mssql():
    """Create and return a new DB connection"""
    try:
        conn = pyodbc.connect(CONN_STR)
        print("✅ MSSQL connection established successfully.")
        return conn
    except Exception as e:
        print("❌ Failed to connect to MSSQL:", e)
        raise