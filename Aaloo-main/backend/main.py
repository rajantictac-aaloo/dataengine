from flask import Flask, request, jsonify, send_file
import pandas as pd
import json
import os
from flask_cors import CORS
from dotenv import load_dotenv
import mysql.connector as conn
from io import BytesIO
import googlerestaurants
import googlereviews
import zomatorestaurants
import zomatoreviews
import sentianalysis
import arsscore
import trendingfood
# Create a Flask application instance
app = Flask(__name__)


# Enable Cross-Origin Resource Sharing (CORS) for the app to send data to frontend
CORS(app)

# Load environment variables from a .env file
load_dotenv()

# Set the maximum content length for uploaded files (500 MB)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024


# MySQL database configuration, values fetched from environment variables
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DB"),
}



#function for counting the menu items of each row
def menuitemcount(json_str):   
    try:
        json_list = json.loads(json_str)   # Parse the JSON string into a Python object
        return len(json_list) # Return the number of items in the JSON list
    except (json.JSONDecodeError, TypeError):
        return 0




# Function to process Google reviews in chunks and handle database operations
def process_in_chunks_googlereviews(file, tablename, chunk_size=50000):
    for chunk in pd.read_csv(file, chunksize=chunk_size, encoding="utf-8", low_memory=False):
        
        # Get the column names of the uploaded file
        columnsofuploadedfile = chunk.columns.tolist()
        
        # Check for required and extra columns specific to Google reviews
        googlecheck, column_response_data = googlereviews.googlereviewscolumncheck(columnsofuploadedfile)
        dropped_columns = []
        # Handle missing or extra columns        
        if not googlecheck:
            if ("missing_columns" in column_response_data and "extra_columns" not in column_response_data):
                return {
                    "error": "Missing columns in the uploaded file.",
                    "details": column_response_data,
                }

            elif ( "extra_columns" in column_response_data and "missing_columns" not in column_response_data):
                #dropping the extra columns if missing columns are not there
                extra_columns = column_response_data["extra_columns"]
                dropped_columns.extend(extra_columns)  # Track dropped columns
                chunk = chunk.drop(extra_columns, axis=1)

            elif ( "missing_columns" in column_response_data and "extra_columns" in column_response_data):
                return {
                    "error": "Both missing and extra columns detected.",
                    "details": column_response_data,
                }
        
        # mandatory column check
        mandatory_column_response_data = googlereviews.greviewsmandatoarycolumncheck(chunk)
        
        # Remove duplicate entries from the chunk
        drop3, duplicate_response_data = googlereviews.googlereviewduplicatecheck(chunk)
        
        # Handle null values in the chunk
        drop3 = googlereviews.googlereviewnullvaluehandle(drop3)
        
        # sentiment analysis functino for googlereview sheets uncomment if you need to check sentiment of each review
        # drop3 = sentianalysis.sentimentanalysis_google_reviews(drop3)
        
        try:
            # Insert the processed chunk into the MySQL database
            db_result = googlereviews.insert_data_to_mysql_googlereview(drop3, MYSQL_CONFIG, tablename)
            if "error" in db_result:
                return {
                    "error": "Failure not all data wasnt inserted into DB some error occured",
                    "details": db_result,
                    }
                
            return {
                "status": "success",
                "db_message": db_result["message"],
                "duplicates": duplicate_response_data,
                "extra_columns": dropped_columns,
                "nullvalues": mandatory_column_response_data,
            }
        except Exception as e:
            # Return an error message if database insertion fails
            return {"error": f"Database error: {str(e)}"}


def process_in_chunks_zomatoreviews(file, tablename, chunk_size=50000):
    for chunk in pd.read_csv(file, chunksize=chunk_size, encoding="utf-8", low_memory=False):
        
        columnsofuploadedfile = chunk.columns.tolist()
        dropped_columns = []
        zomcheck, column_response_data = zomatoreviews.zomatoreviewscolumncheck(columnsofuploadedfile)
        if not zomcheck:
            if ("missing_columns" in column_response_data and "extra_columns" not in column_response_data):
                return {
                    "error": "Missing columns in the uploaded file.",
                    "details": column_response_data,
                }

            elif ("extra_columns" in column_response_data and "missing_columns" not in column_response_data):
                #dropping the extra columns if missing columns are not there
                extra_columns = column_response_data["extra_columns"]
                dropped_columns.extend(extra_columns)  # Track dropped columns
                chunk = chunk.drop(extra_columns, axis=1)

            elif ("missing_columns" in column_response_data  and "extra_columns" in column_response_data):
                return {
                    "error": "Both missing and extra columns detected.",
                    "details": column_response_data,
                }
        
        # mandatory column check
        mandatory_column_response_data = zomatoreviews.zreviewsmandatoarycolumncheck(chunk)
        
        drop3, duplicate_response_data = zomatoreviews.zomreviewduplicatecheck(chunk)
        
        drop3 = zomatoreviews.zomreviewnullvaluehandle(drop3)

        try:
            db_result = zomatoreviews.insert_data_to_mysql_zomatoreview( drop3, MYSQL_CONFIG, tablename)
            if "error" in db_result:
                return {
                    "error": "Failure not all data wasnt inserted into DB some error occured",
                    "details": db_result,
                    }
            return {
                "status": "success",
                "db_message": db_result["message"],
                "duplicates": duplicate_response_data,
                "extra_columns": dropped_columns,
                "nullvalues": mandatory_column_response_data,
            }
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}


