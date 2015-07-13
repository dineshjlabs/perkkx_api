from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
import datetime
import random
import string
import json
failure = dumps({ "success": 0 })
dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.test

limit = 2

@csrf_exempt
def test(request):
        collection = db.googleapitest
        collection.insert({"hi":"hi"})
        return HttpResponse("Bad Request",content_type="application/json")

""" OLD
@csrf_exempt
def get_coupon(request):
	try:
		collection = db.deals
		data = json.loads(request.body)
		result = collection.find_one({"vendor_id":data['vendor_id'],"cID":data["cID"]})
		user = db.order_data.find_one({"userID":data['userID'],"cID":data["cID"]})
		if user:
			return HttpResponse(dumps({ "success": 1, "code": user['rcode'] }), content_type="application/json")
		if db.order_data.find({"userID":data['userID'],"ustatus":"pending"}).count() >=2:
			return HttpResponse(dumps({ "success": 0, "reason": "redeem limit reached" }), content_type="application/json")
		else:
			codes = result['rcodes']
			code = codes.pop()
			result['rcodes'] = codes
			result['usedrcodes'].append(code)
			collection.update({"vendor_id":data['vendor_id'],"cID":data["cID"]},{"$set":result},False)
			couponRecord = {"vendor_id":data['vendor_id'],"cID":data["cID"],"userID":data['userID'],"rcode":code,"used_on":datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),"ustatus":"pending","mstatus":"pending"}
			db.order_data.insert(couponRecord)
			return HttpResponse(dumps({ "success": 1, "code": code }), content_type="application/json")
	except:
		return HttpResponse(failure, content_type="application/json")
"""

"""
{
    userID: aa1111,
    cID: A1
}
"""
success = { "success": 1 }
failure = { "success": 0 }
@csrf_exempt
def getUserDeals(request,userID):
    collection = db.order_data
    t = collection.find({
            "userID": userID,
            "ustatus": "pending"
        })
    data = []
    if t:
        for x in t:
            x = x



@csrf_exempt
def check_coupon(request):
    try:
        collection = db.order_data
        data = json.loads(request.body)
        # 1. Check if this user has already subscribed to deal
        t1 = collection.find_one({
            "userID": data["userID"],
            "cID": data["cID"],
            "ustatus": "pending"
        })
        if t1:
            result = failure.copy()
            result.update({"rcode": t1["rcode"]})
            return HttpResponse(dumps(result), content_type="application/json")

        # 2. Security check, validity of cID
        if db.deals.find({"cID": data["cID"]}).count() == 0:
            result = failure.copy()
            result.update({"error": "Invalid cID"})
            return HttpResponse(dumps(result), content_type="application/json")
        # 3 Check if user is verified or not
        users = db.user
        user = users.find_one({"userID":data['userID']})
        if user['verified'] in 'Y':
            limit = 2
        else:
            limit = 1

        # 4 Check if the user is over his/her limit for coupons
        t2 = collection.find({
            "userID": data["userID"],
            "ustatus": "pending"
        }).count()
        if t2 >= limit:
            return HttpResponse(dumps(failure), content_type="application/json")
        else:
            return HttpResponse(dumps(success), content_type="application/json")
    except Exception, e:
        result = failure.copy()
        result.update({"error": str(e)})
        return HttpResponse(dumps(result), content_type="application/json")

@csrf_exempt
def add_coupon(request):
    try:
        collection = db.order_data
        data = json.loads(request.body)
        vendor = db.deals.find_one({"cID": data["cID"]})
        if vendor:
            collection.insert({
                "userID": data["rcode"][:-2],
                "rcode": data["rcode"],
                "ustatus": "pending",
                "mstatus": "pending",
                "vendor_id": vendor["vendor_id"],
                "cID": data["cID"],
                "used_on":datetime.datetime.now()       ## Mongo can store date directly !!
            })
            return HttpResponse(dumps(success), content_type="application/json")
        else:
            result = failure.copy()
            result.update({"error": "deal doesn't exist"})
            return HttpResponse(dumps(failure), content_type="application/json")
    except Exception, e:
        result = failure.copy()
        result.update({"error": str(e)})
        return HttpResponse(dumps(result), content_type="application/json")

