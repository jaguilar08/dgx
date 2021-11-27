from bson import ObjectId
from flask import Blueprint, jsonify, request
from re import compile, IGNORECASE
# aplication imports
from mongoCon import MongoCon, DESC_ORDER
from utils.decorators import login_required, validate_request, activity_log_decorator
from utils.recycle import Recycle
from utils.responses import not_found, success_ok, make_response


recycle = Blueprint('recycle', __name__)


@recycle.route('/get_recycle', methods=['POST'])
@login_required
@validate_request({
    '_id': {'type': 'object_id'},
})
def get_recycle():
    recycle = {}
    with MongoCon() as cnx:
        query = {"_id": ObjectId(request.json["_id"])}
        recycle = cnx.recycle.find_one(query)
    if recycle:
        recycle['events'].reverse()
        recycle = jsonify(recycle)
    else:
        recycle = not_found("recycle")
    return recycle


@recycle.route('/get_recycles', methods=['POST'])
@login_required
@activity_log_decorator('Get recycles')
@validate_request(headers=True)
def get_recycles():
    recycles = []
    with MongoCon() as cnx:
        params = {"events": False, "creation_date": False, "created_by": False}
        query = {"dealer_code": request.headers["current-dealer"]}
        recycles = list(cnx.recycle.find(query, params).sort('creation_date', -1))
    return jsonify(recycles)


@recycle.route('/search_recycle', methods=['POST'])
@login_required
@validate_request({
    'search': {'type': 'string', "required": False}
}, headers=True)
@activity_log_decorator('Search recycle')
def search_recycle():
    recycles = []
    with MongoCon() as cnx:
        search = request.json.get("search", "")
        query = [
            {
                "$match": {
                    "group_code": request.headers["current-group"],
                    "dealer_code": request.headers["current-dealer"],
                    "$or": [
                        {"type": compile(search, IGNORECASE)},
                        {"display": compile(search, IGNORECASE)}
                    ]
                }
            },
            {
                "$sort": {'creation_date': DESC_ORDER}
            },
            {
                "$project": {
                    "item": False
                }
            }
        ]
        recycles = list(cnx.recycle.aggregate(query))
    return jsonify(recycles)


@recycle.route('/delete_recycle', methods=['POST'])
@login_required
@validate_request({
    '_id': {'type': 'object_id'}
})
@activity_log_decorator('Delete recycle')
def delete_recycle():
    _id = request.json.pop('_id', False)
    if _id:
        data_id = ObjectId(_id)
        with MongoCon() as cnx:
            item = cnx.recycle.find_one({"_id": data_id})
            if item:
                cnx.recycle.delete_one(item)
            else:
                return not_found('recycle')
        return success_ok()
    else:
        return not_found('recycle')


@recycle.route('/delete_massive_recycle', methods=['POST'])
@login_required
@validate_request({
    'ids': {'type': 'list'}
})
@activity_log_decorator('Delete massive recycle')
def delete_massive_recycle():
    ids = request.json.pop('ids', False)
    if ids:
        with MongoCon() as cnx:
            query = {"_id": {"$in": [ObjectId(_id) for _id in ids]}}
            cnx.recycle.delete_many(query)
    else:
        return make_response(jsonify({"message": "Bad request, this operation need one or more ids."}), 400)
    return success_ok()


@recycle.route('/recover_recycle', methods=['POST'])
@login_required
@validate_request({
    '_id': {'type': 'object_id'}
})
@activity_log_decorator('Recover recycle')
def recover_recycle():
    Recycle.recovery_recycle(request.json["_id"])
    return success_ok()


@recycle.route('/recover_massive', methods=['POST'])
@login_required
@validate_request({
    'recover_list': {'type': 'object'},
})
@activity_log_decorator('Recover massive rows')
def recover_massive():
    ids = request.json.pop('ids', [])
    if ids:
        query = {"_id": {"$in": [ObjectId(_id) for _id in ids]}}
        Recycle.recovery_recycle_query(query)
    else:
        return make_response(jsonify({"message": "Bad request, this operation need one or more ids."}), 400)
    return success_ok()
