from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
from datetime import datetime
import random
import string
import json

#from dispute import check_dispute

dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.perkkx

def updateRating (vendor_id, rating):
    collection = db.merchants
    merchant = collection.find_one({"vendor_id": vendor_id})
    newRating = (merchant['rating'] + rating) / 2
    result = collection.update({"vendor_id": vendor_id, "rating": merchant['rating']}, {"$set": {"rating": newRating}}, False)
    return result['updatedExisting']


def check_dispute (query, ustatus):
    collection = db.order_data
    order = collection.find_one(query)

    mstatus = order['mstatus']

    if ustatus == 'used' and mstatus == 'pending':      # New rules
        res = 'disputed'
    elif ustatus == 'expired' and mstatus == 'pending':
        res = 'expired'
    elif ustatus == 'expired' and mstatus == 'used':    # resolve dispute
        res = 'used'
    else:
        res = 'disputed'

    result = collection.update(order, {"$set": {"mstatus": res, "ustatus": ustatus}}, False)
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
        vID = int(data['vendor_id'])
        das = data['das']
        # Step 0: check validity of user
        if db.user.count({"userID": uID}) == 0:
            return response({"success": 0, "error": "Invalid user"})

        # Step 1: Save rating to user db (opt)
        if not das:
            try:
                db.user.update({"userID": uID}, {"$push": {"rating": {
                    "value": data['rating'],
                    "vendor_id": vID,
                    "date": datetime.now()
                }}}, False)
            except Exception, e:
                return response({"sucess": 0, "error": "Step 1, "+str(e)})
            try:
                # Step 2: Modify merchant rating (opt)
                while not updateRating(vID, data['rating']):
                    pass
            except Exception, e:
                return response({"sucess": 0, "error": "Step 2, "+str(e), "vendor_id": vID})

        # Step 3: Update order_data and resolve conflict        //Dicey, check code
        try:
            if das:
                status = "expired"
            else:
                status = "used"

            query = {
                "vendor_id": vID,
                "cID": data['cID'],
                "rcode": data['rcode'],
                "userID": uID
            }

            if db.order_data.count(query) == 0:
                if status == "used":
                    query.update({
                        "used_on": datetime.now(),
                        "mstatus": "disputed",
                        "ustatus": "used"
                    })
                    db.order_data.insert(query)
            else:
                while not check_dispute(query, status):
                    pass
        except Exception, e:
            return response({"sucess": 0, "error": "Step 3, "+str(e)})
        """
        db.order_data.update({
            "vendor_id": vID,
            "userID": uID,
            "rcode": data['rcode'],
            "cID": data['cID']
        }, {"$set": {"ustatus": status}}, False)
        while not check_dispute(data['rcode'], data['cID']):
            pass
        """

        return response({"success": 1})
    except Exception, e:
        return response({"success": 0, "error": "Exception "+str(e)})

@csrf_exempt
def check_pending (request):
    try:
        userID = request.GET['userID']
        records = db.order_data.find({"userID": userID, "ustatus": "pending"},
                                     {"_id": False, "rcode": True, "cID": True, "mstatus": True, "paid": True, "discount": True})

        return response({"success": 1, "data": records})
    except Exception, e:
        return response({"success": 0, "error": "Exception "+str(e)})

@csrf_exempt
def get_ratings (request):
    pass