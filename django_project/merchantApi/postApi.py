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

def update_order_data (query, req_data):
    collection = db.order_data
    record = collection.find_one(query)

    # Section 0: Update cID if original is different
    record['cID'] = req_data['cID']

    # Section 1: Merchant Initiated
    if record['ustatus'] == "pending":
        record['mstatus'] = req_data['status']
        record['ustatus'] = req_data['status']  # Will be used only
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

    result = collection.update_one(query, record, False)
    return result['updatedExisting']

" Post data from the merchnat app "
@csrf_exempt
def post(request, vendor_id):
    try:
        req_data = json.loads(request.body.decode())
        collection = db.order_data
        
        if 'orig_cID' in req_data:
            query = {
                "vendor_id": int(vendor_id),
                "cID": req_data["orig_cID"],
                "userID": req_data["rcode"][:-2],
                "rcode": req_data["rcode"]
            }
            while not update_order_data(query, req_data):
                pass
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
