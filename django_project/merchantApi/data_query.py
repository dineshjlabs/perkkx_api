## Base Query get methods
from bson.json_util import dumps
from django.http import HttpResponse
import pymongo
import math

dbclient = pymongo.MongoClient("mongodb://45.55.232.5:27017")
db = dbclient.perkkx
limit = 10

def response(obj):
    return HttpResponse(dumps(obj), content_type='application/json')

" Execute the main query, based on the operation "
def _exec_query(vendor_id, operation):
    base_filter = {"vendor_id": False, "_id": False, "ustatus": False, "valid": False, "userID": False, "mstatus": False}     # TODO: Drop valid from database, also, remove mstatus
    if operation == "used":
        sortkey = "submitted_on"
    else: sortkey = "used_on"
    return db.order_data.find({"vendor_id": vendor_id, "mstatus": operation }, base_filter).sort([(sortkey, -1)])


" Get the initial data, i.e. perform the query "
def get_data(request, vendor_id, operation):
    lst = _exec_query(vendor_id, operation)
    try:
        page = int(request.GET['page'])
    except:
        page = 1

    start = (page-1)*limit
    end = start + limit - 1
    if end > lst.count():
        end = lst.count()
    if start > lst.count():
        start = lst.count() - limit

    res = lst[start:end]
    return page, int(math.ceil(res.count() / (limit*1.0))), res             # Works for even stupid splices like [-10:0]

