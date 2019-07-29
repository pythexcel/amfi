
from django.conf import settings

from pymongo import MongoClient

dataSource = False


def getDataSource():
    if dataSource is False:
        client = MongoClient(settings.MONGO_URL)
        db = client[settings.MONGO_DB]
        dataSource = db
        return dataSource
    else:
        return dataSource


def addLogs(logs, process_name, isUI=False):

    for log in logs:
        if log["type"] == "alert":
            log["process"] = process_name
            db.alert.insert_one(log)
            pass
        else:
            if isUI is True:
                db = getDataSource()
                log["process"] = process_name  # which process is this
                db.logs.insert_one(log)

            pass

    pass
