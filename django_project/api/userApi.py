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
db = dbclient.perkkx

@csrf_exempt
def fMerchant(request,user,vendor):
    try:
        collection = db.user
        verified = collection.find_one({"userID":user})
        if 'followed' in verified:
            verified['followed'].update({vendor:datetime.datetime.now().strftime("%d/%m/%Y")})
        else:
            verified.update({"followed":{vendor:datetime.datetime.now().strftime("%d/%m/%Y")}})
        collection.update({"userID":user},{"$set": verified} ,False)
        return HttpResponse(dumps({"success": '1'}),content_type="application/json")
    except:
        return HttpResponse(dumps({"success": '0'}),content_type="application/json")

@csrf_exempt
def user_exist(request):
    global db
    result = dict() 
    data = json.loads(request.body)
    email = data['email']
    doc = db.user.find_one({"email":email}) 
    if doc != None:
        result['success'] = '1'
        result['userID'] = doc['userID']
        result['name'] = doc['fname'] + ' ' + doc['lname']
        result['email'] = doc['email']
        if 'cname' in doc:
            result['cname'] = doc['cname']
        else:
            result['cname'] = ""
        return HttpResponse(dumps(result), content_type="application/json")
    else:
        result['success']='0'
        result['reason'] = "NO INFORMATION FOUND FOR GIVEN EMAIL : "+ email

        return HttpResponse(dumps(result), content_type="application/json")
        
""" generating user ID"""
def userIdGenPartial():
    p1 = ''.join(random.choice(string.ascii_lowercase) for _ in range(2))
    p2 = ''.join(random.choice(string.digits) for _ in range(4))
    return p1 + p2

def userIdGen():
    global db
    res = userIdGenPartial()
    collection = db.user
    while db.user.find({"userID": res}).count() > 0:
        res = userIdGenPartial()
    return res
# ---------------------- #

@csrf_exempt
def signup(request):	   
    global db
    try:
        #return HttpResponse(request,content_type="application/json")
        data = json.loads(request.body)
	data = data['data']
        """fname = data['fname']
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
        #db = dbclient.perkkx"""
        failure = dict()
	collection = db.user
        if collection.find({"$or": [ {"email": data['email']}]}).count() is not 0:
            return HttpResponse(failure,content_type="application/json")

        #key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))    # TODO
        #key = '12345599'
        key = userIdGen()
        data.update({"userID":key})
        data.update({"verified":"N"})
        collection.insert(data)
        res = { "success":'1', "userID": key }
        return HttpResponse(dumps(res),content_type="application/json")
    except:
        raise
        failure['success'] = '0'
        failure['reason'] = "DATA ALREADY EXIST"
	return HttpResponse(dumps(failure), content_type="application/json")

@csrf_exempt
def getdata(request):
    global db
    failure = dict()
    try:
        id = request.GET['userID']
        #db = dbclient.perkkx
        collection = db.user
        data = collection.find({"userID":id})
	if data.count() is 1:
            return HttpResponse(dumps(data[0]),content_type="application/json")
	else:
	    failure['success'] = '0'
	    failure['reason'] = "NO USER FOUND"
	    return HttpResponse(dumps(failure),content_type="application/json")    
    except:
	raise
        failure['success'] = '0'
        failure['reason'] = "NO USER FOUND"

        return HttpResponse(dumps(failure),content_type="application/json")
def conf_mail(email,code):
    import sendgrid
    sg = sendgrid.SendGridClient('ashmeetjlabs', 'jlabs@123')
    message = sendgrid.Mail()
    message.add_to(email)
    message.set_subject("Verify your Corporate ID")
    message.set_html("Click <a href='http://api.jlabs.co/perkkx/verifyUser/" + code + "'>Here</a> to verify your account and get all deals." )
    message.set_from('Verify <no-reply@perkkx.com>')
    return sg.send(message)

@csrf_exempt
def updateuser(request):
    global db
    failure = dict()
    try:
        #return HttpResponse(request,content_type="application/json")
        data = json.loads(request.body)
        data = data['data']
        """fname = data['fname']
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
        #db = dbclient.perkkx"""
        collection = db.user
        key = data['userID']
        data.pop('userID')
        verified = collection.find_one({"userID":key})
        try:
            #conf_mail(data['cemail'],key)
            if verified['verified'] in 'N':
                verify = ''.join(random.choice(string.ascii_lowercase) for _ in range(4))
                code = key + "_" + verify
                status,msg = conf_mail(data['cemail'],code)
                data['code'] = verify
        except:
            print "hi"
        collection.update({"userID":key},{"$set": data} ,False)
        return HttpResponse(dumps({"success": '1'}),content_type="application/json")
    except:
        #raise
        failure['success'] = '0'
        failure['reason'] = "UPDATATION CAN'T BE PROCEEDED"
        return HttpResponse(dumps(failure),content_type="application/json")
@csrf_exempt
def user_coupons(request,uid):
    global db
    try:
        usedDeals = db.order_data.find({"userID":uid})
        pending = []
        expired = []
        used = []
        for x in usedDeals:
            vendorData = db.merchants.find_one({"vendor_id":int(x['vendor_id'])})
            address = vendorData['address']['text']
            dealData = db.deals.find_one({"cID":x['cID']})
            rep = {"vendor_name":vendorData['vendor_name'],
            "address":address,
            "code":x['rcode'],
            "expiry":dealData['expiry'],
            "used_on":x['used_on'].strftime("%d/%m/%Y %H:%M:%S"),
            "status":x['ustatus']}
            if x['ustatus'] in "pending":
                pending.append(rep)
            elif x['ustatus'] in "used":
                used.append(rep)
            elif x['ustatus'] in "expired":
                expired.append(rep)
        return HttpResponse(dumps({"pending":pending,"expired":expired,"used":used}),content_type="application/json")
    except Exception, e:
        raise
        failure = {"success": 0, "reason": str(e)}
        return HttpResponse(dumps(failure),content_type="application/json")
@csrf_exempt
def getFacility(request):
	failure = {"success": 0}
	if "domain" in request.GET.keys():
		global db
		domain = str(request.GET['domain'])
		collection = db.corp
		data = []
		search = {"domain":domain}
		temp = collection.find(search)
		if temp.count() > 0:
			for x in temp:
				x.pop("domain")
				x.pop("name")
				x.pop("_id")
				data.append(x)
			return HttpResponse(dumps(data),content_type="application/json")
		else:
			failure.update({"reason":"domain not found"})
			return HttpResponse(dumps(failure),content_type="application/json")
	else:
		failure.update({"reason":"Bad Request"})
		return HttpResponse(dumps(failure),content_type="application/json")

@csrf_exempt
def verifyUser(request,code):
    code = code.split("_")
    if len(code) == 2:
        global db
        collection = db.user
        data = collection.find_one({"userID":code[0]})
        if data:
            try:
                if data['verified'] == "Y":
                    return HttpResponse("Already Verified")
                if data['code'] in code[1].strip():
                    data['verified'] = "Y"
                    collection.update({"userID":code[0]},{"$set": data} ,False)
                    return HttpResponse("User has been verified. COntinue to app")
                else:
                    return HttpResponse("Invalid URL")
            except:
                return HttpResponse("Invalid Username")
        else:
            return HttpResponse("Invalid Username")
    else:
        return HttpResponse("Invalid Format")