from __future__ import print_function

from flask import request
from flask_restful import fields, marshal_with, reqparse, Resource
from flask_jwt_extended import JWTManager, jwt_required

from chaeum import cnx_pool, jwt

def isstr(s):
    return s if s else ''

post_parser = reqparse.RequestParser()
#########################################
# 1 : hairprd
# 2 : med
# 3 : hairshop
# 4 : clinic
#########################################
post_parser.add_argument(
    'category', dest='category', choices=('1', '2', '3', '4'),
    type=str, location='json', required=True,
    help='category is fault',
)
post_parser.add_argument(
    'contents', dest='contents',
    type=str, location='json', required=True,
    help='contents is fault',
)
post_parser.add_argument(
    'score', dest='score',
    type=int, location='json', required=True,
    help='score is fault',
)
post_parser.add_argument(
    'like_cnt', dest='like_cnt',
    type=int, location='json', required=True,
    help='like_cnt is fault',
)
post_parser.add_argument(
    'owner_id', dest='owner_id',
    type=int, location='json', required=True,
    help='owner_id is fault',
)
post_parser.add_argument(
    'hairprd_id', dest='hairprd_id',
    type=int, location='json', required=False,
    help='hairprd_id is fault',
)
post_parser.add_argument(
    'med_id', dest='med_id',
    type=int, location='json', required=False,
    help='med_id is fault',
)
post_parser.add_argument(
    'hairshop_id', dest='hairshop_id',
    type=int, location='json', required=False,
    help='hairshop_id is fault',
)
post_parser.add_argument(
    'clinic_id', dest='clinic_id',
    type=int, location='json', required=False,
    help='clinic_id is fault',
)

list_fields = {
    'review_id': fields.Integer,
    'category': fields.String,
    'contents': fields.String,
    'score': fields.Integer,
    'like_cnt': fields.Integer,
    'reg_date': fields.DateTime,
    'mod_date': fields.DateTime,
    'owner_id': fields.Integer,
    'nickname': fields.String,
    'hairprd_id': fields.Integer,
    'hairprd_nm': fields.String,
    'med_id': fields.Integer,
    'med_nm': fields.String,
    'hairshop_id': fields.Integer,
    'hairshop_nm': fields.String,
    'clinic_id': fields.Integer,
    'clinic_nm': fields.String,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'score': fields.Float,
    'results': fields.List(fields.Nested(list_fields))
}


def fetch_list(clinic_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.review_id, a.category, a.contents, a.score, a.like_cnt, a.reg_date, a.mod_date,
               b.user_id, b.nickname, c.hairprd_id, c.hairprd_nm, d.med_id, d.med_nm, e.hairshop_id,
               e.hairshop_nm, f.clinic_id, f.clinic_nm
          FROM TBREVIEW a
          LEFT JOIN TBUSER AS b
                 ON a.owner_id = b.user_id
          LEFT JOIN TBHAIRPRD AS c
                 ON a.hairprd_id = (CASE WHEN a.category = '1'
                                         THEN c.hairprd_id
                                         ELSE null
                                    END)
          LEFT JOIN TBMEDICINE AS d
                 ON a.med_id = (CASE WHEN a.category = '2'
                                     THEN d.med_id
                                     ELSE null
                                END)
          LEFT JOIN TBHAIRSHOP AS e
                 ON a.hairshop_id = (CASE WHEN a.category = '3'
                                          THEN e.hairshop_id
                                          ELSE null
                                     END)
          LEFT JOIN TBCLINIC AS f
                 ON a.clinic_id = (CASE WHEN a.category = '4'
                                        THEN f.clinic_id
                                        ELSE null
                                   END)
         WHERE a.category = 4
           AND a.clinic_id = %s
        ORDER BY reg_date DESC
    """

    try:
        cursor.execute(query, (clinic_id,))
        result = cursor.fetchall()
        retObjList = []

        for item in result:

            review_id, category, contents, score, like_cnt, reg_date, mod_date, \
                owner_id, nickname, hairprd_id, hairprd_nm, med_id, med_nm, \
                hairshop_id,hairshop_nm, clinic_id, clinic_nm = item
            retObj = {
                "review_id": review_id,
                "category": category,
                "contents": contents,
                "score": score,
                "like_cnt": like_cnt,
                "reg_date": reg_date,
                "mod_date": mod_date,
                "owner_id": owner_id,
                "nickname": nickname,
                "hairprd_id": hairprd_id,
                "hairprd_nm": hairprd_nm,
                "med_id": med_id,
                "med_nm": med_nm,
                "hairshop_id": hairshop_id,
                "hairshop_nm": hairshop_nm,
                "clinic_id": clinic_id,
                "clinic_nm": clinic_nm,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


def fetch_list_summary(clinic_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT count(*), round(avg(a.score), 1) as score
          FROM TBREVIEW a
          LEFT JOIN TBUSER AS b
                 ON a.owner_id = b.user_id
          LEFT JOIN TBHAIRPRD AS c
                 ON a.hairprd_id = (CASE WHEN a.category = '1'
                                         THEN c.hairprd_id
                                         ELSE null
                                    END)
          LEFT JOIN TBMEDICINE AS d
                 ON a.med_id = (CASE WHEN a.category = '2'
                                     THEN d.med_id
                                     ELSE null
                                END)
          LEFT JOIN TBHAIRSHOP AS e
                 ON a.hairshop_id = (CASE WHEN a.category = '3'
                                          THEN e.hairshop_id
                                          ELSE null
                                     END)
          LEFT JOIN TBCLINIC AS f
                 ON a.clinic_id = (CASE WHEN a.category = '4'
                                        THEN f.clinic_id
                                        ELSE null
                                   END)
         WHERE a.category = 4
           AND a.clinic_id = %s
    """

    try:
        cursor.execute(query, (clinic_id,))
        result = cursor.fetchall()
        count = 0
        score = 0.0

        for item in result:
            count, score = item

    except Exception as e:
        return False, None
    finally:
        conn.close()

    return count, score


class ReviewClinic(Resource):

    @marshal_with(result_fields)
    # @jwt_required
    def get(self):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        # owner_id = args.get('owner_id')
        # limit = args.get('limit')
        # offset = args.get('offset')
        # ordering = args.get('ordering')
        # asc = args.get('asc')
        clinic_id = args.get('clinic_id')

        # if ordering is None:
        #     ordering = 'reg_date'
        # if asc is None:
        #     asc = 'DESC'

        count = 0
        score = 0.0

        result, review = fetch_list(clinic_id)
        count, score = fetch_list_summary(clinic_id)

        if not result:
            responseObject = {
                'msg': 'Fail',
                'count': count,
                'score': score
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'count': count,
                'score': score,
                'results': review
            }
            return responseObject, 200