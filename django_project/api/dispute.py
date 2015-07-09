import pymongo
import datetime
import random
import string
import json
import sys

dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.test

"""
def check_dispute(object):
    record = db.find({
        "userID": object["userID"],
        "cID": object["cID"],
        "rcode": object["rcode"]
    })
    if record['ustatus'] == "used" and record['mstatus'] == "expired":  #NOT possible
        record['mstatus'] = 'disputed'
    elif record['ustatus'] == "used" and record['mstatus'] == "pending":            # Dispute according to new rules, aka pending
        record['mstatus'] = 'disputed'
    elif record['ustatus'] == 'expired' and record['mstatus'] == 'pending':
        record['mstatus'] = 'expired'
    elif record['ustatus'] == 'expired' and record['mstatus'] == 'used':    # Auto resolve dispute
        record['ustatus'] == 'used'

    db.update({
        "userID": object["userID"],
        "cID": object["cID"],
        "rcode": object["rcode"]
    }, record, False)
"""


