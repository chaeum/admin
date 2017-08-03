from __future__ import print_function
from flask import request
from flask_restful import fields, marshal_with, reqparse, Resource
from flask_jwt_extended import JWTManager, jwt_required,\
    create_access_token, get_jwt_identity
import sys

from chaeum import cnx_pool, jwt

def valid_email(str):
    return True

def email(email_str):
    """Return email_str if valid, raise an exception in other case."""
    if valid_email(email_str):
        return email_str
    else:
        raise ValueError('{} is not a valid email'.format(email_str))

def isstr(s):
    return s if s else ''

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

# user_fields = {
#     'id': fields.Integer,
#     'username': fields.String,
#     'email': fields.String,
#     'user_priority': fields.Integer,
#     'custom_greeting': fields.FormattedString('Hey there {username}!'),
#     'date_created': fields.DateTime,
#     'date_updated': fields.DateTime,
#     'links': fields.Nested({
#         'friends': fields.Url('user_friends'),
#         'posts': fields.Url('user_posts'),
#     }),
# }
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
            print(cursor.rowcount, file=sys.stderr)
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
            print(cursor.rowcount, file=sys.stderr)
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


def fetch_list(limit, offset, ordering, asc , nickname=None):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT user_id, check_id, nickname, birth, app_type, push_tkn, push_yn, device,
            gender, location, is_staff, last_login, is_active, date_joined
          FROM TBUSER
    """

    try:
        if nickname is not None:
            query = query + "where nickname = %s"
            cursor.execute(query, (nickname,))
        else:
            query = query + 'ORDER BY ' + ordering + ' ' + asc + ' \n'
            if limit is not None and offset is not None:
                query = query + 'LIMIT ' + offset + ', ' + limit
        cursor.execute(query)
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

    print(retObjList, file=sys.stdout)

    return True, retObjList


def fetch_list_cnt(nickname):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT count(*)
          FROM TBUSER
         WHERE nickname = %s
    """

    try:
        cursor.execute(query, (nickname,))
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


def fetch_detail(user_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT user_id, check_id, nickname, birth, app_type, push_tkn, push_yn, device,
            gender, location, is_staff, last_login, is_active, date_joined
          FROM TBUSER
         WHERE user_id = %s
    """
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    retObjList = []

    try:
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

    print(retObjList, file=sys.stdout)

    return True, retObjList


def fetch_detail_by_nickname(nickname):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT user_id, check_id, nickname, birth, app_type, push_tkn, push_yn, device,
            gender, location, is_staff, last_login, is_active, date_joined
          FROM TBUSER
         WHERE nickname = %s
    """
    cursor.execute(query, (nickname,))
    result = cursor.fetchall()
    retObjList = []

    try:
        for item in result:
            user_id, check_id, nickname, birth, app_type, push_tkn, push_yn, device, \
                gender, location, is_staff, last_login, is_active, date_joined = item
            retObj = {
                "user_id": '',
                "check_id": '',
                "nickname": '',
                "birth": '',
                "app_type": '',
                "push_tkn": '',
                "push_yn": '',
                "device": '',
                "gender": '',
                "location": '',
                "is_staff": '',
                "last_login": '',
                "is_active": '',
                "date_joined": ''
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    print(retObjList, file=sys.stdout)

    return True, retObjList


class User(Resource):

    @marshal_with(result_fields)
    def post(self):
        args = post_parser.parse_args()
        result, user = create_user(args.check_id, args.nickname, args.birth, args.app_type,
                           args.push_tkn, args.push_yn, args.device, args.gender,
                           args.location, args.is_staff)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': user
            }
            return responseObject, 201

    @marshal_with(result_fields)
    def put(self, user_id=None):
        args = post_parser.parse_args()
        result, user = update_user(args.check_id, args.nickname, args.birth, args.app_type,
                                   args.push_tkn, args.push_yn, args.device, args.gender,
                                   args.location, args.is_staff, user_id)

        if not result:
            responseObject = {
                'msg': 'Fail'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'results': user
            }
            return responseObject, 201

    @marshal_with(result_fields)
    #@jwt_required
    def get(self, user_id=None):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        # keyword = args.get('keyword')
        # limit = args.get('limit')
        # offset = args.get('offset')
        # ordering = args.get('ordering')
        nickname = args.get('nickname')

        #### nickname 중복 찾기 ###
        if nickname is not None and user_id is None:
            result, user = fetch_detail_by_nickname(nickname)
            count = fetch_list_cnt(nickname)
        else:
            result, user = fetch_detail(user_id)

        if not result:
            responseObject = {
                'msg': 'Fail',
                'count': 0
            }
            return responseObject, 401
        else:
            print('성공', file=sys.stderr)
            responseObject = {
                'msg': 'Success',
                'count': count,
                'results': user
            }
            print(responseObject, file=sys.stderr)
            return responseObject, 200

