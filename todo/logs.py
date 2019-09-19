
from django.conf import settings

import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId


dataSource = False


def getDataSource():
    global dataSource
    if dataSource is False:
        client = MongoClient(settings.MONGO_URL)
        db = client[settings.MONGO_DB]
        dataSource = db
        return dataSource
    else:
        return dataSource


def addLogs(log, log_id):
    log["log_id"] = log_id
    log["time"] = datetime.datetime.now()
    db = getDataSource()
    if log["type"] == "alert":
        db.alert.insert_one(log)
    db.log_detail.insert_one(log)


def get_critical_logs():
    db = getDataSource()
    return db.alert.find().sort("time").limit(100)


def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    if doc["log_id"]:
        doc["log_id"] = str(doc["log_id"])

    doc["time"] = doc["time"]["$date"]
    
    return doc


def clear_log(log_id):
    db = getDataSource()
    log = db.alert.find_one({
        "_id": ObjectId(log_id)
    })
    text = log["message"]

    db.alert.remove({
        "_id": ObjectId(log_id)
    })

    db.alert.remove({
        "message": text
    })

    db.log_detail.remove({
        "message": text
    })


def startLogs(process_name, detail={}):
    db = getDataSource()
    detail["process_name"] = process_name
    detail["time"] = datetime.datetime.now()
    return db.logs.insert_one(detail).inserted_id


def get_logs(process_name):
    db = getDataSource()
    return db.logs.find({"process": process_name}).sort("time")
