from flask_restful import reqparse, Resource
from admin.common.render import render_html


class AdmUserList(Resource):
    def get(self):
        return render_html('user/user.html')


class AdmUserDetail(Resource):
    def get(self, user_id=None):
        return render_html('user/user_detail.html')

