from flask import Flask, request, jsonify, send_file
import pandas as pd
import json
import os
from flask_cors import CORS
from dotenv import load_dotenv
import mysql.connector as conn
from io import BytesIO

load_dotenv()

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DB"),
}

zomatoreviewschema = [
    "Place ID",
    "User Name",
    "Timestamp",
    "Rating",
    "Review Text",
    "Like Count",
    "Comment Count",
    "Review URL",
    "User Profile URL",
]



def zomatoreviewscolumncheck(columnsofuploadedfile):
    uploaded_columns = set(columnsofuploadedfile)
    expected_columns = set(zomatoreviewschema)

    missing_columns = expected_columns - uploaded_columns
    extra_columns = uploaded_columns - expected_columns

    if not missing_columns and not extra_columns:
        return True, None

    if missing_columns and not extra_columns:
        response_data = {
            "error": "Missing columns in the uploaded file.",
            "missing_columns": list(missing_columns),
        }
        return False, response_data

    if extra_columns and not missing_columns:
        response_data = {
            "warning": "Extra columns found and will be dropped.",
            "extra_columns": list(extra_columns),
        }
        return False, response_data

    else:
        response_data = {
            "missing_columns": list(missing_columns),
            "extra_columns": list(extra_columns),
        }
        return False, response_data


def zomreviewduplicatecheck(chunk):
    entire_duplicated_rows = chunk[chunk.duplicated(keep=False)]
    drop3 = chunk.drop_duplicates(keep="first")

    response_data = {"duplicate_rows": entire_duplicated_rows.index.tolist()}
    
    filtered_response_data = {
        key: value for key, value in response_data.items() if value
    }
    
    if not filtered_response_data:
        filtered_response_data = None
        
    print(response_data)
    return drop3, filtered_response_data


def zreviewsmandatoarycolumncheck(chunk):
    nullplaceid = chunk.index[chunk["Place ID"].isna()].tolist()
    nullreviewurl = chunk.index[chunk["Review URL"].isna()].tolist()
    nulluserprofileurl = chunk.index[chunk["User Profile URL"].isna()].tolist()

    
    response_data = {
        "nullplaceid": nullplaceid,
        "nullreviewurl": nullreviewurl,
        "nulluserprofileurl": nulluserprofileurl
    }
    filtered_response_data = { key: value for key, value in response_data.items() if value}
    
    if not filtered_response_data:
        filtered_response_data = None
    
    return filtered_response_data


def zomreviewnullvaluehandle(drop3):
    drop3["Place ID"] = drop3["Place ID"].fillna("Missing")
    drop3["User Name"] = drop3["User Name"].fillna("Unknown")
    drop3["Timestamp"] = drop3["Timestamp"].fillna("Unknown")
    drop3["Rating"] = drop3["Rating"].fillna(0.0)
    drop3["Review Text"] = drop3["Review Text"].fillna("N/A")
    drop3["Like Count"] = drop3["Like Count"].fillna(0)
    drop3["Comment Count"] = drop3["Comment Count"].fillna(0)
    drop3["Review URL"] = drop3["Review URL"].fillna("N/A")
    drop3["User Profile URL"] = drop3["User Profile URL"].fillna("N/A")

    return drop3


def create_zomato_review_table(drop3, MYSQL_CONFIG, tablename):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {tablename} (
     placeid VARCHAR(255) NOT NULL,
     username VARCHAR(255)  NOT NULL,
     timestamp VARCHAR(255)  NOT NULL,
     rating DECIMAL(3,2) DEFAULT 0.0,
     reviewtext TEXT,
     likecount INT DEFAULT 0,
     commentcount INT DEFAULT 0,
     reviewURL VARCHAR(255) DEFAULT 'N/A',
     userprofileURL VARCHAR(255) DEFAULT 'N/A'
);
    """

    try:
        db = conn.connect(
            host=MYSQL_CONFIG["host"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
            connection_timeout=600,
        )
        cursor = db.cursor()
        cursor.execute(create_table_query)

        db.commit()
        cursor.close()
        db.close()
        print("Table created successfully")
    except conn.Error as err:
        print(f"Error creating table: {err}")


def insert_data_to_mysql_zomatoreview(drop3, MYSQL_CONFIG, tablename):
    try:
        create_zomato_review_table(drop3, MYSQL_CONFIG, tablename)

        db = conn.connect(
            host=MYSQL_CONFIG["host"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
            connection_timeout=600,
        )

        cursor = db.cursor()
        cursor.execute("SET GLOBAL max_allowed_packet = 200 * 1024 * 1024;")
        cursor.execute("SET GLOBAL net_read_timeout = 600;")
        cursor.execute("SET GLOBAL net_write_timeout = 600;")
        insert_query = f"""
        INSERT INTO {tablename}(
            placeid,username,timestamp,rating,reviewtext,likecount,commentcount,reviewurl,userprofileURL
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = []

        for index, row in drop3.iterrows():
            data.append(
                (
                    row["Place ID"],
                    row["User Name"],
                    row["Timestamp"],
                    row["Rating"],
                    row["Review Text"],
                    row["Like Count"],
                    row["Comment Count"],
                    row["Review URL"],
                    row["User Profile URL"],
                )
            )

        cursor.executemany(insert_query, data)
        db.commit()
        cursor.close()
        db.close()

        print("Data inserted successfully into MySQL database.")
        return {"message": "Data Successfully saved to DB"}

    except conn.Error as err:
        print(f"Error: {err}")
        return {"error": str (err)}
