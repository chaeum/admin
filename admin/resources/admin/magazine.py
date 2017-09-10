from flask_restful import fields, reqparse, Resource
from admin.common.render import render_html
from flask import request

from admin import cnx_pool, jwt

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


def isstr(s):
    return s if s else ''


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
        result = cursor.fetchone()
        count = 0

        for item in result:
            count = item

    except Exception as e:
        count = -1
    finally:
        conn.close()

    return count


class AdmMagazineList(Resource):
    def get(self):
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

        result, magazine = fetch_list(isstr(keyword), limit, offset, ordering, asc)
        count = fetch_list_cnt(isstr(keyword))

        return render_html('magazine/magazine.html', result=result, magazine=magazine, count=count)


class AdmMagazineDetail(Resource):
    def get(self, magazine_id=None):
        return render_html('magazine/magazine_detail.html')

