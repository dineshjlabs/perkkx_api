from bson.json_util import dumps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template,Context
import pymongo
from datetime import datetime, date
import calendar
from .data_query import db, get_data

@csrf_exempt
def get_pending(request, vendor_id):
    page, total_pages, init_data = get_data(request, int(vendor_id), "pending")       # Get initial data from mongo
    result_list = []
    for data in init_data:
        used_on = datetime.strptime(data["used_on"], "%d/%m/%Y %H:%M:%S")               # common, except for expired
        data["used_on"] = int(calendar.timegm( used_on.utctimetuple()))                
        deal = db.deals.find_one({"cID": data["cID"]}, {"deal": True, "expiry": True})  # common
        data["deal"] = deal["deal"]
        data["expiry"] = int(calendar.timegm(                                           # common, except for disputed
            datetime.strptime(deal["expiry"], "%d/%m/%Y").utctimetuple()
        ))
        result_list.append(data)

    res = {
        "page": page,
        "total_pages": total_pages,
        "data": result_list
    }
    return HttpResponse(dumps(res), content_type="application/json")
