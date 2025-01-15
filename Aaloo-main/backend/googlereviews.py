from flask import Flask, request, jsonify, send_file
import pandas as pd
import json
import os
from flask_cors import CORS
from dotenv import load_dotenv
import mysql.connector as conn
from io import BytesIO
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

load_dotenv()

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DB"),
}
googlereviewschema = [
    "Place ID",
    "Rating",
    "Review",
    "Review ID",
    "Food Rating",
    "Published At",
    "Reviewer Name",
    "Is Local Guide",
    "Service Rating",
    "Reviewer Profile",
    "Published At Date",
    "Atmosphere Rating",
    "Review Likes Count",
    "Total Photos by Reviewer",
    "Total Reviews by Reviewer",
]

def googlereviewscolumncheck(columnsofuploadedfile):
    uploaded_columns = set(columnsofuploadedfile)
    expected_columns = set(googlereviewschema)

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


def greviewsmandatoarycolumncheck(chunk):
    nullplaceid = chunk.index[chunk["Place ID"].isna()].tolist()
    nullreviewid = chunk.index[chunk["Review ID"].isna()].tolist()
    nullreviewerprofile = chunk.index[chunk["Reviewer Profile"].isna()].tolist()
   
    
    response_data = {
        "nullplaceid": nullplaceid,
        "nullreviewid": nullreviewid,
        "nullreviewerprofile": nullreviewerprofile
    }
    filtered_response_data = { key: value for key, value in response_data.items() if value}
    
    if not filtered_response_data:
        filtered_response_data = None
    
    return filtered_response_data


def googlereviewduplicatecheck(chunk):
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


def googlereviewnullvaluehandle(drop3):
    drop3["Place ID"] = drop3["Place ID"].fillna("Missing")
    drop3["Rating"] = drop3["Rating"].fillna(0.0)
    drop3["Review"] = drop3["Review"].fillna("N/A")
    drop3["Review ID"] = drop3["Review ID"].fillna("N/A")
    drop3["Food Rating"] = drop3["Food Rating"].fillna(0.0)
    drop3["Published At"] = drop3["Published At"].fillna("N/A")
    drop3["Reviewer Name"] = drop3["Reviewer Name"].fillna("Unknown")
    drop3["Is Local Guide"] = drop3["Is Local Guide"].fillna(False)
    drop3["Service Rating"] = drop3["Service Rating"].fillna(0.0)
    drop3["Reviewer Profile"] = drop3["Reviewer Profile"].fillna("N/A")
    drop3["Published At Date"] = drop3["Published At Date"].fillna("N/A")
    drop3["Atmosphere Rating"] = drop3["Atmosphere Rating"].fillna(0.0)
    drop3["Review Likes Count"] = drop3["Review Likes Count"].fillna(0)
    drop3["Total Photos by Reviewer"] = drop3["Total Photos by Reviewer"].fillna(0)
    drop3["Total Reviews by Reviewer"] = drop3["Total Reviews by Reviewer"].fillna(0)

    return drop3


def create_google_review_table(drop3, MYSQL_CONFIG, tablename):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {tablename} (
     placeid VARCHAR(255) NOT NULL,
     rating DECIMAL(3,2) DEFAULT 0.0,
     review TEXT,
     reviewid VARCHAR(255) DEFAULT 'N/A',
     foodrating DECIMAL(3,2) DEFAULT 0.0,
     publishedat VARCHAR(255) DEFAULT 'N/A',
     reviewername VARCHAR(255) DEFAULT 'Unknown',
     islocalguide BOOLEAN DEFAULT FALSE,
     servicerating DECIMAL(3,2) DEFAULT 0.0,
     reviewerprofile VARCHAR(255) DEFAULT 'N/A',
     publishedatdate VARCHAR(255) DEFAULT 'N/A',
     atmosphererating DECIMAL(3,2) DEFAULT 0.0,
     reviewlikescount INT DEFAULT 0,
     totalphotosbyreviewer INT DEFAULT 0,
     totalreviewsbyreviewer INT DEFAULT 0

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


def insert_data_to_mysql_googlereview(drop3, MYSQL_CONFIG, tablename):
    try:
        create_google_review_table(drop3, MYSQL_CONFIG, tablename)

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
            placeid,rating,review,reviewid,foodrating,publishedat,reviewername,islocalguide,servicerating,reviewerprofile,publishedatdate,atmosphererating,reviewlikescount,totalphotosbyreviewer,totalreviewsbyreviewer
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = []
        #inserting into sql database from each row of the sheet
        for index, row in drop3.iterrows():
            data.append(
                (
                    row["Place ID"],
                    row["Rating"],
                    row["Review"],
                    row["Review ID"],
                    row["Food Rating"],
                    row["Published At"],
                    row["Reviewer Name"],
                    row["Is Local Guide"],
                    row["Service Rating"],
                    row["Reviewer Profile"],
                    row["Published At Date"],
                    row["Atmosphere Rating"],
                    row["Review Likes Count"],
                    row["Total Photos by Reviewer"],
                    row["Total Reviews by Reviewer"],
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
        return {"error":  str(err)}
