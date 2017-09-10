from flask_restful import fields, reqparse, Resource
from admin.common.render import render_html
from flask import request

from admin import cnx_pool, jwt

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


def isstr(s):
    return s if s else ''


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
        return False, None
    finally:
        conn.close()

    return True, retObj


def fetch_list(limit, offset, ordering, asc):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT clinic_id, clinic_nm, branch, region, address, like_cnt,
               phone_num, mobile_num, kakao_id, reg_date
          FROM TBCLINIC
    """

    query = query + 'ORDER BY ' + ordering + ' ' + asc + ' \n'
    if limit is not None and offset is not None:
        query = query + 'LIMIT ' + offset + ', ' + limit

    try:
        cursor.execute(query)
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


def fetch_list_cnt():
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT count(*)
          FROM TBCLINIC
         WHERE region = %s
           AND clinic_nm like %s
    """

    try:
        cursor.execute(query)
        result = cursor.fetchone()
        count = 0

        for item in result:
            count = item
    except Exception as e:
        count = -1
    finally:
        conn.close()

    return count


class AdmHairClinicList(Resource):
    def get(self):
        args = request.args
        #keyword = args.get('keyword')
        limit = args.get('limit')
        offset = args.get('offset')
        ordering = args.get('ordering')
        #region = args.get('region')
        asc = args.get('asc')
        count = 0
        if ordering is None:
            ordering = 'like_cnt'
        if asc is None:
            asc = 'DESC'

        result, clinic = fetch_list(limit, offset, ordering, asc)
        count = fetch_list_cnt()

        return render_html('clinic/clinic.html', result=result, clinic=clinic, count=count)


class AdmHairClinicDetail(Resource):
    def get(self, hairprd_id=None):
        return render_html('clinic/clinic_detail.html')

