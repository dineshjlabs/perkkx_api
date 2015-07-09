from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import pymongo
from datetime import datetime, date
import calendar
from .data_query import db
import json

def _time_transform(data):
    tm = datetime.fromtimestamp(int(data / 1000))
    return tm
    #return tm.strftime("%d/%m/%Y %H:%M:%S")

def _copy_bill(dest, source):
    dest['submitted_on'] = _time_transform(source['submitted_on'])
    dest['paid'] = source['paid']
    dest['discount'] = source['discount']

" Post data from the merchnat app "
@csrf_exempt
def post(request, vendor_id):
    try:
        req_data = json.loads(request.body.decode())
        collection = db.order_data
        
        if 'orig_cID' in req_data:
            search = {
                "vendor_id": int(vendor_id),
                "cID": req_data["orig_cID"],
                "userID": req_data["rcode"][:-2],
                "rcode": req_data["rcode"]
            }
            record = collection.find_one(search)
            #record['rcode'] = req_data['rcode']
            
            # Section 1: Merchant Initiated
            if record['ustatus'] == "pending":
                # TODO
                # We need to send out a notification to user here, to let him rate 
                # the merchant or to select did-not avail service
                
                record['mstatus'] = req_data['status']
                if req_data['status'] == 'used':
                    _copy_bill(record, req_data)
                # Rest of the merchant initiated process to be done when user closes the coupon

            elif record['ustatus'] == 'used' and req_data['status'] == 'used':              # Section 2: User Initiated, was disputed, will resolve dispute
                record['mstatus'] = 'used'
                _copy_bill(record, req_data)
            elif record['ustatus'] == 'expired' and req_data['status'] == 'expired':    ## NOT possible
                record['mstatus'] = 'expired'
            elif record['ustatus'] == 'expired' and req_data['status'] == 'used':       # Resolve dispute ## NOT possible
                record['ustatus'] = 'used'
                record['mstatus'] = 'used'
                _copy_bill(record, req_data)
            else:                                                                       # DISPUTE
                record['mstatus'] = 'disputed'                                          # NOT possible

            collection.update(search, record)
            return HttpResponse(dumps({ "success": 1, "debug": "case1" }), content_type='application/json')
            
        else:
            newData = {
                "rcode": req_data["rcode"],
                "userID": req_data["rcode"][:-2],
                "cID": req_data["cID"],
                "used_on": _time_transform(req_data["used_on"]),
                "ustatus": req_data["status"],
                "vendor_id": int(vendor_id),
                "mstatus": req_data["status"]
            }
            if req_data['status'] == 'used':
                _copy_bill(newData, req_data)
            
            collection.insert(newData)
            return HttpResponse(dumps({ "success": 1 , "debug": "case2"}), content_type='application/json')

    except Exception, e:
        return HttpResponse(dumps({ "success": 0, "error": str(e) }), 'application/json')
