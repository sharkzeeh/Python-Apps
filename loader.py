import json
import pymongo
from pymongo import MongoClient
from zipfile import ZipFile
from random import randint
import numpy as np
from sys import exit
import pprint
np.random.seed(42)

client = MongoClient('localhost', 27017)
db = client.gc
collection = db.subj
zipped = "data-4-structure-3.json.zip"

COUNTER, INSERT_LIMIT = 0, 1000000

with ZipFile(zipped) as myzip:
    for name in myzip.namelist():
        with myzip.open(name) as myfile:
            data = json.loads(myfile.read().decode("utf-8"))
            for d in data:
                p = randint(1, 5)
                if p == 1:
                    try:
                        collection.insert_one(d)
                    except KeyboardInterrupt:
                        print("Sorry!")
                        exit(1)
        if COUNTER == INSERT_LIMIT:
            break

collection.create_index([("data.museum.name", pymongo.TEXT)], default_language="russian")