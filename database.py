# This file deals with interaction between the postgres database hosted in Amazon RDS and the bot.py file.
# Here we will create functions containing SQL queries that will be used to add, cancel and lookup meetings.

# import libraries
import psycopg2
import psycopg2.extras
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime, timedelta

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

    cur = conn.cursor()  # We need a cursor to conduct transactional database operations/queries

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
	#establish a connection the the database
    print("Creating connection to Postgres") # prints to the logs
    conn = psycopg2.connect(
        user=database_user,
        password=database_password,
        dbname=database_name,  # connect to the database we created previously through the database name
        host=database_endpoint,
        port=database_port,
    )

    cur = conn.cursor()   #create our cursor which will be used to execute transactional queries

    print("Creating meetings table if it doesn't exist.") # prints to the logs
    # cur.execute(
    #     f"DROP TABLE IF EXISTS meetings"
    # )  # Remove this after testing is complete(keep it just so we dont have to always drop the table to make changes)
    cur.execute(
        f"""CREATE TABLE IF NOT EXISTS meetings (
        meeting_id VARCHAR ( 255 ) PRIMARY KEY,
        title VARCHAR ( 255 ) NOT NULL,
        user_id VARCHAR ( 255 ) NOT NULL,
	    server_id VARCHAR ( 255 ) NOT NULL,
        channel_id VARCHAR ( 255 ) NOT NULL,
	    start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL,
        cancelled BOOLEAN NOT NULL
    )"""
    )  # query to create the table

    conn.commit() # commit the query to the database
    cur.close() # close the cursor
    conn.close() # close the connection


# init_db function will be used in bot.py at start up. This means we can call a single function in bot.py that runs the following two functions.
def init_db():
    create_db()
    create_tables()


# Function to add meeting records to the table (using SQL queries)
def add_meeting(title, user_id, server_id, channel_id, start_time, end_time, cancelled):
	#establish a connection the the database
    conn = psycopg2.connect(
        user=database_user,
        password=database_password,
        dbname=database_name,
        host=database_endpoint,
        port=database_port,
    )

    meeting_id = uuid.uuid4()  # Create a unique value for meeting_id
    start_time_str = start_time.isoformat() # string representation of time
    end_time_str = end_time.isoformat() # string representation of time
    psycopg2.extras.register_uuid()  # register the uuid

    cur = conn.cursor()  #create our cursor which will be used to execute transactional queries
    postgres_insert_query = f"INSERT INTO meetings (meeting_id, title, user_id, server_id, channel_id, start_time, end_time, cancelled) VALUES ('{meeting_id}','{title}','{user_id}','{server_id}','{channel_id}','{start_time_str}','{end_time_str}',{cancelled})"
    cur.execute(postgres_insert_query) # execute the query using the cursor

    conn.commit() # commits the query to the database 
    print("Record inserted successfully into database") # prints to logs
    cur.close()  # close the cursor
    conn.close() # close the connection


# Function to remove cancelled meetings - check if deleted or update cancel
def cancel_meeting(title, user_id, server_id, start_time):
	#establish a connection the the database
    conn = psycopg2.connect(
        user=database_user,
        password=database_password,
        dbname=database_name,
        host=database_endpoint,
        port=database_port,
    )
    cur = conn.cursor() # create our cursor which will be used to execute transactional queries
    query = f"UPDATE meetings SET cancelled = TRUE WHERE title = '{title}' and start_time='{start_time}'"
    cur.execute(query) # execute the query using the cursor
    rows_affected = cur.rowcount  # return the number of rows returened from the query 
    conn.commit() # commits the query to the database 
    print(f"Cancelled meeting {title} {start_time}") 
    cur.close() # close the cursor
    conn.close() # close the connection
    return rows_affected


# Function to lookup meeting records in the table for a specific user, we can use this to lookup meetings by day, month or week as we simply need to supply the end date in the bot.py file.
def lookup_meeting_by_date_window(user_id, server_id, start_date, end_date):
#establish a connection the the database
    conn = psycopg2.connect(
        user=database_user,
        password=database_password,
        dbname=database_name,
        host=database_endpoint,
        port=database_port,
    )

    
    cur = conn.cursor() # create our cursor which will be used to execute transactional queries
    query = f"SELECT title,start_time,end_time FROM  meetings WHERE start_time>'{start_date}' and start_time<'{end_date}' and cancelled=false and user_id='{user_id}' and server_id='{server_id}'"
    cur.execute(query) # execute the query using the cursor
    records = cur.fetchall()  # return query results as a list 
    conn.commit() # commits the query to the database 
    cur.close() # close the cursor
    conn.close()  # close the connection
    return records


# Function to lookup meeting records in the table for all users, this will be used for the notification function in bot.py, we are not looking up a specific user here because..
# the notification function will run for all users every minute, hence we don't lookup the user_id in the the SQL query.
def lookup_all_meetings_by_date_window(start_date, end_date):
#establish a connection the the database
    conn = psycopg2.connect(
        user=database_user,
        password=database_password,
        dbname=database_name,
        host=database_endpoint,
        port=database_port,
    )
	
    cur = conn.cursor() # create our cursor which will be used to execute transactional queries
    # define an SQL query
    query = f"SELECT title,start_time,end_time,user_id FROM  meetings WHERE start_time>'{start_date}' and start_time<'{end_date}' and cancelled=false"
    cur.execute(query) # execute the query using the cursor
    records = cur.fetchall() # return query results as a list 
    conn.commit()  # commits the query to the database 
    cur.close() # close the cursor
    conn.close() # close the connection
    return records
