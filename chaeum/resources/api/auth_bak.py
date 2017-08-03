from flask import make_response, jsonify
from flask_restful import fields, marshal_with, reqparse, Resource
from flask_jwt import JWT

import datetime
import jwt

from chaeum import app, api, cnx_pool

def encode_auth_token(username):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': username
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e

def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'check_id', dest='check_id',
    type=str, location='json', required=True,
    help='The user\'s check_id check',
)
post_parser.add_argument(
    'is_staff', dest='is_staff',
    type=int, location='json', required=False,
    help='The user\'s is_staff',
)
post_parser.add_argument(
    'username', dest='username',
    location='json', type=str, required=True,
    help='The user\'s username',
)

def create_user(check_id, is_staff, username):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        INSERT
          INTO TBUSER(check_id, last_login, is_staff, username, is_active, date_joined)
        VALUES (%s, now(), %s, %s, 1, now())
    """
    cursor.execute(query, (check_id, is_staff, username))

    return True

def fetch_user(check_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT username
          FROM TBUSER
         WHERE check_id = %s
    """
    cursor.execute(query, (check_id,))
    result = cursor.fetchone()

    return result

class RegisterAuth(Resource):
    def post(self):
        args = post_parser.parse_args()
        user = fetch_user(args.check_id)

        if not user:
            try:
                create_user(args.check_id, 0, args.username)
                auth_token = encode_auth_token(args.username)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered',
                    'auth_token': auth_token.decode(),
                }
                # return make_response(jsonify(responseObject)), 201
                return responseObject
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                # return make_response(jsonify(responseObject)), 401
                return responseObject
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            # return make_response(jsonify(responseObject)), 202
            return responseObject

class LoginAuth(Resource):
    def post(self):
        args = post_parser.parse_args()
        user = fetch_user(args.check_id)

        if not user:
            try:
                create_user(args.check_id, 0, args.username)
                auth_token = encode_auth_token(args.username)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered',
                    'auth_token': auth_token.decode(),
                }
                # return make_response(jsonify(responseObject)), 201
                return responseObject
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                # return make_response(jsonify(responseObject)), 401
                return responseObject
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            # return make_response(jsonify(responseObject)), 202
            return responseObject