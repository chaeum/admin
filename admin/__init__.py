import mysql.connector.pooling as pooling
from flask import Flask, url_for
from flask_jwt_extended import JWTManager
from flask_restful import Api
import os

# from flask_jwt_extended import JWTManager, jwt_required, \
#     create_access_token,  jwt_refresh_token_required, \
#     create_refresh_token, get_jwt_identity, set_access_cookies, \
#     set_refresh_cookies, unset_jwt_cookies

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'testtest'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:chaeum!01@testwebinstance.ciowpdvbzwrs.ap-northeast-2.rds.amazonaws.com:3306/chaeum'

# browser cache ignore for static files
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

#
api = Api(app)
# db = SQLAlchemy(app)

jwt = JWTManager(app)

db_user = "admin"
db_pass = "chaeum!01"
db_url = "testwebinstance.ciowpdvbzwrs.ap-northeast-2.rds.amazonaws.com"
db_name = "chaeumTest"

cnx_pool = pooling.MySQLConnectionPool(pool_name="chaeum_pool",
                                                       pool_size=10,
                                                       autocommit=True,
                                                       user=db_user,
                                                       password=db_pass,
                                                       host=db_url,
                                                       database=db_name)


# from admin.resources.web.index import WebIndex
# api.add_resource(WebIndex, '/index')
# from admin.resources.web.index import WebSearch
# api.add_resource(WebSearch, '/search')
# from admin.resources.web.hairprd import WebHairPrdList
# api.add_resource(WebHairPrdList, '/hairprds')
# from admin.resources.web.hairprd import WebHairPrdDetail
# api.add_resource(WebHairPrdDetail, '/hairprds/<int:hairprd_id>')
# from admin.resources.web.hairshop import WebHairShopList
# api.add_resource(WebHairShopList, '/hairshops')
# from admin.resources.web.hairshop import WebHairShopDetail
# api.add_resource(WebHairShopDetail, '/hairshops/<int:hairshop_id>')
from admin.resources.admin.index import AdmIndex
api.add_resource(AdmIndex, '/index')
from admin.resources.admin.index import AdmIcons
api.add_resource(AdmIcons, '/icons')
from admin.resources.admin.user import AdmUserList
api.add_resource(AdmUserList, '/users')
from admin.resources.admin.hairprd import AdmHairPrdList
api.add_resource(AdmHairPrdList, '/hairprds')
from admin.resources.admin.medicine import AdmMedicineSpecList
api.add_resource(AdmMedicineSpecList, '/medicines/spec')
from admin.resources.admin.medicine import AdmMedicineNormList
api.add_resource(AdmMedicineNormList, '/medicines/norm')
from admin.resources.admin.medicine import AdmMedicineEtcList
api.add_resource(AdmMedicineEtcList, '/medicines/etc')
from admin.resources.admin.clinic import AdmHairClinicList
api.add_resource(AdmHairClinicList, '/clinics')
from admin.resources.admin.hairshop import AdmHairShopList
api.add_resource(AdmHairShopList, '/hairshops')
from admin.resources.admin.magazine import AdmMagazineList
api.add_resource(AdmMagazineList, '/magazines')