from flask_restful import reqparse, Resource
from admin.common.render import render_html


class AdmHairPrdList(Resource):
    def get(self):
        return render_html('hairprd/hairprd.html')


class AdmHairPrdDetail(Resource):
    def get(self, hairprd_id=None):
        return render_html('hairprd/hairprd_detail.html')

