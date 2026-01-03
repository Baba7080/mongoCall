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


@app.route("/get-calls", methods=["GET"])
def get_calls():
    docs = collection.find()
    result = []

    for doc in docs:
        doc["_id"] = str(doc["_id"])  # ONLY this is required
        result.append(doc)

    return jsonify(result)

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
