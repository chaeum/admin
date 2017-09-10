from flask_restful import fields, reqparse, Resource
from admin.common.render import render_html
from flask import request

from admin import cnx_pool, jwt

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'check_id', dest='check_id',
    type=str, location='json', required=True,
    help='check_id is fault',
)
post_parser.add_argument(
    'nickname', dest='nickname',
    type=str, location='json', required=True,
    help='nickname is fault',
)
post_parser.add_argument(
    'birth', dest='birth',
    type=str, location='json', required=True,
    help='birth is fault',
)
post_parser.add_argument(
    'app_type', dest='app_type', choices=('C', 'G', 'N'),
    type=str, location='json', required=True,
    help='app_type is fault',
)
post_parser.add_argument(
    'push_tkn', dest='push_tkn',
    type=str, location='json', required=True,
    help='push_tkn is fault',
)
post_parser.add_argument(
    'push_yn', dest='push_yn', choices=('Y', 'N'),
    type=str, location='json', required=True,
    help='push_yn is fault',
)
post_parser.add_argument(
    'device', dest='device', choices=('A', 'I'),
    type=str, location='json', required=True,
    help='device is fault',
)
post_parser.add_argument(
    'gender', dest='gender', choices=('M', 'W'),
    type=str, location='json', required=True,
    help='gender is fault',
)
post_parser.add_argument(
    'location', dest='location',
    type=str, location='json', required=True,
    help='location is fault',
)
post_parser.add_argument(
    'is_staff', dest='is_staff', choices=(0, 1),
    type=int, location='json', required=True,
    help='is_staff is fault',
)

list_fields = {
    'user_id': fields.Integer,
    'check_id': fields.String,
    'nickname': fields.String,
    'birth': fields.String,
    'app_type': fields.String,
    'push_tkn': fields.String,
    'push_yn': fields.String,
    'device': fields.String,
    'gender': fields.String,
    'location': fields.String,
    'last_login': fields.DateTime,
    'is_staff': fields.Integer,
    'is_active': fields.Integer,
    'date_joined': fields.DateTime,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}


def create_user(check_id, nickname, birth, app_type, push_tkn, push_yn,
                device, gender, location, is_staff):


    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
                INSERT
                  INTO TBUSER(check_id, nickname, birth, app_type, push_tkn, push_yn, device, gender, location,
                              is_staff, last_login, is_active, date_joined)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, now(), 1, now())
            """
        user = cursor.execute(query, (check_id, nickname, birth, app_type, push_tkn, push_yn,
                                      device, gender, location, is_staff))

        if cursor.rowcount == 1:
            retObj = {
                "user_id": cursor.lastrowid,
                "check_id": check_id,
                "nickname": nickname,
                "birth": birth,
                "app_type": app_type,
                "push_tkn": push_tkn,
                "push_yn": push_yn,
                "device": device,
                "gender": gender,
                "location": location,
                "is_staff": is_staff,
            }
    except Exception as e:
        return False, None
    finally:
        conn.close()
    return True, retObj


def update_user(check_id, nickname, birth, app_type, push_tkn, push_yn,
                device, gender, location, is_staff, user_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()
    retObj = {}

    try:
        query = """
            UPDATE TBUSER
              SET check_id = %s,
                  nickname = %s,
                  birth = %s,
                  app_type = %s,
                  push_tkn = %s,
                  push_yn = %s,
                  device = %s,
                  gender = %s,
                  location = %s,
                  is_staff = %s
            WHERE user_id = %s
        """
        user = cursor.execute(query, (check_id, nickname, birth, app_type, push_tkn, push_yn,
                                      device, gender, location, is_staff, user_id))

        if cursor.rowcount == 1:
            retObj = {
                "user_id": cursor.lastrowid,
                "check_id": check_id,
                "nickname": nickname,
                "birth": birth,
                "app_type": app_type,
                "push_tkn": push_tkn,
                "push_yn": push_yn,
                "device": device,
                "gender": gender,
                "location": location,
                "is_staff": is_staff,
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
        SELECT user_id, check_id, nickname, birth, app_type, push_tkn, push_yn, device,
            gender, location, is_staff, last_login, is_active, date_joined
          FROM TBUSER
    """

    try:
        cursor.execute(query)
        query = query + 'ORDER BY ' + ordering + ' ' + asc + ' \n'
        if limit is not None and offset is not None:
            query = query + 'LIMIT ' + offset + ', ' + limit
        result = cursor.fetchall()
        retObjList = []

        for item in result:
            user_id, check_id, nickname, birth, app_type, push_tkn, push_yn, device, \
            gender, location, is_staff, last_login, is_active, date_joined = item
            retObj = {
                "user_id": user_id,
                "check_id": check_id,
                "nickname": nickname,
                "birth": birth,
                "app_type": app_type,
                "push_tkn": push_tkn,
                "push_yn": push_yn,
                "device": device,
                "gender": gender,
                "location": location,
                "is_staff": is_staff,
                "last_login": last_login,
                "is_active": is_active,
                "date_joined": date_joined
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
          FROM TBUSER
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


class AdmUserList(Resource):
    def get(self):
        ordering = None
        asc = None
        if ordering is None:
            ordering = 'reg_date'
        if asc is None:
            asc = 'DESC'

        result, user = fetch_list(None, None, ordering, asc)
        count = fetch_list_cnt()
        return render_html('user/user.html', user=user, count=count)


class AdmUserDetail(Resource):
    def get(self, user_id=None):
        return render_html('user/user_detail.html')

