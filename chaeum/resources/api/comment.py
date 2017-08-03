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
    'contents', dest='contents',
    type=str, location='json', required=True,
    help='contents is fault',
)
post_parser.add_argument(
    'review_id', dest='review_id',
    type=int, location='json', required=True,
    help='review_id is fault',
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
    'mod_date': fields.DateTime,
    'review_id': fields.Integer,
    'owner_id': fields.Integer,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}


def create_comment(contents, review_id, owner_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
            INSERT
              INTO TBCOMMENT(category, reg_date, mod_date, review_id, owner_id)
            VALUES (%s, now(), now(), %s, %s)
        """
        review = cursor.execute(query, (contents, review_id, owner_id))

        if cursor.rowcount == 1:
            retObj = {
                "category_id": cursor.lastrowid,
                "contents": contents,
                "review_id": review_id,
                "owner_id": owner_id,
            }
    except Exception as e:
        print(e, file=sys.stdout)
        return False, None
    finally:
        conn.close()

    return True, retObj


def fetch_list(review_id, limit, offset, ordering, asc):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT comment_id, contents, reg_date, mod_date, review_id, owner_id
          FROM TBCOMMENT
         WHERE review_id = %s
    """

    query = query + 'ORDER BY ' + ordering + ' ' + asc + ' \n'
    if limit is not None and offset is not None:
        query = query + 'LIMIT ' + offset + ', ' + limit

    try:
        cursor.execute(query, (review_id,))
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            comment_id, contents, reg_date, mod_date, review_id, owner_id = item
            retObj = {
                "comment_id": comment_id,
                "contents": contents,
                "reg_date": reg_date,
                "mod_date": mod_date,
                "review_id": review_id,
                "owner_id": owner_id,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


class Comment(Resource):

    @marshal_with(result_fields)
    def post(self):
        args = post_parser.parse_args()
        result, comment = create_comment(args.contents, args.review_id, args.owner_id)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': comment
            }
            return responseObject, 200

    @marshal_with(result_fields)
    # @jwt_required
    def get(self, review_id=None):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        review_id = args.get('review_id')
        limit = args.get('limit')
        offset = args.get('offset')
        ordering = args.get('ordering')
        asc = args.get('asc')
        if ordering is None:
            ordering = 'like_cnt'
        if asc is None:
            asc = 'DESC'

        if review_id is not None:
            result, comment = fetch_list(review_id, limit, offset, ordering, asc)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': comment
            }
            return responseObject, 200