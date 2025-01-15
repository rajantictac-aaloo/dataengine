#file name grestaurants.py
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

gmapsschema = [
    "Place ID",
    "Name",
    "Phone",
    "Rating",
    "Address",
    "Website",
    "Menu Items",
    "Menu Highlights",
    "Latitude",
    "Longitude",
    "Categories",
    "Order Link",
    "Owner Name",
    "Description",
    "Price Meter",
    "Hours",
    "Rating Count",
    "Featured Image",
    "Google Maps URL",
    "Review Keywords",
    "Reservation Link",
    "Restaurant Claimed",
    "Is Temporarily Closed",
    "Menu Search Query",
]


def gmpscolumnscheck(columnsofuploadedfile):
    uploaded_columns = set(columnsofuploadedfile)
    expected_columns = set(gmapsschema)

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


def gmapsmandatoarycolumncheck(chunk):
    nullplaceid = chunk.index[chunk["Place ID"].isna()].tolist()
    nullname = chunk.index[chunk["Name"].isna()].tolist()
    nulladdress = chunk.index[chunk["Address"].isna()].tolist()
    nulllatitude = chunk.index[chunk["Latitude"].isna()].tolist()
    nulllongitude = chunk.index[chunk["Longitude"].isna()].tolist()
    nullcategories = chunk.index[chunk["Categories"].isna()].tolist()
    nullfeaturedimage = chunk.index[chunk["Featured Image"].isna()].tolist()
    nullgooglemapsurl = chunk.index[chunk["Google Maps URL"].isna()].tolist()

    response_data = {
        "nullplaceid": nullplaceid,
        "nullname": nullname,
        "nulladdress": nulladdress,
        "nulllatitude": nulllatitude,
        "nulllongitude": nulllongitude,
        "nullcategories": nullcategories,
        "nullfeaturedimage": nullfeaturedimage,
        "nullgooglemapsurl": nullgooglemapsurl,
    }
    filtered_response_data = { key: value for key, value in response_data.items() if value}
    
    if not filtered_response_data:
        filtered_response_data = None
    
    return filtered_response_data


def gmpsduplicatecheck(chunk):
    entire_duplicated_rows = chunk[chunk.duplicated(keep=False)]
    drop1 = chunk.drop_duplicates(keep="first")

    duplicate_place_id = drop1[drop1[["Place ID"]].duplicated(keep=False)]
    drop2 = drop1.drop_duplicates(subset=["Place ID"], keep="first")

    duplicate_place_id_name_address = drop2[drop2[["Place ID", "Name", "Address", "Google Maps URL"]].duplicated(keep=False)]
    drop3 = drop2.drop_duplicates(subset=["Place ID", "Name", "Address", "Google Maps URL"], keep="first")

    same_place_diff_place_id = chunk[chunk[["Name", "Address", "Latitude", "Longitude"]].duplicated(keep=False)]

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


def gmpsnullvaluehandle(drop3):
    drop3["Place ID"] = drop3["Place ID"].fillna("Unknown")
    drop3["Name"] = drop3["Name"].fillna("Unknown")
    drop3["Phone"] = drop3["Phone"].fillna("N/A")
    drop3["Rating"] = drop3["Rating"].fillna(0.0)
    drop3["Address"] = drop3["Address"].fillna("Unknown")
    drop3["Website"] = drop3["Website"].fillna("N/A")
    drop3["Menu Items"] = drop3["Menu Items"].fillna("[]")
    drop3["Menu Highlights"] = drop3["Menu Highlights"].fillna("[]")
    drop3["Review Keywords"] = drop3["Review Keywords"].fillna("[]")
    drop3["Latitude"] = drop3["Latitude"].fillna(0.0)
    drop3["Longitude"] = drop3["Longitude"].fillna(0.0)
    drop3["Categories"] = drop3["Categories"].fillna("N/A")
    drop3["Order Link"] = drop3["Order Link"].fillna("N/A")
    drop3["Owner Name"] = drop3["Owner Name"].fillna("Unknown")
    drop3["Description"] = drop3["Description"].fillna("No description available")
    drop3["Price Meter"] = drop3["Price Meter"].fillna(0)
    drop3["Hours"] = drop3["Hours"].fillna("Not available")
    drop3["Rating Count"] = drop3["Rating Count"].fillna(0)
    drop3["Featured Image"] = drop3["Featured Image"].fillna("N/A")
    drop3["Google Maps URL"] = drop3["Google Maps URL"].fillna("N/A")
    drop3["Reservation Link"] = drop3["Reservation Link"].fillna("NO")
    drop3["Restaurant Claimed"] = drop3["Restaurant Claimed"].fillna(False)
    drop3["Is Temporarily Closed"] = drop3["Is Temporarily Closed"].fillna(False)
    drop3["Menu Search Query"] = drop3["Menu Search Query"].fillna("N/A")
    return drop3


def creategmapstable(drop3, MYSQL_CONFIG, tablename):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {tablename} (
     placeid VARCHAR(255) PRIMARY KEY,
     name VARCHAR(255) NOT NULL,
     phone VARCHAR(255) DEFAULT 'N/A',
     rating DECIMAL DEFAULT 0.0,
     address TEXT,
     website LONGTEXT,
     menuitems JSON,
     menuhighlights JSON,
     menusearchquery VARCHAR(255) DEFAULT 'N/A',
     latitude DECIMAL(10,8) DEFAULT 0.0,
     longitude DECIMAL(11,8) DEFAULT 0.0,
     categories VARCHAR(255) DEFAULT 'N/A',
     orderLink LONGTEXT,
     ownername VARCHAR(255) DEFAULT 'Unknown',
     description TEXT,
     pricemeter INT DEFAULT 0,
     hours JSON,
     ratingcount INT DEFAULT 0,
     featuredimage LONGTEXT,
     googlemapsURL LONGTEXT,
     reviewkeywords TEXT,
     reservationlink VARCHAR(255) DEFAULT 'NO',
     restaurantclaimed BOOLEAN DEFAULT FALSE,
     istemporarilyclosed BOOLEAN DEFAULT FALSE,
     menuitemscount INT 
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


def insert_data_to_mysql_googlemaps(drop3, MYSQL_CONFIG, tablename):
    try:
        creategmapstable(drop3, MYSQL_CONFIG, tablename)
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
            placeid, name, phone, rating, address, website, menuitems,
            menuhighlights, menusearchquery, latitude, longitude, categories, orderlink,
            ownername, description, pricemeter, hours, ratingcount,
            featuredimage, googlemapsURL, reviewkeywords, reservationlink,
            restaurantclaimed, istemporarilyclosed, menuitemscount
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """

        data = []

        for index, row in drop3.iterrows():
            data.append(
                (
                    row["Place ID"],
                    row["Name"],
                    row["Phone"],
                    row["Rating"],
                    row["Address"],
                    row["Website"],
                    row["Menu Items"],
                    row["Menu Highlights"],
                    row["Menu Search Query"],
                    row["Latitude"],
                    row["Longitude"],
                    row["Categories"],
                    row["Order Link"],
                    row["Owner Name"],
                    row["Description"],
                    row["Price Meter"],
                    row["Hours"],
                    row["Rating Count"],
                    row["Featured Image"],
                    row["Google Maps URL"],
                    row["Review Keywords"],
                    row["Reservation Link"],
                    row["Restaurant Claimed"],
                    row["Is Temporarily Closed"],
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

