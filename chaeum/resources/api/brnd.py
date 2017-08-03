from __future__ import print_function

from flask import request
from flask_restful import fields, marshal_with, reqparse, Resource
from flask_jwt_extended import JWTManager, jwt_required
import sys

from chaeum import cnx_pool, jwt

def isstr(s):
    return s if s else ''

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'brnd_nm', dest='brnd_nm',
    type=str, location='json', required=True,
    help='brnd_nm is fault',
)
post_parser.add_argument(
    'like_cnt', dest='like_cnt',
    type=int, location='json', required=True,
    help='like_cnt is fault',
)

list_fields = {
    'brnd_id': fields.Integer,
    'brnd_nm': fields.String,
    'like_cnt': fields.Integer,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}

def create_brnd(brnd_nm, like_cnt):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
            INSERT
              INTO TBBRND(brnd_nm, like_cnt)
            VALUES (%s, %s)
        """
        hairprd = cursor.execute(query, (brnd_nm, like_cnt))

        if cursor.rowcount == 1:
            retObj = {
                "brnd_id": cursor.lastrowid,
                "brnd_nm": brnd_nm,
                "like_cnt": 0,
            }
    except Exception as e:
        print(e, file=sys.stdout)
        return False, None
    finally:
        conn.close()

    return True, retObj

def fetch_list(keyword, limit, offset, ordering):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT brnd_id, brnd_nm, like_cnt
          FROM TBBRND
         WHERE brnd_nm like %s
    """

    query = query + 'ORDER BY ' + ordering + ' DESC \n'
    if limit is not None and offset is not None:
        query = query + 'LIMIT ' + offset + ', ' + limit

    try:
        cursor.execute(query, ('%' + keyword + '%',))
        result = cursor.fetchall()
        retObjList = []
        for item in result:
            brnd_id, brnd_nm, like_cnt = item
            retObj = {
                "brnd_id": cursor.lastrowid,
                "brnd_nm": brnd_nm,
                "like_cnt": like_cnt,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


class Brnd(Resource):

    @marshal_with(result_fields)
    def post(self):
        args = post_parser.parse_args()
        result, brnd = create_brnd(args.brnd_nm, args.like_cnt)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': brnd
            }
            return responseObject, 200

    @marshal_with(result_fields)
    # @jwt_required
    def get(self, brnd_id=None):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        keyword = args.get('keyword')
        limit = args.get('limit')
        offset = args.get('offset')
        ordering = args.get('ordering')

        if ordering is None:
            ordering = 'like_cnt'

        if brnd_id is None:
            result, brnd = fetch_list(isstr(keyword),  limit, offset, ordering)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': brnd
            }
            return responseObject, 200