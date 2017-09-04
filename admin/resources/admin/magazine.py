from flask_restful import reqparse, Resource
from admin.common.render import render_html


class AdmMagazineList(Resource):
    def get(self):
        return render_html('magazine/magazine.html')


class AdmMagazineDetail(Resource):
    def get(self, magazine_id=None):
        return render_html('magazine/magazine_detail.html')

