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
    'comp_hg_nm', dest='comp_hg_nm',
    type=str, location='json', required=True,
    help='comp_hg_nm is fault',
)
post_parser.add_argument(
    'comp_eng_nm', dest='comp_eng_nm',
    type=str, location='json', required=True,
    help='comp_eng_nm is fault',
)
post_parser.add_argument(
    'grade', dest='grade', choices=('A', 'B', 'C', 'D', 'E', 'F'),
    type=str, location='json', required=True,
    help='grade is fault',
)

list_fields = {
    'comp_id': fields.Integer,
    'comp_hg_nm': fields.String,
    'com_eng_nm': fields.String,
    'grade': fields.String,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}

def create_comp(comp_hg_nm, comp_eng_nm, grade):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
            INSERT
              INTO TBCOMP(comp_hg_nm, comp_eng_nm, grade)
            VALUES (%s, %s, %s)
        """
        comp = cursor.execute(query, (comp_hg_nm, comp_eng_nm, grade))

        if cursor.rowcount == 1:
            retObj = {
                "comp_id": cursor.lastrowid,
                "comp_hg_nm": comp_hg_nm,
                "comp_eng_nm": comp_eng_nm,
                "grade": grade,
            }
    except Exception as e:
        print(e, file=sys.stdout)
        return False, None
    finally:
        conn.close()

    return True, retObj

def fetch_list(keyword):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT comp_id, comp_hg_nm, comp_eng_nm, grade
          FROM TBCOMP
         WHERE comp_hg_nm like %s
            OR comp_eng_nm like %s
    """
    cursor.execute(query, ('%'+keyword+'%',))
    result = cursor.fetchall()
    retObjList = []

    try:
        for item in result:
            comp_id, comp_hg_nm, comp_eng_nm, grade = item
            retObj = {
                "comp_id": cursor.lastrowid,
                "comp_hg_nm": comp_hg_nm,
                "comp_eng_nm": comp_eng_nm,
                "grade": grade,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


class Comp(Resource):

    @marshal_with(result_fields)
    def post(self):
        args = post_parser.parse_args()
        result, comp = create_comp(args.comp_hg_nm, args.comp_eng_nm, args.grade)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': comp
            }
            return responseObject, 200

    @marshal_with(result_fields)
    # @jwt_required
    def get(self, comp_id=None):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        keyword = args.get('keyword')
        result, comp = fetch_list(isstr(keyword))

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': comp
            }
            return responseObject, 200