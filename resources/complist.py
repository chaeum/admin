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
#########################################
# 1 : hairprd
# 2 : med
#########################################
post_parser.add_argument(
    'category', dest='category', choices=('1', '2'),
    type=str, location='json', required=True,
    help='category is fault',
)
post_parser.add_argument(
    'comp_id', dest='comp_id',
    type=int, location='json', required=True,
    help='comp_id is fault',
)
post_parser.add_argument(
    'hairprd_id', dest='hairprd_id',
    type=int, location='json', required=False,
    help='hairprd_id is fault',
)
post_parser.add_argument(
    'med_id', dest='med_id',
    type=int, location='json', required=False,
    help='med_id is fault',
)

list_fields = {
    'complist_id': fields.Integer,
    'category': fields.String,
    'comp_id': fields.Integer,
    'hairprd_id': fields.Integer,
    'med_id': fields.Integer,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}

def create_complist(category, comp_id, hairprd_id, med_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
            INSERT
              INTO TBCOMP_LIST(category, comp_id, hairprd_id, med_id)
            VALUES (%s, %s, %s, %s)
        """
        comp = cursor.execute(query, (category, comp_id, hairprd_id, med_id))

        if cursor.rowcount == 1:
            retObj = {
                "complist_id": cursor.lastrowid,
                "category": category,
                "comp_id": comp_id,
                "hairprd_id": hairprd_id,
                "med_id": med_id,
            }
    except Exception as e:
        print(e, file=sys.stdout)
        return False, None
    finally:
        conn.close()

    return True, retObj

def fetch_list(comp_id, hairprd_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT complist_id, category, comp_id, hairprd_id, med_id
          FROM TBCOMP_LIST
         WHERE category = 1
           AND comp_id = %s
           AND hairprd_id = %s
    """
    cursor.execute(query, (comp_id, hairprd_id))
    result = cursor.fetchall()
    retObjList = []

    try:
        for item in result:
            complist_id, category, comp_id, hairprd_id, med_id = item
            retObj = {
                "complist_id": complist_id,
                "category": category,
                "comp_id": comp_id,
                "hairprd_id": hairprd_id,
                "med_id": med_id,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


class CompList(Resource):

    @marshal_with(result_fields)
    def post(self):
        args = post_parser.parse_args()
        result, complist = create_complist(args.category, args.comp_id, args.hairprd_id, args.med_id)

        if not result:
            responseObject = {
                'msg': 'Fail',
                'count': 0,
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'count': 1,
                'results': complist
            }
            return responseObject, 200

    # @marshal_with(result_fields)
    # # @jwt_required
    # def get(self, comp_id=None):
    #     # args = post_parser.parse_args()
    #     # current_user = get_jwt_identity()
    #     args = request.args
    #     keyword = args.get('keyword')
    #     result, comp = fetch_list(isstr(keyword))
    #
    #     if not result:
    #         responseObject = {
    #             'msg': 'Fail'
    #         }
    #         return responseObject, 401
    #     else:
    #         responseObject = {
    #             'msg': 'Success',
    #             'results': comp
    #         }
    #         return responseObject, 200