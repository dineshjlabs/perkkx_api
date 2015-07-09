from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
from datetime import datetime, date
import calendar
from .data_query import db, get_data
import re

def _get_unix_timestamp(data):      # data is datetime
    return int(calendar.timegm(
            data.utctimetuple()
        ) * 1000)
    
""""
@csrf_exempt
def validate_code(request):
    try:
        code = request.GET['rcode']
        # Assert the code length
        userID = code[:-2]
        if db.user.find({"userID": userID}).count() == 0:
            return HttpResponse(dumps({"valid": False}), content_type='application/json')
        else:
            return HttpResponse(dumps({"valid": True, "rcode": code }))
    except:
        return HttpResponse(dumps({"valid": False,"error": "Invalid code"}), content_type='application/json')

"""

def get_dealOpts(vendor_id):
    deals = db.deals.find({ "vendor_id": vendor_id})
    dealOpts = []
    for d in deals:
        if datetime.strptime(d["expiry"], "%d/%m/%Y") > datetime.now():
            dealOpts.append({
                "deal": d["deal"],
                "cID": d["cID"]
            })
    return dealOpts

@csrf_exempt
def validate_code(request):
    invalid_code = {"valid": False, "error": "Invalid code"}
    try:
        vendor_id = int(request.GET['vendor_id'])
        code = request.GET['rcode'].lower()
        res = db.order_data.find_one({"rcode": code, "userID": code[:-2], "vendor_id": vendor_id}, {"_id": False, "used_on": True, "rcode": True, "cID": True, "userID": True, "mstatus": True})
        if res:
            if res["mstatus"] == "pending" or res['mstatus'] == 'disputed':
                res.pop("mstatus")

                cid = res['cID']
                dealOpts = get_dealOpts(vendor_id)

                res['dealOpts'] = dealOpts

                indexArr = [idx for idx, val in enumerate(dealOpts) if val['cID'] == cid]
                if indexArr:
                    res['selectedIndex'] = indexArr[0]
                else:
                    res['selectedIndex'] = 0

                res["used_on"] = _get_unix_timestamp(res["used_on"])
                #deal = db.deals.find_one({"cID": res["cID"]})
                #res["deal"] = deal["deal"]
                #res["desc"] = deal["desc"]
                return HttpResponse(dumps({"valid": True, "data": res}), content_type='application/json')
            else: return HttpResponse(dumps(invalid_code), content_type='application/json')
        else:
            user = db.user.find_one({"userID": code[:-2]})
            if not user:
                return HttpResponse(dumps({"valid": False, "error": "Wrong user id "+code[:-2]}), content_type='application/json')
            """
            # Assuming that the last two characters are cID
            cid = code[-2:]
            creg = re.compile("^"+cid+"$", re.IGNORECASE)
            deals = db.deals.find({"cID": creg})
            #return HttpResponse(dumps({"valid": False, "debug": deals.count()}), content_type='application/json')
            deal = {}
            for d in deals:
                if datetime.strptime(d["expiry"], "%d/%m/%Y") > datetime.now():
                    deal = d
                    break

            if not deal:
                return HttpResponse(dumps(invalid_code), content_type='application/json')
            """
            dealOpts = get_dealOpts(vendor_id)
            """
            deals = db.deals.find({ "vendor_id": vendor_id})
            dealOpts = []
            for d in deals:
                if datetime.strptime(d["expiry"], "%d/%m/%Y") > datetime.now():
                    dealOpts.append({
                        "deal": d["deal"],
                        "cID": d["cID"]
                    })
            """
            if not dealOpts:
                return HttpResponse(dumps({"valid": False, "error": "No dealOpts"}), content_type='application/json')

            result = {
                "used_on": int(calendar.timegm(datetime.now().utctimetuple()) * 1000),
                "rcode": code,
                "userID": code[:-2],
                "dealOpts": dealOpts,
                "selectedIndex": 0
            }
            return HttpResponse(dumps({"valid": True, "data": result}), content_type='application/json')
        
        """
        else:
            return HttpResponse(dumps({"valid": False,"error": "Invalid code"}), content_type='application/json')
        """
    except Exception, e:
        return HttpResponse(dumps({"valid": False,"error": "Invalid code and error " + str(e)}), content_type='application/json')
        

@csrf_exempt
def get(request, typ, vendor_id):
    "GET requests for typ [pending, used, expired, disputed] and vendor_id"
    if typ not in ['pending', 'used', 'expired', 'disputed']:
        return HttpResponse(dumps({"error": "Unknown type"}), content_type='application/json')

    page, total_pages, init_data = get_data(request, int(vendor_id), typ)

    result_list = []
    for data in init_data:
        # Step 1. Get the deal value
        deal = db.deals.find_one({"cID": data["cID"]}, {"deal": True, "expiry": True})  # common
        data["deal"] = deal["deal"]

        # Step 2. Get expiry
        if typ not in ["used"]:
            data["expiry"] = int(calendar.timegm(                                           # common, except for disputed
                datetime.strptime(deal["expiry"], "%d/%m/%Y").utctimetuple()
            ) * 1000)
            
        # Step 3. Get used_on
        if typ != "expired":
            data["used_on"] = _get_unix_timestamp(data["used_on"])
        else:
            del data["used_on"]
        
        # Step 4. Change submitted_on to proper format
        if typ == "used":
            data["submitted_on"] = _get_unix_timestamp(data["submitted_on"])

        result_list.append(data)

    result = {
        "page": page,
        "total_pages": total_pages,
        "data": result_list
    }

    return HttpResponse(dumps(result), content_type="application/json")

@csrf_exempt
def get_count(request, vendor_id):
    "GET the counts for each type of deals in used, expired, disputed"
    try:
        collection = db.order_data
        result = {
            "used": collection.count({"vendor_id": int(vendor_id), "mstatus": "used"}),
            "disputed": collection.count({"vendor_id": int(vendor_id), "mstatus": "disputed"})
        }
        return HttpResponse(dumps(result), content_type="application/json")
    except Exception, e:
        return HttpResponse(dumps({"error": str(e)}), content_type="application/json")

