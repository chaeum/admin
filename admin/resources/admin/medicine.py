from flask_restful import reqparse, Resource
from admin.common.render import render_html


class AdmMedicineSpecList(Resource):
    def get(self):
        return render_html('medicine/spec.html')


class AdmMedicineNormList(Resource):
    def get(self):
        return render_html('medicine/norm.html')


class AdmMedicineEtcList(Resource):
    def get(self):
        return render_html('medicine/etc.html')
# class AdmHairPrdDetail(Resource):
#     def get(self, hairprd_id=None):
#         return render_html('medicine/hairprd_detail.html')

