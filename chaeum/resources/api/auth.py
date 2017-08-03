from flask import make_response, jsonify
from flask_restful import fields, marshal_with, reqparse, Resource
from flask_jwt_extended import JWTManager, jwt_required, \
    create_access_token, get_jwt_identity

import datetime
import jwt

from chaeum import app, api, cnx_pool

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'check_id', dest='check_id',
    type=str, location='json', required=True,
    help='The user\'s check_id check',
)


def create_user(check_id, is_staff, username):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        INSERT
          INTO TBUSER(check_id, last_login, is_staff, nickname, is_active, date_joined)
        VALUES (%s, now(), %s, %s, 1, now())
    """
    cursor.execute(query, (check_id, is_staff, username))

    return True

def fetch_user(check_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT nickname
          FROM TBUSER
         WHERE check_id = %s
    """
    cursor.execute(query, (check_id,))
    result = cursor.fetchone()

    return result


class Auth(Resource):
    def post(self):
        args = post_parser.parse_args()
        user = fetch_user(args.check_id)

        if not user:
            responseObject = {
                'msg': 'Bad username or password'
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'access_token': create_access_token(identity=user[0])
            }
            return responseObject, 200
