from flask_restful import reqparse, Resource
from admin.common.render import render_html


class WebHairShopList(Resource):
    def get(self):
        return render_html('hairshop/hairshop.html')


class WebHairShopDetail(Resource):
    def get(self, hairshop_id=None):
        return render_html('hairshop/hairshop_detail.html')

