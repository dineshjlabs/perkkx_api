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

@csrf_exempt
def merchants(request, mID):
    global db
    #db = dbclient.perkkx
    merchant = db.merchants.find_one({"vendor_id": int(mID)})
    if merchant is None:
        return HttpResponse(dumps({}), content_type="application/json")

    s = []
    g = []
    deals = db.deals.find(
        {"vendor_id": merchant['vendor_id']},
        {"rcodes": False, "usedrcodes": False}
    )
    for deal in deals:
        if deal['type'] == 'single':
            s.append(deal)
        else:
            g.append(deal)
    merchant['deals'] = {
        "single": s,
        "group": g
    }
    return HttpResponse(dumps(merchant), content_type="application/json")
@csrf_exempt
def get_coupons(request,mID):
	global db
	try:
		collection = db.deals
		result = collection.find({"vendor_id":int(mID)})
		used = {}
		for x in result:
			used.update({x['cID']:x['usedrcodes']})
		res = { "success": 1, "coupons": used }
		return HttpResponse(dumps(res),content_type="application/json")
	except:
		return HttpResponse(failure, content_type="application/json")
