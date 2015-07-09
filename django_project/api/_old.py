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

@csrf_exempt
def signup(request):
    try:
        #return HttpResponse(request,content_type="application/json")
        data = json.loads(request.body)
        fname = data['fname']
        lname = data['lname']
        mob = data['mob']
        gender = data['gender']
        dob = data['dob']
        mstatus = data['mstatus']
        try:
            aniv = data['aniv']
        except:
            aniv = ""
        cemail = data['cemail']
        cname = data['cname']
        cadd = data['cadd']
        salary = data['salary']
        intr = data['interest']
        key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) + cemail        # This should be unique
        client = pymongo.MongoClient()
        db = client.perkkx
        collection = db.user
        collection.insert({"userID":key,"fname":fname,"lname":lname,"mob":mob,"gender":gender,"mstatus":mstatus,"aniv":aniv,"cname":cname,"cadd":cadd,"salary":salary,"intr":intr})
        res = { "success": 1, "userID": key }
        return HttpResponse(dumps(res),content_type="application/json")
    except:
        raise
        return HttpResponse(failure, content_type="application/json")

@csrf_exempt
def getdata(request):
    try:
        id = json.loads(request.body)['id']
        client = pymongo.MongoClient()
        db = client.perkkx
        collection = db.user
        data = collection.find({"userID":id})
        return HttpResponse(data,content_type="application/json")
    except:
        return HttpResponse(failure,content_type="application/json")

@csrf_exempt
def updateuser(request):
    try:
        #return HttpResponse(request,content_type="application/json")
        data = json.loads(request.body)
        fname = data['fname']
        lname = data['lname']
        mob = data['mob']
        gender = data['gender']
        dob = data['dob']
        mstatus = data['mstatus']
        try:
                aniv = data['aniv']
        except:
                aniv = ""
        cemail = data['cemail']
        cname = data['cname']
        cadd = data['cadd']
        salary = data['salary']
        intr = data['interest']
        key = data['userID']
        client = pymongo.MongoClient()
        db = client.perkkx
        collection = db.user
        collection.update({"key":key},{"fname":fname,"lname":lname,"mob":mob,"gender":gender,"mstatus":mstatus,"aniv":aniv,"cname":cname,"cadd":cadd,"salary":salary,"intr":intr},{ "upsert": "False" })
        return HttpResponse(dumps({"success": 1}),content_type="application/json")
    except:
        raise
        return HttpResponse(failure,content_type="application/json")