def process_in_chunks_zomato(file, tablename, chunk_size=50000):
    for chunk in pd.read_csv(file, chunksize=chunk_size, encoding="utf-8", low_memory=False):
        
        #column check
        dropped_columns = []
        columnsofuploadedfile = chunk.columns.tolist()
        zomcheck, column_response_data = zomatorestaurants.zomcolumnscheck(columnsofuploadedfile)    
        #checking if missing columns or extra columns are present in the uploaded file
        if not zomcheck:
            if ("missing_columns" in column_response_data and "extra_columns" not in column_response_data):
                return {
                    "error": "Missing columns in the uploaded file.",
                    "details": column_response_data,
                }

            elif ("extra_columns" in column_response_data and "missing_columns" not in column_response_data ):
                #if extra columns present and no missing columns then we drop the extra columns
                extra_columns = column_response_data["extra_columns"]
                dropped_columns.extend(extra_columns)  # Track dropped columns
                chunk = chunk.drop(extra_columns, axis=1)

            elif (
                "missing_columns" in column_response_data
                and "extra_columns" in column_response_data
            ):
                return {
                    "error": "Both missing and extra columns detected.",
                    "details": column_response_data,
                }
        #handling duplicates and sending them to the frontend
        
        #mandatory column check
        mandatory_column_response_data = zomatorestaurants.zomatorestraurantmandatoarycolumncheck(chunk)
        
        
        drop3, duplicate_response_data = zomatorestaurants.zomduplicatecheck(chunk)
        
        #handling null values
        drop3 = zomatorestaurants.zomnullvaluehandle(drop3)
        
        #menu item count function to calculate the number of menu items in each row
        drop3["Menu Items Count"] = drop3["Menu Items"].apply(menuitemcount)
        
        #isnerting into database
        try:
            db_result = zomatorestaurants.insert_data_to_mysql_zomato(drop3, MYSQL_CONFIG, tablename)
            if "error" in db_result:
                return {
                    "error": "Failure not all data wasnt inserted into DB some error occured",
                    "details": db_result,
                    }
                
            return {
                "status": "success",
                "db_message": db_result["message"],
                "duplicates": duplicate_response_data,
                "extra_columns": dropped_columns,
                "nullvalues": mandatory_column_response_data,
            }
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}


#function for google restaurants processing in chunks
def process_in_chunks(
    file, tablename, chunk_size=100000):
    for chunk in pd.read_csv(file, chunksize=chunk_size, encoding="utf-8", low_memory=False):
        
        # column check
        dropped_columns = []
        columnsofuploadedfile = chunk.columns.tolist()
        gmapscheck, column_response_data = googlerestaurants.gmpscolumnscheck(columnsofuploadedfile)
        if not gmapscheck:
            #missing columns but not extra columns
            if ("missing_columns" in column_response_data  and "extra_columns" not in column_response_data):
                return {
                    "error": "Missing columns in the uploaded file.",
                    "details": column_response_data}
            
            elif "extra_columns" in column_response_data and "missing_columns" not in column_response_data:
                extra_columns = column_response_data["extra_columns"]
                dropped_columns.extend(extra_columns)  # Track dropped columns
                chunk = chunk.drop(extra_columns, axis=1)
            
            
            #both missing columns and extra columns
            elif ( "missing_columns" in column_response_data and "extra_columns" in column_response_data):
                return {
                    "error": "Both missing and extra columns detected.",
                    "details": column_response_data}

        # mandatory column check
        mandatory_column_response_data = googlerestaurants.gmapsmandatoarycolumncheck(chunk)
        # if mandatory_column_response_data:
        #     # return {
        #     #     "error": "Mandatory columns values are missing.",
        #     #     "details": mandatory_column_response_data,
        #     # }
        #     mandatory_column  = mandatory_column_response_data
            
        # duplicate check
        drop3, duplicate_response_data = googlerestaurants.gmpsduplicatecheck(chunk)

        # null value handle
        drop3 = googlerestaurants.gmpsnullvaluehandle(drop3)

        # new column
        drop3["Menu Items Count"] = drop3["Menu Items"].apply(menuitemcount)

        # insert to db
        try:
            db_result = googlerestaurants.insert_data_to_mysql_googlemaps(drop3, MYSQL_CONFIG, tablename)
            if "error" in db_result:
                return {
                    "error": "Failure not all data wasnt inserted into DB some error occured",
                    "details": db_result,
                    }
            
            return {
                "status": "success",
                "db_message": db_result["message"],
                "duplicates": duplicate_response_data,
                "extra_columns": dropped_columns,
                "nullvalues": mandatory_column_response_data,
            }

        except Exception as e:
            print(e)
            return {"error": f"Database error: {str(e)}"}




