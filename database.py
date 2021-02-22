# This file deals with interaction between the postgres database hosted in Amazon RDS
# Here we will create fucntions that can query and add records

import psycopg2
import os
import uuid
from dotenv import load_dotenv

load_dotenv()  # loading the .env file

# creating variables for our creditentials which are needed to establish a database connection
database_endpoint = os.getenv("DATABASE_ENDPOINT")
database_port = os.getenv("DATABASE_PORT")
database_name = os.getenv("DATABASE_NAME")
database_user = os.getenv("DATABASE_USER")
database_password = os.getenv("DATABASE_PASSWORD")

# The following function creates our database in postgres
def create_db():
    print("Creating connection to Postgres")
    conn = psycopg2.connect(
        user=database_user,
        password=database_password,
        dbname="postgres",  # connect to the default database before creating our own database
        host=database_endpoint,
        port=database_port,
    )
    conn.autocommit = True  # This is required or CREATE DATABASE statement will not work. It makes sure the database is 'saved' and not deleted

    cur = conn.cursor()  # We need a cursor to conduct database operations/queries

    print(f"Checking if database {database_name} already exists.")

    # This query is checking if the database exists. The results are stored in the cursor until you fetch them
    cur.execute(
        f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{database_name}'"
    )

    # fetchall() fetches all the rows of a query result. An empty list is returned if there is no record to fetch the cursor
    exists = cur.fetchall()

    # if exists is empty then create the database
    if not exists:
        print("Database does not exist, executing create database statement.")
        cur.execute(f"CREATE DATABASE {database_name}")

    cur.close()  # exit the cursor
    conn.close()  # close the connection


# The following function creates a table in our database.
def create_tables():
    print("Creating connection to Postgres")
    conn = psycopg2.connect(
        user=database_user,
        password=database_password,
        dbname=database_name,  # connect to the database we created previously through the database name
        host=database_endpoint,
        port=database_port,
    )

    cur = conn.cursor()

    print("Creating meetings table if it doesn't exist.")
    cur.execute(
        f"DROP TABLE IF EXISTS meetings"
    )  # Remove this after testing is complete(keep it just so we dont have to always drop the table to make changes)
    cur.execute(
        f"""CREATE TABLE IF NOT EXISTS meetings (
        meeting_id VARCHAR ( 255 ) PRIMARY KEY,
        title VARCHAR ( 255 ) NOT NULL,
        user_id VARCHAR ( 255 ) NOT NULL,
	    server_id VARCHAR ( 255 ) NOT NULL,
        channel_id VARCHAR ( 255 ) NOT NULL,
	    time TIMESTAMP NOT NULL,
        cancelled BOOLEAN NOT NULL
    )"""
    )  # query to create the table

    conn.commit()
    cur.close()
    conn.close()


# init_db function will be used in bot.py at start up. This means we can call a single.function in the bot.py file that runs the above two functions.
# We can add more function to this if needed.
def init_db():
    create_db()
    create_tables()


# Next:


# function to add meeting records to the table (using SQL queries)
# e.g def add_meeting(title, user_id, server_id, channel_id, time, cancelled):
# meeting_id = uuid.uuid4()  # Create a unique value for meeting_id
def add_meeting(title, user_id, server_id, channel_id, time, cancelled):
    
    conn = psycopg2.connect(
        user=database_user,
        password=database_password,
        dbname=database_name,  
        host=database_endpoint,
        port=database_port,
    )
    meeting_id = uuid.uuid4()
    cur = conn.cursor()
    postgres_insert_query = """INSERT INTO meetings (meeting_id,title, user_id, server_id, channel_id, time, cancelled,) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
    record_to_insert = (meeting_id,title, user_id, server_id, channel_id, time, cancelled)
    cur.execute(postgres_insert_query, record_to_insert)

    conn.commit()
    cur.close()
    conn.close()
#https://pynative.com/python-postgresql-insert-update-delete-table-data-to-perform-crud-operations/


# function to remove meeting records from the table
# .e.g def cancel_meeting(title, user_id, server_id, channel_id, time, cancelled):

# function to lookup meeting records in the table