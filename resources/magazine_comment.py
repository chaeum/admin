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
post_parser.add_argument(
    'contents', dest='contents',
    type=str, location='json', required=True,
    help='contents is fault',
)
post_parser.add_argument(
    'magazine_id', dest='magazine_id',
    type=int, location='json', required=True,
    help='magazine_id is fault',
)
post_parser.add_argument(
    'owner_id', dest='owner_id',
    type=int, location='json', required=True,
    help='owner_id is fault',
)
list_fields = {
    'comment_id': fields.Integer,
    'contents': fields.String,
    'reg_date': fields.DateTime,
    'magazine_id': fields.Integer,
    'owner_id': fields.Integer,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}

def create_magazine_comment(contents, magazine_id, owner_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
            INSERT
              INTO TBMAGAZINE_COMMENT(contents, reg_date, magazine_id, owner_id)
            VALUES (%s, now(), %s, %s)
        """
        magazine_comment = cursor.execute(query, (contents, magazine_id, owner_id))

        if cursor.rowcount == 1:
            retObj = {
                "comment_id": cursor.lastrowid,
                "contents": contents,
                "magazine_id": magazine_id,
                "owner_id": owner_id,
            }
    except Exception as e:
        print(e, file=sys.stdout)
        return False, None
    finally:
        conn.close()

    return True, retObj

def fetch_list(contents):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT comment_id, contents, reg_date, magazine_id, owner_id
          FROM TBMAGAZINE_COMMENT
         WHERE contents like %s
    """
    cursor.execute(query, ('%'+contents+'%'))
    result = cursor.fetchall()
    retObjList = []

    try:
        for item in result:
            comment_id, contents, reg_date, magazine_id, owner_id = item
            retObj = {
                "comment_id": cursor.lastrowid,
                "contents": contents,
                "reg_date": reg_date,
                "magazine_id": magazine_id,
                "owner_id": owner_id,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


class Magazine_Comment(Resource):

    @marshal_with(result_fields)
    def post(self):
        args = post_parser.parse_args()
        result, magazine_comment = create_magazine_comment(args.contents, args.magazine_id, args.owner_id)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': magazine_comment
            }
            return responseObject, 200

    @marshal_with(result_fields)
    # @jwt_required
    def get(self, comment_id=None):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        contents = args.get('contents')
        result, magazine_comment = fetch_list(isstr(contents))

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': magazine_comment
            }
            return responseObject, 200