from __future__ import print_function

from flask import request
from flask_restful import fields, marshal_with, reqparse, Resource
from flask_jwt_extended import JWTManager, jwt_required

from chaeum import cnx_pool, jwt

def isstr(s):
    return s if s else ''

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'hairprd_nm', dest='hairprd_nm',
    type=str, location='json', required=True,
    help='hairprd_nm is fault',
)
post_parser.add_argument(
    'price', dest='price',
    type=int, location='json', required=True,
    help='price is fault',
)
post_parser.add_argument(
    'capacity', dest='capacity',
    type=str, location='json', required=True,
    help='capacity is fault',
)
post_parser.add_argument(
    'like_cnt', dest='like_cnt',
    type=int, location='json', required=True,
    help='like_cnt is fault',
)

post_parser.add_argument(
    'brnd_id', dest='brnd_id',
    type=int, location='json', required=True,
    help='brnd_id is fault',
)

list_fields = {
    'hairprd_id': fields.Integer,
    'hairprd_nm': fields.String,
    'price': fields.Integer,
    'capacity': fields.String,
    'like_cnt': fields.Integer,
    'reg_date': fields.DateTime,
    'brnd_id': fields.Integer,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}


def fetch_list(owner_id, limit, offset, ordering):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.hairprd_id, a.hairprd_nm, a.price, a.capacity, a.like_cnt, a.reg_date, a.brnd_id
          FROM TBHAIRPRD a, TBLIKE b
         WHERE b.category = 2
           AND b.owner_id = %s
           AND a.hairprd_id = b.hairprd_id
    """
    query = query + 'ORDER BY ' + ordering + ' DESC \n'
    if limit is not None and offset is not None:
        query = query + 'LIMIT ' + offset + ', ' + limit

    try:
        cursor.execute(query, (owner_id,))
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            hairprd_id, hairprd_nm, price, capacity, like_cnt, reg_date, brnd_id = item
            retObj = {
                "hairprd_id": cursor.lastrowid,
                "hairprd_nm": hairprd_nm,
                "price": price,
                "capacity": capacity,
                "like_cnt": like_cnt,
                "reg_date": reg_date,
                "brnd_id": brnd_id,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


class HairPrd_Like(Resource):

    @marshal_with(result_fields)
    # @jwt_required
    def get(self):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        owner_id = args.get('owner_id')
        limit = args.get('limit')
        offset = args.get('offset')
        ordering = args.get('ordering')
        if ordering is None:
            ordering = 'reg_date'

        result, hairprd = fetch_list(owner_id, limit, offset, ordering)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': hairprd
            }
            return responseObject, 200