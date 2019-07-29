
from django.conf import settings

import datetime
from pymongo import MongoClient

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


def startLogs(process_name, detail={}):
    db = getDataSource()
    detail["process_name"] = process_name
    detail["time"] = datetime.datetime.now()
    return db.logs.insert_one(detail).inserted_id

def get_logs(process_name):
    db = getDataSource()
    return db.logs.find({"process": process_name}).sort("time")
