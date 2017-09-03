from flask_restful import reqparse, Resource
from admin.common.render import render_html


search_parser = reqparse.RequestParser()
search_parser.add_argument(
    'q', type=str, help='search query'
)

class AdminIndex(Resource):
    def get(self):
        return render_html('index.html')


class AdminSearch(Resource):
    def get(self):
        args = search_parser.parse_args()
        return render_html('search.html', query=args.q)
