from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
import datetime
import random
import string
import json
from mailer import Mailer
from mailer import Message

dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.test


@csrf_exempt
def get_savings(request, userID):       # Dummy
    collection = db.order_data
    deals = collection.find({"userID":userID})
    total = 0
    for x in deals:
        total = total + x['discount']
    result = {
    "count":deals.count(),
    "saving":total
    }
    return HttpResponse(dumps(result), content_type='application/json')

@csrf_exempt
def get_followed(request, userID):      # Dummy
    try:
        collection = db.user
        result = collection.find_one({"userID":userID})
        merchants = result['followed']
        data = []
        merchant = db.merchants
        for x,y in merchants.items():
            mm = merchant.find_one({"vendor_id":int(x)})
            temp = {
            "vendor_name": mm['vendor_name'],
            "address":  mm['address']['text'],
            "cat": mm['cat'],
            "rating": mm['rating'],
            "date": y
            }
            data.append(temp)
        return HttpResponse(dumps({"data":data}), content_type='application/json')
    except:
        return HttpResponse(dumps({"sucess":0}), content_type='application/json')
