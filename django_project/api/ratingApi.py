from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
import datetime
import random
import string
import json

#from dispute import check_dispute

dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.test

def updateRating (vendor_id, rating):
    collection = db.merchant
    merchant = collection.find_one({"vendor_id": vendor_id})
    newRating = (merchant['raing'] + rating) / 2
    result = collection.update(merchant, {"$set": {"rating": newRating}}, False)
    return result['updatedExisting']


def check_dispute (rcode, cID):
    collection = db.order_data
    order = collection.findd_one({"cID": cID, "userID": rcode[:-2], "rcode": rcode})

    ustatus = order['ustatus']
    mstatus = order['mstatus']
    res = ''

    if ustatus == 'used' and mstatus == 'pending':      # New rules
        res = 'disputed'
    elif ustatus == 'expired' and mstatus == 'pending':
        res = 'expired'
    elif ustatus == 'expired' and mstatus == 'used':    # resolve dispute
        res = 'used'
    else:
        res = 'disputed'

    result = collection.update(order, {"$set": {"mstatus": res}}, False)
    return result['updatedExisting']


def response (obj):
    return HttpResponse(dumps(obj), content_type='application/json')

"""
format:
JSON body:
    rcode, vendor_id, cID
    das: <boolean> //did not avail service
    rating: optional iff not das
"""
@csrf_exempt
def rate_merchant (request):
    try:
        data = json.loads(request.body)
        uID = data['rcode'][:-2]
        vID = data['vendor_id']
        das = data['das']
        # Step 1: Save rating to user db (opt)
        if not das:
            db.user.update({"userID": uID}, {"$push": {"rating": {
                "value": data['rating'],
                "vendor_id": vID,
                "date": datetime.now()
            }}}, False)
            # Step 2: Modify merchant rating (opt)
            while not updateRating (vID, data['rating']):
                pass

        # Step 3: Update order_data and resolve conflict        //Dicey, check code
        if das:
            status = "expired"
        else:
            status = "used"
        db.order_data.update({
            "vendor_id": vID,
            "userID": uID,
            "rcode": data['rcode'],
            "cID": data['cID']
        }, {"$set": {"ustatus": status}}, False)
        while not check_dispute(data['rcode'], data['cID']):
            pass


        return response({"success": 1})
    except Exception e:
        return response({"success": 0, "error": "Exception "+str(e)})

@csrf_exempt
def check_pending (request):
    pass
