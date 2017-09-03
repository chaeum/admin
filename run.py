import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from admin import app
import mysql.connector

# from flask import Flask, Blueprint, request
# from flask_restful import Resource, Api, url_for, reqparse
# from flaskext.mysql import MySQL
# from resources.user import User

# app = Flask(__name__)
# # api_bp = Blueprint('api', __name__)
# # api = Api(api_bp)
# api = Api(app)
#
# mysql = MySQL()

# app.config['MYSQL_DATABASE_USER'] = 'admin'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'wjdrbdud1`'
# app.config['MYSQL_DATABASE_DB'] = 'admin'
# app.config['MYSQL_DATABASE_HOST'] = 'testwebinstance.ciowpdvbzwrs.ap-northeast-2.rds.amazonaws.com'
# app.config['MYSQL_DATABASE_PORT'] = 3306
#
# mysql.init_app(app)
#
# api.add_resource(User, '/api/user/<int:id>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)