@app.route("/googlerestaurants", methods=["GET", "POST"])
def handle_googlerestaurants():
    if request.method == "POST":
        #checking if file is present in the request or not 
        if "file" not in request.files:
            return jsonify({"error": "No file or an empty file provided"}), 400
        
        #post requesting for the file that has been uploaded on the frontend 
        file = request.files["file"]
        #table name to storoe in sql database
        tablename = request.form.get("tablename")
        
        # user_response = request.form.get("user_response")  # Get user response from the request
        # Validate user response
        # if user_response not in ["yes", "no"]:
        #     return jsonify({"message": "Invalid user response. Please provide 'yes' or 'no'."}), 400
        
        try:
            #making the request to process in chunk function for googlerestaurants
            result = process_in_chunks(file, tablename)
            
            if "error" in result:
                return jsonify({
                    "error": result["error"],
                    "details": result["details"]
                    }),400

            return jsonify({"results": result}), 200

        except Exception as e:
            print(e)
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500

    return jsonify({"error": "No file received."})


@app.route("/zomatorestaurants", methods=["GET", "POST"])
def handle_zomatorrestaurants():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file or an empty file provided"}), 400

        file = request.files["file"]
        tablename = request.form.get("tablename")

        try:
            result = process_in_chunks_zomato(file, tablename)
            if "error" in result:
                return (
                    jsonify(
                        {
                            "message": result["error"],
                            "details": result["details"],
                        }
                    ),
                    400,
                )

            return jsonify({"results": result}), 200

        except Exception as e:
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
    
    return jsonify({"error": "No file received."})

@app.route("/zomatoreviews", methods=["GET", "POST"])
def handle_zomatoreviews():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file or an empty file provided"}), 400

        file = request.files["file"]
        tablename = request.form.get("tablename")

        try:
            result = process_in_chunks_zomatoreviews(file, tablename)
            if "error" in result:
                return (
                    jsonify(
                        {
                            "message": result["error"],
                            "details": result["details"],
                        }
                    ),
                    400,
                )

            return jsonify({"results": result}), 200

        except Exception as e:
            print(e)
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
    

@app.route("/googlereviews", methods=["GET", "POST"])
def handle_googlereviews():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"message": "No file or an empty file provided"}), 400

        file = request.files["file"]
        tablename = request.form.get("tablename")

        try:
            result = process_in_chunks_googlereviews(file, tablename)
            if "error" in result:
                print(result["details"])
                return (
                    jsonify(
                        {
                            "message": result["error"],
                            "details": result["details"],
                        }
                    ),
                    400,
                )

            return jsonify({"results": result}), 200

        except Exception as e:
            return jsonify({"message": f"Error processing file: {str(e)}"}), 500

@app.route("/ars", methods=["POST","GET"])
def handle_ars():
    
    if request.method == "GET":
        try:
            connection = conn.connect(
            host=MYSQL_CONFIG["host"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
             )
            cursor = connection.cursor(dictionary=True)  # Use dictionary cursor for easier handling
        
            cursor.execute("SHOW tables")
            tables = cursor.fetchall()
            print(tables)
            return jsonify({"tables": tables}), 200  
        
        except conn.Error as err:
            print(f"Database Error: {err}")
            return jsonify({"message": "Database Error"}), 500
        
        finally:
            if connection:
                try:
                    connection.close()
                except conn.Error as close_err:
                    print(f"Error closing connection: {close_err}")
     
     
     
     
    if request.method == "POST":

        try:
            data = request.json  # Parse JSON payload
            googlerestaurantstablename = data.get("googlerestaurants")
            zomatorestaurantstablename = data.get("zomatorestaurants")
            googlereviewtablename = data.get("googlereviews")
            
            print(googlerestaurantstablename)
            print(zomatorestaurantstablename)
            print(googlereviewtablename)
            
            if not googlerestaurantstablename or not zomatorestaurantstablename or not googlereviewtablename:
                return jsonify({"message": "Missing required table names"}), 400
            
            # Call arsfunc function
            result = arsscore.arsfunc(googlerestaurantstablename,zomatorestaurantstablename,googlereviewtablename)
            print("result",result)
            return jsonify({"results": result}), 200
        
        
        except Exception as e:
            print("error",e)
            return jsonify({"message": f"Error processing file: {str(e)}"}), 500
   
        
@app.route("/trendingfood",methods=["GET","POST"])  
def handle_trendingfood():
    if request.method == "POST":
        data = request.json
        placeids = data.get("placeids")
        print(placeids)
        
        trendingfoods = trendingfood.trendingfoodfinder(placeids)
        
        if not placeids:
            return jsonify({"message": "Missing required place ids"}), 400
    
    return jsonify({"trendingfood": trendingfoods}), 200
        
        
        
if __name__ == "__main__":
    app.run(debug=True)
