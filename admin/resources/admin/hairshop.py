from flask_restful import fields, reqparse, Resource
from admin.common.render import render_html
from flask import request

from admin import cnx_pool, jwt


post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'hairshop_nm', dest='hairshop_nm',
    type=str, location='json', required=True,
    help='hairshop_nm is fault',
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
    'hairshop_id': fields.Integer,
    'hairshop_nm': fields.String,
    'region': fields.String,
    'address': fields.String,
    'like_cnt': fields.Integer,
    'phone_num': fields.String,
    'mobile_num': fields.String,
    'kakao_id': fields.Integer,
    'reg_date': fields.DateTime,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}


def isstr(s):
    return s if s else ''


def create_hairshop(hairshop_nm, region, address, like_cnt, phone_num, mobile_num, kakao_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
            INSERT
              INTO TBHAIRSHOP(hairshop_nm, region, address, like_cnt, phone_num, mobile_num, kakao_id, reg_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, now())
        """
        hairshop = cursor.execute(query, (hairshop_nm, region, address, like_cnt, phone_num, mobile_num, kakao_id))

        if cursor.rowcount == 1:
            retObj = {
                "hairshop_id": cursor.lastrowid,
                "hairshop_nm": hairshop_nm,
                "region": region,
                "address": address,
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


def fetch_list(keyword, limit, offset, ordering, asc, region=None):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT hairshop_id, hairshop_nm, region, address, like_cnt, phone_num, mobile_num, kakao_id, reg_date
          FROM TBHAIRSHOP
         WHERE hairshop_nm like %s
    """

    if region is not None:
        query += '\n AND region = %s \n'

    query = query + 'ORDER BY ' + ordering + ' ' + asc + ' \n'
    if limit is not None and offset is not None:
        query = query + 'LIMIT ' + offset + ', ' + limit

    try:
        if region is None:
            cursor.execute(query, ('%' + keyword + '%',))
        else:
            cursor.execute(query, ('%' + keyword + '%', region))
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            hairshop_id, hairshop_nm, region, address, like_cnt, phone_num, mobile_num, kakao_id, reg_date = item
            retObj = {
                "hairshop_id": hairshop_id,
                "hairshop_nm": hairshop_nm,
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


def fetch_detail(hairshop_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT hairshop_id, hairshop_nm, region, address, like_cnt, phone_num, mobile_num, kakao_id, reg_date
          FROM TBHAIRSHOP
         WHERE hairshop_id = %s
    """

    try:
        cursor.execute(query, (hairshop_id,))
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            hairshop_id, hairshop_nm, region, address, like_cnt, phone_num, mobile_num, kakao_id, reg_date = item
            retObj = {
                "hairshop_id": hairshop_id,
                "hairshop_nm": hairshop_nm,
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


def fetch_list_cnt(keyword):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT count(*)
          FROM TBHAIRSHOP
         WHERE hairshop_nm like %s
    """

    try:
        cursor.execute(query, ('%' + keyword + '%',))
        result = cursor.fetchone()
        count = 0

        for item in result:
            count = item
    except Exception as e:
        count = -1
    finally:
        conn.close()

    return count


class AdmHairShopList(Resource):
    def get(self):
        args = request.args
        keyword = args.get('keyword')
        region = args.get('region')
        limit = args.get('limit')
        offset = args.get('offset')
        ordering = args.get('ordering')
        asc = args.get('asc')
        count = 0
        if ordering is None:
            ordering = 'reg_date'
        if asc is None:
            asc = 'DESC'

        result, hairshop = fetch_list(isstr(keyword), limit, offset, ordering, asc, region)
        count = fetch_list_cnt(isstr(keyword))

        return render_html('hairshop/hairshop.html', result=result, hairshop=hairshop, count=count)


class AdmHairShopDetail(Resource):
    def get(self, hairshop_id=None):
        return render_html('hairshop/hairshop_detail.html')

