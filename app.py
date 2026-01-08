from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from urllib.parse import quote_plus

app = Flask(__name__)

password = "Abhi@6394"
# MongoClient(MONGO_URI)
# client = MongoClient("mongodb+srv://abhishekshukla0700:{encoded_password}@cluster0.kursdso.mongodb.net/")
client = MongoClient("mongodb+srv://krishna:Admin123@cluster0.trgyhks.mongodb.net/")
print(client)
db = client["call_detail"]
collection = db["call_detail"]

@app.route("/add-call", methods=["GET","POST"])
def add_call():
    data = request.json
    print(data)

    # data["timestamp"] = datetime.fromisoformat(
    #     data["timestamp"].replace("Z", "+00:00")
    # )

    result = collection.insert_one(data)
    print(result)
    print("----------------")
    return jsonify({
        "message": "Call detail inserted",
        "id": str(result.inserted_id)
    }), 201
def serialize(doc):
    doc["_id"] = str(doc["_id"])
    if "timestamp" in doc or doc["timestamp"]:
        doc["timestamp"] = doc["timestamp"].isoformat()
    return doc


@app.route("/call-stats", methods=["GET"])
def call_stats():
    number = request.args.get("number")
    if not number:
        return jsonify({"error": "Number is required"}), 400

    # Match numbers ignoring +91
    query = {
        "$or": [
            {"owner": number},
            {"owner": "+91" + number}
        ]
    }

    pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": None,
                "total_calls": {"$sum": 1},
                "incoming_calls": {"$sum": {"$cond": [{"$eq": ["$type", "INCOMING"]}, 1, 0]}},
                "outgoing_calls": {"$sum": {"$cond": [{"$eq": ["$type", "OUTGOING"]}, 1, 0]}},
                "missed_calls": {"$sum": {"$cond": [{"$eq": ["$type", "MISSED"]}, 1, 0]}},
                "total_duration": {"$sum": {"$toInt": "$duration"}}
            }
        }
    ]

    stats = list(collection.aggregate(pipeline))
    if stats:
        return jsonify(stats[0])
    else:
        return jsonify({
            "total_calls": 0,
            "incoming_calls": 0,
            "outgoing_calls": 0,
            "missed_calls": 0,
            "total_duration": 0
        })


@app.route("/call-stats-datewise", methods=["GET"])
def call_stats_datewise():
    number = request.args.get("number")
    start_date = request.args.get("start")  # optional, format: YYYY-MM-DD
    end_date = request.args.get("end")      # optional, format: YYYY-MM-DD

    if not number:
        return jsonify({"error": "Number is required"}), 400

    # Build number query (ignore +91)
    query = {
        "$or": [
            {"owner": number},
            {"owner": "+91" + number}
        ]
    }

    # Optional date filter
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
            query["timestamp"]["$gte"] = start_ts
        if end_date:
            # add 1 day to include end_date fully
            end_ts = int((datetime.strptime(end_date, "%Y-%m-%d").timestamp() + 86400) * 1000)
            query["timestamp"]["$lt"] = end_ts

    pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": {"$toDate": "$timestamp"}}
                },
                "total_calls": {"$sum": 1},
                "incoming_calls": {"$sum": {"$cond": [{"$eq": ["$type", "INCOMING"]}, 1, 0]}},
                "outgoing_calls": {"$sum": {"$cond": [{"$eq": ["$type", "OUTGOING"]}, 1, 0]}},
                "missed_calls": {"$sum": {"$cond": [{"$eq": ["$type", "MISSED"]}, 1, 0]}},
                "total_duration": {"$sum": {"$toInt": "$duration"}}
            }
        },
        {"$sort": {"_id": 1}}  # sort by date ascending
    ]

    stats = list(collection.aggregate(pipeline))
    return jsonify(stats)

@app.route("/get-calls", methods=["GET"])
def get_calls():
    docs = collection.find()
    result = []

    for doc in docs:
        doc["_id"] = str(doc["_id"])  # ONLY this is required
        result.append(doc)

    return jsonify(result)

@app.route("/delete-all", methods=["DELETE"])
def delete_all_calls():
    result = collection.delete_many({})

    return jsonify({
        "message": "All records deleted successfully",
        "deleted_count": result.deleted_count
    })
def normalize_number(num):
    num = num.replace(" ", "").replace("-", "")
    
    if num.startswith("+91"):
        return num[3:]
    elif num.startswith("91"):
        return num[2:]
    elif num.startswith("091"):
        return num[3:]
    return num

@app.route("/filter-calls", methods=["GET"])
def filter_calls():
    owner = request.args.get("owner")
    call_number = request.args.get("callee")

    query = {"owner": owner}

    if call_number:
        num = normalize_number(call_number)

        query["$or"] = [
            {"call_number": num},
            {"call_number": "+91" + num},
            {"call_number": "91" + num}
        ]

    docs = collection.find(query)
    result = []

    for doc in docs:
        doc["_id"] = str(doc["_id"])
        result.append(doc)

    return jsonify(result)

# def filter_calls():
#     owner = request.args.get("owner")
#     call_number = request.args.get("callee")
#     query = {"owner": owner}
#     if call_number:
#         num = call_number.replace(" ", "")
#         code = "91"
#         # remove +91 if exists
#         if code in num:
#             num = num[2:]

#         query["$or"] = [
#             {"call_number": num},
#             {"call_number": "+91" + num}
#         ]
        
#     else:
#         query = { "owner": owner }

#     docs = collection.find(query)
#     result = []

#     for doc in docs:
#         doc["_id"] = str(doc["_id"])
#         result.append(doc)

#     return jsonify(result)



if __name__ == "__main__":
    app.run(debug=True)

# from flask import Flask, request, jsonify
# from pymongo import MongoClient
# from urllib.parse import quote_plus


# app = Flask(__name__)

# password = "Abhi@6394"

# encoded_password = quote_plus(password)
# # ---------------- MONGO CONNECTION ----------------
# # MONGO_URI = "mongodb+srv://krishna:Admin123@cluster0.trgyhks.mongodb.net/"  # change if using Atlas
# MONGO_URI = "mongodb+srv://abhishekshukla0700:{encoded_password}@cluster0.kursdso.mongodb.net/appName=Cluster0"
# client = MongoClient(MONGO_URI)
# print(client)
# db = client["call_detail"]        # database name
# collection = db["call_detail"]          # collection name

# # ---------------- POST API ----------------
# @app.route("/add-user", methods=["GET","POST"])
# def add_user():
#     # data = request.json
#     data = {
#         "caller": "+917307120116",
#         "callee": "+919956981029",
#         "duration": "5:53",
#         "timestamp": {
#             "$date": "2025-12-30T14:35:00.000Z"
#         }
# }
#     print(data)
#     if not data:
#         return jsonify({"error": "No data provided"}), 400
#     print(collection)
#     result = collection.insert_one(data)
#     print(result)

#     return jsonify({
#         "message": "Data inserted successfully",
#         "inserted_id": str(result.inserted_id)
#     }), 201


# # ---------------- RUN SERVER ----------------
# if __name__ == "__main__":
#     app.run(debug=True)
