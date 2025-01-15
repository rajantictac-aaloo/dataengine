from flask import Flask, request, jsonify, send_file
import pandas as pd
import json
import os
from flask_cors import CORS
from dotenv import load_dotenv
import mysql.connector as conn
from io import BytesIO

load_dotenv()

# MySQL database configuration, values fetched from environment variables
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DB"),
}

# def trendingfoodfinder(placeids):
#     trendingfoods = {}
    
#     connection = conn.connect(
#         host=MYSQL_CONFIG["host"],
#         user=MYSQL_CONFIG["user"],
#         password=MYSQL_CONFIG["password"],
#         database=MYSQL_CONFIG["database"],
#      )
#     cursor = connection.cursor(dictionary=True)  # Use dictionary cursor for easier handling
    
#     try:  
#         # for ids in placeids:
#         #     cursor.execute("SELECT name, menuitems FROM mastertable WHERE placeid = %s", (ids,))
#         #     row = cursor.fetchone()
#         #     trendingfoods[ids] = {
#         #         "name": row["name"],
#         #         "menuitems": row["menuitems"]
#         #     }
#         menu_items = {}
#         for ids in placeids:
#             cursor.execute("SELECT name, menuitems FROM mastertable WHERE placeid = %s", (ids,))
#             row = cursor.fetchone()

#             if row:
#                 place_name = row["name"]
#                 # Parse menuitems from JSON string
#                 menu = json.loads(row["menuitems"])

#                 for item in menu:
#                     item_name = item["name"]
#                     arsscore = item.get("arsscore", 0)  # Get the arsscore of the menu item (default 0 if not found)

#                     # Accumulate the ARS score for the same menu item name
#                     if item_name not in menu_items:
#                         menu_items[item_name] = {
#                             "total_arsscore": arsscore,
#                             "details": [item]  # Save the menu item details as a list
#                         }
#                     else:
#                         menu_items[item_name]["total_arsscore"] += arsscore
#                         menu_items[item_name]["details"].append(item)

#         # Now, we need to sort the menu items by total_arsscore in descending order
#         sorted_items = sorted(menu_items.items(), key=lambda x: x[1]["total_arsscore"], reverse=True)

#         # Prepare the final list of trending foods with sorted items
#         trendingfoods = [
#             {"name": item_name, "total_arsscore": details["total_arsscore"], "menuitems": details["details"]}
#             for item_name, details in sorted_items
#         ]
            
   
   
#     except Exception as err:
#         print(str(err))
#         return {"error": str(err)}
   
   
#     finally:
#         cursor.close()
#         connection.close()
    
   
#     return trendingfoods
def trendingfoodfinder(placeids):
    menu_items = {}
    
    connection = conn.connect(
        host=MYSQL_CONFIG["host"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["database"],
    )
    cursor = connection.cursor(dictionary=True)
    
    try:
        for ids in placeids:
            cursor.execute("SELECT name, menuitems FROM mastertable WHERE placeid = %s", (ids,))
            row = cursor.fetchone()
            
            if row:
                place_name = row["name"]
                menu = json.loads(row["menuitems"])

                for item in menu:
                    item_name = item["name"]
                    arsscore = item.get("arsscore")  # Get the ARS score (default 0 if not found)

                    # Accumulate the ARS score for the same menu item name
                    if item_name not in menu_items:
                        menu_items[item_name] = {
                            "total_arsscore": arsscore,
                            "details": [{"name": item_name, "price": item.get("price", "N/A"), "arsscore": arsscore,"restaurant": place_name}]
                        }
                    else:
                        # Update the total ARS score
                        menu_items[item_name]["total_arsscore"] += arsscore

                        # Avoid duplicate entries in the details array
                        existing_details = menu_items[item_name]["details"]
                        new_entry = {
                            "name": item_name,
                            "price": item.get("price", "N/A"),
                            "arsscore": arsscore,
                            "restaurant": place_name
                        }
                        if new_entry not in existing_details:  # Check for duplicates
                            existing_details.append(new_entry)

        # Sort the menu items by total_arsscore in descending order
        sorted_items = sorted(menu_items.items(), key=lambda x: x[1]["total_arsscore"], reverse=True)

        # Prepare the final list of trending foods with sorted items
        trendingfoods = [
            {"name": item_name, "total_arsscore": details["total_arsscore"], "menuitems": details["details"]}
            for item_name, details in sorted_items
        ]

    except Exception as err:
        print(str(err))
        return {"error": str(err)}
    finally:
        cursor.close()
        connection.close()

    return trendingfoods