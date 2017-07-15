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
    'med_nm', dest='med_nm',
    type=str, location='json', required=True,
    help='med_nm is fault',
)
#########################################
# 1 : Duta
# 2 : Fina
#########################################
post_parser.add_argument(
    'detail_category', dest='detail_category', choices=('D', 'F'),
    type=str, location='json', required=True,
    help='detail_category is fault',
)
post_parser.add_argument(
    'like_cnt', dest='like_cnt',
    type=int, location='json', required=True,
    help='like_cnt is fault',
)
post_parser.add_argument(
    'insur_yn', dest='insur_yn', choices=('Y', 'N'),
    type=str, location='json', required=True,
    help='insur_yn is fault',
)
post_parser.add_argument(
    'effect', dest='effect',
    type=str, location='json', required=True,
    help='effect is fault',
)
post_parser.add_argument(
    'usg_cap', dest='usg_cap',
    type=str, location='json', required=True,
    help='usg_cap is fault',
)
post_parser.add_argument(
    'forbid', dest='forbid',
    type=str, location='json', required=True,
    help='forbid is fault',
)
post_parser.add_argument(
    'careful_med', dest='careful_med',
    type=str, location='json', required=True,
    help='careful_med is fault',
)
post_parser.add_argument(
    'side_effect', dest='side_effect',
    type=str, location='json', required=True,
    help='side_effect is fault',
)
post_parser.add_argument(
    'brnd_making_id', dest='brnd_making_id',
    type=int, location='json', required=True,
    help='brnd_making_id is fault',
)
post_parser.add_argument(
    'brnd_sales_id', dest='brnd_sales_id',
    type=int, location='json', required=True,
    help='brnd_sales_id is fault',
)

list_fields = {
    'med_id': fields.Integer,
    'med_nm': fields.String,
    'category': fields.String,
    'detail_category': fields.String,
    'like_cnt': fields.Integer,
    'insur_yn': fields.Integer,
    'effect': fields.String,
    'usg_cap': fields.String,
    'forbid': fields.String,
    'careful_med': fields.String,
    'side_effect': fields.String,
    'reg_date': fields.DateTime,
    'brnd_making_id': fields.Integer,
    'brnd_sales_id': fields.Integer,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}


def fetch_list(detail_category, keyword, limit, offset, ordering, asc):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.med_id, a.med_nm, a.category, a.detail_category, a.like_cnt, a.insur_yn, a.effect,
               a.usg_cap, a.forbid, a.careful_med, a.side_effect, a.reg_date,
               b.brnd_nm as brnd_making_nm, c.brnd_nm as brnd_sales_nm
          FROM TBMEDICINE a
          LEFT JOIN TBBRND AS b
            ON a.brnd_making_id = b.brnd_id
          LEFT JOIN TBBRND AS c
            ON a.brnd_sales_id = c.brnd_id
         WHERE a.category = 'S'
           AND a.detail_category = '%s'
           AND a.med_nm like %s
    """

    query = query + 'ORDER BY ' + ordering + ' ' + asc + ' \n'
    if limit is not None and offset is not None:
        query = query + 'LIMIT ' + offset + ', ' + limit

    try:
        cursor.execute(query, (detail_category, '%' + keyword + '%'))
        result = cursor.fetchall()
        retObjList = []
        for item in result:
            med_id, med_nm, category, detail_category, like_cnt, insur_yn, effect, \
                usg_cap, forbid, careful_med, side_effect, reg_date, brnd_making_nm, brnd_sales_nm = item
            retObj = {
                "med_id": med_id,
                "med_nm": med_nm,
                "category": category,
                "detail_category": detail_category,
                "like_cnt": like_cnt,
                "insur_yn": insur_yn,
                "effect": effect,
                "usg_cap": usg_cap,
                "forbid": forbid,
                "careful_med": careful_med,
                "side_effect": side_effect,
                "reg_date": reg_date,
                "brnd_making_nm": brnd_making_nm,
                "brnd_sales_nm": brnd_sales_nm,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


def fetch_list_cnt(detail_category, keyword):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT count(*)
          FROM TBMEDICINE a
          LEFT JOIN TBBRND AS b
            ON a.brnd_making_id = b.brnd_id
          LEFT JOIN TBBRND AS c
            ON a.brnd_sales_id = c.brnd_id
         WHERE a.category = 'S'
           AND a.detail_category = '%s'
           AND a.med_nm like %s
    """

    try:
        cursor.execute(query, (detail_category, '%' + keyword + '%'))
        result = cursor.fetchall()
        count = 0
        for item in result:
            count = item
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return count


def fetch_detail(med_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.med_id, a.med_nm, a.category, a.detail_category, a.like_cnt, a.insur_yn, a.effect,
               a.usg_cap, a.forbid, a.careful_med, a.side_effect, a.reg_date,
               b.brnd_nm as brnd_making_nm, c.brnd_nm as brnd_sales_nm
          FROM TBMEDICINE a
          LEFT JOIN TBBRND AS b
            ON a.brnd_making_id = b.brnd_id
          LEFT JOIN TBBRND AS c
            ON a.brnd_sales_id = c.brnd_id
         WHERE a.category = 'S'
           AND a.med_id = %s
    """

    try:
        cursor.execute(query, (med_id,))
        result = cursor.fetchall()
        retObjList = []
        for item in result:
            med_id, med_nm, category, detail_category, like_cnt, insur_yn, effect, \
                usg_cap, forbid, careful_med, side_effect, reg_date, brnd_making_nm, brnd_sales_nm = item
            retObj = {
                "med_id": med_id,
                "med_nm": med_nm,
                "category": category,
                "detail_category": detail_category,
                "like_cnt": like_cnt,
                "insur_yn": insur_yn,
                "effect": effect,
                "usg_cap": usg_cap,
                "forbid": forbid,
                "careful_med": careful_med,
                "side_effect": side_effect,
                "reg_date": reg_date,
                "brnd_making_nm": brnd_making_nm,
                "brnd_sales_nm": brnd_sales_nm,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


class MedicineSpec(Resource):

    @marshal_with(result_fields)
    # @jwt_required
    def get(self, med_id=None):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        detail_category = args.get('detail_category')
        keyword = args.get('keyword')
        limit = args.get('limit')
        offset = args.get('offset')
        ordering = args.get('ordering')
        asc = args.get('asc')
        count = 0
        if ordering is None:
            ordering = 'like_cnt'
        if asc is None:
            asc = 'DESC'

        if med_id is None:
            result, medicine = fetch_list(detail_category, isstr(keyword), limit, offset, ordering, asc)
            count = fetch_list_cnt(detail_category, isstr(keyword))
        else:
            result, medicine = fetch_detail(med_id)
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
                'results': medicine
            }
            return responseObject, 200