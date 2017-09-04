from flask_restful import reqparse, Resource
from admin.common.render import render_html


class AdminUserList(Resource):
    def get(self):
        return render_html('user/user.html')


class AdminUserDetail(Resource):
    def get(self, user_id=None):
        return render_html('user/user_detail.html')

