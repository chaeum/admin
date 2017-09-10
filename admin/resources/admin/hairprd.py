from flask_restful import fields, reqparse, Resource
from admin.common.render import render_html
from flask import request

from admin import cnx_pool, jwt

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'hairprd_nm', dest='hairprd_nm',
    type=str, location='json', required=True,
    help='hairprd_nm is fault',
)
post_parser.add_argument(
    'price', dest='price',
    type=int, location='json', required=True,
    help='price is fault',
)
post_parser.add_argument(
    'capacity', dest='capacity',
    type=str, location='json', required=True,
    help='capacity is fault',
)
post_parser.add_argument(
    'like_cnt', dest='like_cnt',
    type=int, location='json', required=True,
    help='like_cnt is fault',
)

post_parser.add_argument(
    'brnd_id', dest='brnd_id',
    type=int, location='json', required=True,
    help='brnd_id is fault',
)

list_fields = {
    'hairprd_id': fields.Integer,
    'hairprd_nm': fields.String,
    'price': fields.Integer,
    'capacity': fields.String,
    'like_cnt': fields.Integer,
    'reg_date': fields.DateTime,
    'brnd_id': fields.Integer,
    'brnd_nm': fields.String,
}


def isstr(s):
    return s if s else ''


def create_hairprd(hairprd_nm, price, capacity, like_cnt, brnd_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
            INSERT
              INTO TBHAIRPRD(hairprd_nm, price, capacity, like_cnt, reg_date, brnd_id)
            VALUES (%s, %s, %s, %s, now(), %s)
        """
        hairprd = cursor.execute(query, (hairprd_nm, price, capacity, like_cnt, brnd_id))

        if cursor.rowcount == 1:
            retObj = {
                "hairprd_id": cursor.lastrowid,
                "hairprd_nm": hairprd_nm,
                "price": price,
                "capacity": capacity,
                "like_cnt": 0,
                "brnd_id": brnd_id,
            }
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObj


def fetch_list(keyword, limit, offset, ordering, asc):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.hairprd_id, a.hairprd_nm, a.price, a.capacity, a.like_cnt, a.reg_date,
               a.brnd_id, b.brnd_nm
          FROM TBHAIRPRD a, TBBRND b
         WHERE a.hairprd_nm like %s
           AND a.brnd_id = b.brnd_id
    """
    query = query + 'ORDER BY ' + ordering + ' ' + asc + ' \n'
    if limit is not None and offset is not None:
        query = query + 'LIMIT ' + offset + ', ' + limit

    try:
        cursor.execute(query, ('%' + keyword + '%',))
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            hairprd_id, hairprd_nm, price, capacity, like_cnt, reg_date, brnd_id, brnd_nm = item
            retObj = {
                "hairprd_id": hairprd_id,
                "hairprd_nm": hairprd_nm,
                "price": price,
                "capacity": capacity,
                "like_cnt": like_cnt,
                "reg_date": reg_date,
                "brnd_id": brnd_id,
                "brnd_nm": brnd_nm,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


def fetch_detail(hairprd_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.hairprd_id, a.hairprd_nm, a.price, a.capacity, a.like_cnt, a.reg_date,
               a.brnd_id, b.brnd_nm
          FROM TBHAIRPRD a, TBBRND b
         WHERE a.hairprd_id = %s
           AND a.brnd_id = b.brnd_id
    """

    try:
        cursor.execute(query, (hairprd_id,))
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            hairprd_id, hairprd_nm, price, capacity, like_cnt, reg_date, brnd_id, brnd_nm = item
            retObj = {
                "hairprd_id": hairprd_id,
                "hairprd_nm": hairprd_nm,
                "price": price,
                "capacity": capacity,
                "like_cnt": like_cnt,
                "reg_date": reg_date,
                "brnd_id": brnd_id,
                "brnd_nm": brnd_nm,
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
          FROM TBHAIRPRD a, TBBRND b
         WHERE a.hairprd_nm like %s
           AND a.brnd_id = b.brnd_id
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


class AdmHairPrdList(Resource):
    def get(self):
        args = request.args
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

        result, hairprd = fetch_list(isstr(keyword), limit, offset, ordering, asc)
        count = fetch_list_cnt(isstr(keyword))

        return render_html('hairprd/hairprd.html', result=result, hairprd=hairprd, count=count)


class AdmHairPrdDetail(Resource):
    def get(self, hairprd_id=None):
        return render_html('hairprd/hairprd_detail.html')

