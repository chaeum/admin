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
    'title', dest='title',
    type=str, location='json', required=True,
    help='title is fault',
)
post_parser.add_argument(
    'contents', dest='contents',
    type=str, location='json', required=True,
    help='contents is fault',
)
post_parser.add_argument(
    'comment_cnt', dest='comment_cnt',
    type=int, location='json', required=True,
    help='comment_cnt is fault',
)
post_parser.add_argument(
    'like_cnt', dest='like_cnt',
    type=int, location='json', required=True,
    help='like_cnt is fault',
)

list_fields = {
    'magazine_id': fields.Integer,
    'title': fields.String,
    'contents': fields.String,
    'comment_cnt': fields.Integer,
    'like_cnt': fields.Integer,
    'reg_date': fields.DateTime,
    'mod_date': fields.DateTime,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}


def create_magazine(title, contents, comment_cnt, like_cnt):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
            INSERT
              INTO TBMAGAZINE(title, contents, comment_cnt, like_cnt, reg_date, mod_date)
            VALUES (%s, %s, %s, %s, now(), now())
        """
        magazine = cursor.execute(query, (title, contents, comment_cnt, like_cnt))

        if cursor.rowcount == 1:
            retObj = {
                "magazine_id": cursor.lastrowid,
                "title": title,
                "contents": contents,
                "comment_cnt": 0,
                "like_cnt": 0,
            }
    except Exception as e:
        print(e, file=sys.stdout)
        return False, None
    finally:
        conn.close()

    return True, retObj


def fetch_list(keyword, limit, offset, ordering, asc):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT magazine_id, title, contents, comment_cnt, like_cnt, reg_date, mod_date
          FROM TBMAGAZINE
         WHERE title like %s
            OR contents like %s
    """
    query = query + 'ORDER BY ' + ordering + ' ' + asc + ' \n'
    if limit is not None and offset is not None:
        query = query + 'LIMIT ' + offset + ', ' + limit

    try:
        cursor.execute(query, ('%' + keyword + '%', '%' + keyword + '%'))
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            magazine_id, title, contents, comment_cnt, like_cnt, reg_date, mod_date = item
            retObj = {
                "magazine_id": magazine_id,
                "title": title,
                "contents": contents,
                "comment_cnt": comment_cnt,
                "like_cnt": like_cnt,
                "reg_date": reg_date,
                "mod_date": mod_date,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


def fetch_detail(magazine_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT magazine_id, title, contents, comment_cnt, like_cnt, reg_date, mod_date
          FROM TBMAGAZINE
         WHERE magazine_id = %s
    """

    try:
        cursor.execute(query, (magazine_id,))
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            magazine_id, title, price, contents, comment_cnt, like_cnt, reg_date, mod_date = item
            retObj = {
                "magazine_id": magazine_id,
                "title": title,
                "price": price,
                "contents": contents,
                "comment_cnt": comment_cnt,
                "like_cnt": like_cnt,
                "reg_date": reg_date,
                "mod_date": mod_date,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


def fetch_list_cnt(keyword):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
            SELECT count(*)
              FROM TBMAGAZINE
             WHERE title like %s
                OR contents like %s
        """

    try:
        cursor.execute(query, ('%' + keyword + '%', '%' + keyword + '%'))
        result = cursor.fetchall()
        retObjList = []

        count = 0

        for item in result:
            count = item

    except Exception as e:
        return False, None
    finally:
        conn.close()

    return count


class Magazine(Resource):

    @marshal_with(result_fields)
    def post(self):
        args = post_parser.parse_args()
        result, magazine = create_magazine(args.title, args.contents, args.comment_cnt, args.like_cnt)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': magazine
            }
            return responseObject, 200

    @marshal_with(result_fields)
    # @jwt_required
    def get(self, magazine_id=None):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        keyword = args.get('keyword')
        limit = args.get('limit')
        offset = args.get('offset')
        ordering = args.get('ordering')
        asc = args.get('asc')
        count = 0
        if ordering is None:
            ordering = 'reg_date'
        if asc is None:
            asc = 'DESC'

        if magazine_id is None:
            result, magazine = fetch_list(isstr(keyword), limit, offset, ordering, asc)
            count = fetch_list_cnt(isstr(keyword))
        else:
            result, magazine = fetch_detail(magazine_id)
            if result is False:
                count = 0
            else:
                count = 1

        if not result:
            responseObject = {
                'msg': 'Fail',
                'count': count,
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'count': count,
                'results': magazine
            }
            return responseObject, 200