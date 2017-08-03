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
    'clinic_nm', dest='clinic_nm',
    type=str, location='json', required=True,
    help='clinic_nm is fault',
)
post_parser.add_argument(
    'branch', dest='branch',
    type=str, location='json', required=True,
    help='branch is fault',
)
post_parser.add_argument(
    'region', dest='region',
    type=str, location='json', required=True,
    help='region is fault',
)
post_parser.add_argument(
    'address', dest='address',
    type=str, location='json', required=True,
    help='address is fault',
)
post_parser.add_argument(
    'like_cnt', dest='like_cnt',
    type=int, location='json', required=True,
    help='like_cnt is fault',
)
post_parser.add_argument(
    'phone_num', dest='phone_num',
    type=str, location='json', required=True,
    help='phone_num is fault',
)
post_parser.add_argument(
    'mobile_num', dest='mobile_num',
    type=str, location='json', required=True,
    help='mobile_num is fault',
)
post_parser.add_argument(
    'kakao_id', dest='kakao_id',
    type=str, location='json', required=True,
    help='kakao_id is fault',
)

list_fields = {
    'clinic_id': fields.Integer,
    'clinic_nm': fields.String,
    'region': fields.String,
    'address': fields.String,
    'like_cnt': fields.Integer,
    'phone_num': fields.String,
    'mobile_num': fields.String,
    'kakao_id': fields.String,
    'reg_date': fields.DateTime,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}

def create_clinic(clinic_nm, branch, region, address, like_cnt, phone_num, mobile_num, kakao_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
            INSERT
              INTO TBCLINIC(clinic_nm, branch, region, address, like_cnt, phone_num, mobile_num, kakao_id, reg_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now())
        """
        clinic = cursor.execute(query, (clinic_nm, branch, region, address, like_cnt, phone_num, mobile_num, kakao_id))

        if cursor.rowcount == 1:
            retObj = {
                "clinic_id": cursor.lastrowid,
                "clinic_nm": clinic_nm,
                "branch": branch,
                "region": "region",
                "address": "address",
                "like_cnt": 0,
                "phone_num": phone_num,
                "mobile_num": mobile_num,
                "kakao_id": kakao_id,
            }
    except Exception as e:
        print(e, file=sys.stdout)
        return False, None
    finally:
        conn.close()

    return True, retObj

def fetch_list(keyword, limit, offset, ordering, asc, region):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT clinic_id, clinic_nm, branch, region, address, like_cnt,
               phone_num, mobile_num, kakao_id, reg_date
          FROM TBCLINIC
         WHERE region = %s
           AND clinic_nm like %s
    """

    query = query + 'ORDER BY ' + ordering + ' ' + asc + ' \n'
    if limit is not None and offset is not None:
        query = query + 'LIMIT ' + offset + ', ' + limit

    try:
        cursor.execute(query, (region, '%' + keyword + '%'))
        result = cursor.fetchall()
        retObjList = []
        for item in result:
            clinic_id, clinic_nm, branch, region, address, like_cnt, \
                phone_num, mobile_num, kakao_id, reg_date = item
            retObj = {
                "clinic_id": cursor.lastrowid,
                "clinic_nm": clinic_nm,
                "branch": branch,
                "region": region,
                "address": address,
                "like_cnt": like_cnt,
                "phone_num": phone_num,
                "mobile_num": mobile_num,
                "kakao_id": kakao_id,
                "reg_date": reg_date,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


def fetch_detail(clinic_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT clinic_id, clinic_nm, branch, region, address, like_cnt,
               phone_num, mobile_num, kakao_id, reg_date
          FROM TBCLINIC
         WHERE clinic_id = %s
    """

    try:
        cursor.execute(query, (clinic_id,))
        result = cursor.fetchall()
        retObjList = []
        for item in result:
            clinic_id, clinic_nm, branch, region, address, like_cnt, \
                phone_num, mobile_num, kakao_id, reg_date = item
            retObj = {
                "clinic_id": clinic_id,
                "clinic_nm": clinic_nm,
                "branch": branch,
                "region": region,
                "address": address,
                "like_cnt": like_cnt,
                "phone_num": phone_num,
                "mobile_num": mobile_num,
                "kakao_id": kakao_id,
                "reg_date": reg_date,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


def fetch_list_cnt(keyword, region):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT count(*)
          FROM TBCLINIC
         WHERE region = %s
           AND clinic_nm like %s
    """

    try:
        cursor.execute(query, (region, '%' + keyword + '%'))
        result = cursor.fetchall()
        count = 0
        for item in result:
            count = item
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return count


class Clinic(Resource):

    @marshal_with(result_fields)
    def post(self):
        args = post_parser.parse_args()
        result, clinic = create_clinic(args.clinic_nm, args.branch, args.region, args.address,
                                         args.like_cnt, args.phone_num, args.mobile_num, args.kakao_id)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': clinic
            }
            return responseObject, 200

    @marshal_with(result_fields)
    # @jwt_required
    def get(self, clinic_id=None):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        keyword = args.get('keyword')
        limit = args.get('limit')
        offset = args.get('offset')
        ordering = args.get('ordering')
        region = args.get('region')
        asc = args.get('asc')
        count = 0
        if ordering is None:
            ordering = 'like_cnt'
        if asc is None:
            asc = 'DESC'

        if clinic_id is None:
            result, clinic = fetch_list(isstr(keyword), limit, offset, ordering, asc, region)
            count = fetch_list_cnt(isstr(keyword))
        else:
            result, clinic = fetch_detail(clinic_id)
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
                'results': clinic
            }
            return responseObject, 200