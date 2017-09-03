from flask_restful import reqparse, Resource
from admin.common.render import render_html


class WebHairPrdList(Resource):
    def get(self):
        return render_html('hairprd/hairprd.html')


class WebHairPrdDetail(Resource):
    def get(self, hairprd_id=None):
        return render_html('hairprd/hairprd_detail.html')

