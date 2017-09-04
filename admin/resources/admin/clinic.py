from flask_restful import reqparse, Resource
from admin.common.render import render_html


class AdmHairClinicList(Resource):
    def get(self):
        return render_html('clinic/clinic.html')


class AdmHairClinicDetail(Resource):
    def get(self, hairprd_id=None):
        return render_html('clinic/clinic_detail.html')

