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
# 3 : hairshop
# 4 : clinic
# 5 : magazine
#########################################
post_parser.add_argument(
    'category', dest='category', choices=('1', '2', '3', '4', '5'),
    type=str, location='json', required=True,
    help='category is fault',
)
post_parser.add_argument(
    'owner_id', dest='owner_id',
    type=int, location='json', required=True,
    help='owner_id is fault',
)
post_parser.add_argument(
    'magazine_id', dest='magazine_id',
    type=int, location='json', required=False,
    help='magazine_id is fault',
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
post_parser.add_argument(
    'hairshop_id', dest='hairshop_id',
    type=int, location='json', required=False,
    help='hairshop_id is fault',
)
post_parser.add_argument(
    'clinic_id', dest='clinic_id',
    type=int, location='json', required=False,
    help='clinic_id is fault',
)

list_fields = {
    'bookmark_id': fields.Integer,
    'category': fields.String,
    'owner_id': fields.Integer,
    'magazine_id': fields.Integer,
    'hairprd_id': fields.Integer,
    'med_id': fields.Integer,
    'hairshop_id': fields.Integer,
    'clinic_id': fields.Integer,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}


def create_bookmark(category, owner_id, magazine_id=None, hairprd_id=None,
                med_id=None, hairshop_id=None, clinic_id=None):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
            INSERT
              INTO TBBOOKMARK(category, owner_id, magazine_id, hairprd_id,
                          med_id, hairshop_id, clinic_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        bookmark = cursor.execute(query, (category, owner_id, magazine_id, hairprd_id, med_id, hairshop_id, clinic_id))

        if cursor.rowcount == 1:
            retObj = {
                "bookmark_id": cursor.lastrowid,
                "category": category,
                "owner_id": owner_id,
                "magazine_id": magazine_id,
                "hairprd_id": hairprd_id,
                "med_id": med_id,
                "hairshop_id": hairshop_id,
                "clinic_id": clinic_id,
            }
    except Exception as e:
        print(e, file=sys.stdout)
        return False, None
    finally:
        conn.close()

    return True, retObj


def fetch_list(owner_id, limit, offset, ordering, asc):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.bookmark_id, a.category, b.user_id, b.nickname, c.hairprd_id, c.hairprd_nm,
               d.med_id, d.med_nm, e.hairshop_id, e.hairshop_nm, f.clinic_id, f.clinic_nm,
               g.magazine_id, g.title
          FROM TBBOOKMARK a
          LEFT JOIN TBUSER AS b
            ON a.owner_id = b.user_id
          LEFT JOIN TBHAIRPRD AS c
            ON a.hairprd_id = (CASE WHEN a.category = '1'
                                    THEN c.hairprd_id
                                    ELSE null
                               END)
          LEFT JOIN TBMEDICINE AS d
            ON a.med_id = (CASE WHEN a.category = '2'
                                    THEN d.med_id
                                    ELSE null
                               END)
          LEFT JOIN TBHAIRSHOP AS e
            ON a.hairshop_id = (CASE WHEN a.category = '3'
                                    THEN e.hairshop_id
                                    ELSE null
                               END)
          LEFT JOIN TBCLINIC AS f
            ON a.clinic_id = (CASE WHEN a.category = '4'
                                    THEN f.clinic_id
                                    ELSE null
                               END)
          LEFT JOIN TBMAGAZINE AS g
            ON a.magazine_id = (CASE WHEN a.category = '5'
                                    THEN g.magazine_id
                                    ELSE null
                               END)
         WHERE a.owner_id = %s
    """

    query = query + 'ORDER BY ' + ordering + ' ' + asc + ' \n'
    if limit is not None and offset is not None:
        query = query + 'LIMIT ' + offset + ', ' + limit

    try:
        cursor.execute(query, (owner_id,))
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            bookmark_id, category, owner_id, nickname, hairprd_id, hairprd_nm, med_id, med_nm, \
            hairshop_id, hairshop_nm, clinic_id, clinic_nm, magazine_id, title = item
            retObj = {
                "bookmark_id": bookmark_id,
                "category": category,
                "owner_id": owner_id,
                "nickname": nickname,
                "hairprd_id": hairprd_id,
                "hairprd_nm": hairprd_nm,
                "med_id": med_id,
                "med_nm": med_nm,
                "hairshop_id": hairshop_id,
                "hairshop_nm": hairshop_nm,
                "clinic_id": clinic_id,
                "clinic_nm": clinic_nm,
                "magazine_id": magazine_id,
                "title": title,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


def fetch_detail(review_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.bookmark_id, a.category, b.user_id, b.nickname, c.hairprd_id, c.hairprd_nm,
               d.med_id, d.med_nm, e.hairshop_id, e.hairshop_nm, f.clinic_id, f.clinic_nm,
               g.magazine_id, g.title
          FROM TBBOOKMARK a
          LEFT JOIN TBUSER AS b
            ON a.owner_id = b.user_id
          LEFT JOIN TBHAIRPRD AS c
            ON a.hairprd_id = (CASE WHEN a.category = '1'
                                    THEN c.hairprd_id
                                    ELSE null
                               END)
          LEFT JOIN TBMEDICINE AS d
            ON a.med_id = (CASE WHEN a.category = '2'
                                    THEN d.med_id
                                    ELSE null
                               END)
          LEFT JOIN TBHAIRSHOP AS e
            ON a.hairshop_id = (CASE WHEN a.category = '3'
                                    THEN e.hairshop_id
                                    ELSE null
                               END)
          LEFT JOIN TBCLINIC AS f
            ON a.clinic_id = (CASE WHEN a.category = '4'
                                    THEN f.clinic_id
                                    ELSE null
                               END)
          LEFT JOIN TBMAGAZINE AS g
            ON a.magazine_id = (CASE WHEN a.category = '5'
                                    THEN g.magazine_id
                                    ELSE null
                               END)
         WHERE a.review_id = %s
    """

    try:
        cursor.execute(query, (review_id,))
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            bookmark_id, category, owner_id, nickname, hairprd_id, hairprd_nm, med_id, med_nm, \
            hairshop_id, hairshop_nm, clinic_id, clinic_nm, magazine_id, title = item
            retObj = {
                "bookmark_id": bookmark_id,
                "category": category,
                "owner_id": owner_id,
                "nickname": nickname,
                "hairprd_id": hairprd_id,
                "hairprd_nm": hairprd_nm,
                "med_id": med_id,
                "med_nm": med_nm,
                "hairshop_id": hairshop_id,
                "hairshop_nm": hairshop_nm,
                "clinic_id": clinic_id,
                "clinic_nm": clinic_nm,
                "magazine_id": magazine_id,
                "title": title,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


def fetch_list_cnt(owner_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT count(*)
          FROM TBBOOKMARK a
          LEFT JOIN TBUSER AS b
            ON a.owner_id = b.user_id
          LEFT JOIN TBHAIRPRD AS c
            ON a.hairprd_id = (CASE WHEN a.category = '1'
                                    THEN c.hairprd_id
                                    ELSE null
                               END)
          LEFT JOIN TBMEDICINE AS d
            ON a.med_id = (CASE WHEN a.category = '2'
                                    THEN d.med_id
                                    ELSE null
                               END)
          LEFT JOIN TBHAIRSHOP AS e
            ON a.hairshop_id = (CASE WHEN a.category = '3'
                                    THEN e.hairshop_id
                                    ELSE null
                               END)
          LEFT JOIN TBCLINIC AS f
            ON a.clinic_id = (CASE WHEN a.category = '4'
                                    THEN f.clinic_id
                                    ELSE null
                               END)
          LEFT JOIN TBMAGAZINE AS g
            ON a.magazine_id = (CASE WHEN a.category = '5'
                                    THEN g.magazine_id
                                    ELSE null
                               END)
         WHERE a.owner_id = %s
    """

    try:
        cursor.execute(query, (owner_id,))
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


class Bookmark(Resource):

    @marshal_with(result_fields)
    def post(self):
        args = post_parser.parse_args()
        result, bookmark = create_bookmark(args.category, args.owner_id, args.magazine_id,
                                   args.hairprd_id, args.med_id, args.hairshop_id, args.clinic_id)

        # print(args.magazine_id, file=sys.stdout)

        if not result:
            responseObject = {
                'msg': 'Fail',
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': bookmark
            }
            return responseObject, 200

    @marshal_with(result_fields)
    # @jwt_required
    def get(self, bookmark_id=None):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        owner_id = args.get('owner_id')
        limit = args.get('limit')
        offset = args.get('offset')
        ordering = args.get('ordering')
        asc = args.get('asc')
        count = 0
        if ordering is None:
            ordering = 'reg_date'
        if asc is None:
            asc = 'DESC'

        if owner_id is not None:
            result, bookmark = fetch_list(owner_id, limit, offset, ordering, asc)
            count = fetch_list_cnt(owner_id)
        else:
            result, bookmark = fetch_detail(owner_id)
            if result is False:
                count = 0
            else:
                count = 1

        if not result:
            responseObject = {
                'msg': 'Fail',
                'count': count
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'count': count,
                'results': bookmark
            }
            return responseObject, 200