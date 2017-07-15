from __future__ import print_function

from flask import request
from flask_restful import fields, marshal_with, reqparse, Resource
from flask_jwt_extended import JWTManager, jwt_required
import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from chaeum import cnx_pool, jwt

def isstr(s):
    return s if s else ''

post_parser = reqparse.RequestParser()

list_fields = {
    'average': fields.Float,
    'count': fields.Integer,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}


def fetch_list_summary(category, hairprd_id, med_id, hairshop_id, clinic_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT round(avg(score), 1) as average, count(*) as cnt
          FROM TBREVIEW
    """

    if category is '1':
        if hairprd_id is not None:
            query += "where category = 1 \n"
            query += "  and hairprd_id = %s \n"
            query += "group by category, hairprd_id"
        else:
            return False, None
    elif category is '2':
        if med_id is not None:
            query += "where category = 2 \n"
            query += "  and med_id = %s \n"
            query += "group by category, med_id"
        else:
            return False, None
    elif category is '3':
        if hairshop_id is not None:
            query += "where category = 3 \n"
            query += "  and hairshop_id = %s \n"
            query += "group by category, hairshop_id"
        else:
            return False, None
    elif category is '4':
        if clinic_id is not None:
            query += "where category = 4 \n"
            query += "  and clinic_id = %s \n"
            query += "group by category, clinic_id"
        else:
            return False, None
    else:
        return False, None

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            average, cnt = item
            retObj = {
                "average": average,
                "count": cnt,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


class ReviewSummary(Resource):

    @marshal_with(result_fields)
    # @jwt_required
    def get(self, review_id=None):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        category = args.get('category')
        hairprd_id = args.get('hairprd_id')
        med_id = args.get('med_id')
        hairshop_id = args.get('hairshop_id')
        clinic_id = args.get('clinic_id')

        result, review = fetch_list_summary(category, hairprd_id, med_id, hairshop_id, clinic_id)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': review
            }
            return responseObject, 200