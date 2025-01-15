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

zomatoschema = [
    "Place ID",
    "Restaurant ID",
    "Title",
    "Address",
    "Cuisines",
    "Top Dishes",
    "Menu Items",
    "Zomato URL",
    "Average Cost",
    "Description",
    "Open Timings",
    "Phone Number",
    "Dinner Rating",
    "Delivery Rating",
    "Dinner Rating Count",
    "Delivery Rating Count",
]

def zomcolumnscheck(columnsofuploadedfile):
    uploaded_columns = set(columnsofuploadedfile)
    expected_columns = set(zomatoschema)

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


def zomduplicatecheck(chunk):
    print("yaha nahi aaya")
    entire_duplicated_rows = chunk[chunk.duplicated(keep=False)]
    drop1 = chunk.drop_duplicates(keep="first")

    duplicate_place_id = drop1[drop1[["Place ID"]].duplicated(keep=False)]
    drop2 = drop1.drop_duplicates(subset=["Place ID"], keep="first")

    duplicate_place_id_name_address = drop2[
        drop2[["Place ID", "Title", "Address", "Zomato URL"]].duplicated(keep=False)
    ]
    drop3 = drop2.drop_duplicates(
        subset=["Place ID", "Title", "Address", "Zomato URL"], keep="first"
    )

    same_place_diff_place_id = chunk[
        chunk[["Title", "Address", "Zomato URL"]].duplicated(keep=False)
    ]

    response_data = {
        "duplicate_rows": entire_duplicated_rows.index.tolist(),
        "duplicate_place_id": duplicate_place_id.index.tolist(),
        "duplicate_place_id_name_address": duplicate_place_id_name_address.index.tolist(),
        "same_place_diff_place_id": same_place_diff_place_id.index.tolist(),
    }
    filtered_response_data = {
        key: value for key, value in response_data.items() if value
    }

    if not filtered_response_data:
        filtered_response_data = None

    return drop3, filtered_response_data


def zomatorestraurantmandatoarycolumncheck(chunk):
    nullplaceid = chunk.index[chunk["Place ID"].isna()].tolist()
    nullrestaurantid = chunk.index[chunk["Restaurant ID"].isna()].tolist()
    nulladdress = chunk.index[chunk["Address"].isna()].tolist()
    nullzomatourl = chunk.index[chunk["Zomato URL"].isna()].tolist()
    nulltitle= chunk.index[chunk["Title"].isna()].tolist()

    response_data = {
        "nullplaceid": nullplaceid,
        "nullname": nullrestaurantid,
        "nulladdress": nulladdress,
        "nullzomatourl": nullzomatourl,
        "nulltitle": nulltitle,
    }
    filtered_response_data = { key: value for key, value in response_data.items() if value}
    
    if not filtered_response_data:
        filtered_response_data = None
    
    return filtered_response_data


def zomnullvaluehandle(drop3):
    drop3["Restaurant ID"] = drop3["Restaurant ID"].fillna("Unknown")
    drop3["Title"] = drop3["Title"].fillna("Unknown")
    drop3["Address"] = drop3["Address"].fillna("Unknown")
    drop3["Cuisines"] = drop3["Cuisines"].fillna("N/A")
    drop3["Top Dishes"] = drop3["Top Dishes"].fillna("N/A")
    drop3["Menu Items"] = drop3["Menu Items"].fillna("[]")
    drop3["Zomato URL"] = drop3["Zomato URL"].fillna("N/A")
    drop3["Average Cost"] = drop3["Average Cost"].fillna(0.0)
    drop3["Description"] = drop3["Description"].fillna("N/A")
    drop3["Open Timings"] = drop3["Open Timings"].fillna("Not available")
    drop3["Phone Number"] = drop3["Phone Number"].fillna("Not available")
    drop3["Dinner Rating"] = drop3["Dinner Rating"].fillna(0.0)
    drop3["Delivery Rating"] = drop3["Delivery Rating"].fillna(0.0)
    drop3["Dinner Rating Count"] = drop3["Dinner Rating Count"].fillna(0)
    drop3["Delivery Rating Count"] = drop3["Delivery Rating Count"].fillna(0)
    print("3rd check")
    return drop3


def create_zomato_table(drop3, MYSQL_CONFIG, tablename):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {tablename} (
     placeid VARCHAR(255) PRIMARY KEY,
     restaurantid VARCHAR(255)  NOT NULL,
     title  VARCHAR(255) ,
     address TEXT,
     cuisines LONGTEXT,
     topdishes TEXT,
     menuitems JSON,
     zomatoURL VARCHAR(255) DEFAULT 'N/A',
     averagecost INT DEFAULT 0,
     description TEXT,
     opentimings TEXT ,
     phonenumber TEXT ,
     dinnerrating DECIMAL(3,2) DEFAULT 0.0,
     deliveryrating DECIMAL(3,2) DEFAULT 0.0,
     dinnerratingcount INT DEFAULT 0,
     deliveryratingcount INT DEFAULT 0,
     menuitemscount INT
) ;
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


def insert_data_to_mysql_zomato(drop3, MYSQL_CONFIG, tablename):
    try:
        create_zomato_table(drop3, MYSQL_CONFIG, tablename)

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
            placeid, restaurantid, title, address, cuisines, topdishes, menuitems, 
            zomatoURL, averagecost, description, opentimings, phonenumber, 
            dinnerrating, deliveryrating, dinnerratingcount, deliveryratingcount,menuitemscount
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)
            """

        data = []

        for index, row in drop3.iterrows():
            data.append(
                (
                    row["Place ID"],
                    row["Restaurant ID"],
                    row["Title"],
                    row["Address"],
                    row["Cuisines"],
                    row["Top Dishes"],
                    row["Menu Items"],
                    row["Zomato URL"],
                    row["Average Cost"],
                    row["Description"],
                    row["Open Timings"],
                    row["Phone Number"],
                    row["Dinner Rating"],
                    row["Delivery Rating"],
                    row["Dinner Rating Count"],
                    row["Delivery Rating Count"],
                    row["Menu Items Count"],
                )
            )

        cursor.executemany(insert_query, data)
        db.commit()
        cursor.close()
        db.close()

        print("Data inserted successfully into MySQL database.")
        return {"message": "Data Successfully saved to DB"}

    except Exception as err:
        print(f"Error: {err}")
        return {"error": str(err)}

