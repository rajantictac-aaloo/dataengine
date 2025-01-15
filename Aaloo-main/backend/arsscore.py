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

def arsfunc(googlerestaurantstablename, zomatorestaurantstablename, googlereviewtablename):
    try:
        # Connect to the database
        connection = conn.connect(
            host=MYSQL_CONFIG["host"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
        )
        cursor = connection.cursor(dictionary=True)  # Use dictionary cursor for easier handling

        # Fetch all rows from grestaurants
        cursor.execute(f"SELECT placeid, menuitems FROM {googlerestaurantstablename}")
        grestaurants = cursor.fetchall()
        print(grestaurants)
        
        # Fetch zrestaurants data for all placeids
        cursor.execute(f"SELECT placeid, menuitems FROM {zomatorestaurantstablename}")
        zrestaurants = {row["placeid"]: json.loads(row["menuitems"]) for row in cursor.fetchall()}
        print(zrestaurants)
        
        # Fetch grevi reviews for all placeids
        cursor.execute(f"SELECT placeid, review FROM {googlereviewtablename}")
        grevi_reviews = {}
        for row in cursor.fetchall():
            grevi_reviews.setdefault(row["placeid"], []).append(row["review"])
        print(grevi_reviews)
        
        # Iterate over grestaurants data
        for grestaurant in grestaurants:
            placeid = grestaurant["placeid"]
            menuitem = json.loads(grestaurant["menuitems"])  # Parse JSON object

            # Initialize ARS scores for this placeid
            ars_scores = {item["name"]: 1 for item in menuitem}
            print(ars_scores)
            
            # Check zrestaurants for the same placeid
            if placeid in zrestaurants:
                z_menuitems = zrestaurants[placeid]
                print(zrestaurants[placeid])
                
                # Update ARS scores based on bestseller tag
                for z_item in z_menuitems:
                    item_name = z_item.get("item")
                    tags = z_item.get("tags", [])
                    if item_name in ars_scores:
                        if "bestseller" in tags:
                            ars_scores[item_name] *= 5

            # Check grevi reviews for the same placeid
            reviews = grevi_reviews.get(placeid, [])
            positive_keywords = [
                "good", "excellent", "amazing", "delicious", "tasty", "flavorful",
                "savory", "yummy", "scrumptious", "delectable", "mouthwatering",
                "divine", "fantastic", "outstanding", "perfect", "wonderful",
                "appetizing", "exquisite", "satisfying", "heavenly", "aromatic",
                "luscious", "tempting", "sumptuous", "irresistible","best"
            ]

            associated_items = {}  # Track how many times each item is associated with positive reviews
            for review in reviews:
                review_lower = review.lower()
                for name in ars_scores.keys():
                    if name.lower() in review_lower:  # Check explicit mention
                        # Check for positive sentiment keywords
                        if any(keyword in review_lower for keyword in positive_keywords):
                            if name not in associated_items:
                                associated_items[name] = 0  # Initialize count for the item
                            associated_items[name] += 1  # Increment count for each mention

            # Update ARS scores based on the number of mentions in positive reviews
            for item, count in associated_items.items():
                ars_scores[item] = ars_scores[item] + (1 * count)  # Add the ARS score with the number of count of the menu item for each mention

            # Update menuitem JSON with ARS scores
            updated = False
            for item in menuitem:
                if item["name"] in ars_scores:
                    original_score = item.get("arsscore", 0)
                    new_score = ars_scores[item["name"]]
                    if new_score != original_score:
                        item["arsscore"] = new_score  # Add or update ARS score
                        updated = True

            # Update the database if changes were made
            if updated:
                updated_menuitem_json = json.dumps(menuitem)
                cursor.execute(
                    f"UPDATE {googlerestaurantstablename} SET menuitems = %s WHERE placeid = %s",
                    (updated_menuitem_json, placeid),
                )
                connection.commit()  # Commit changes
                print(f"Updated ARS scores for PlaceID: {placeid}")

        return "ARS Score updated in master restaurant table"

    except conn.Error as err:
        print(f"Database Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed.")
