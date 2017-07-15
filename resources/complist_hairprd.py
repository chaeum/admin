from __future__ import print_function

from flask import request
from flask_restful import fields, marshal_with, reqparse, Resource
from flask_jwt_extended import JWTManager, jwt_required
import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from chaeum import cnx_pool, jwt

def isstr(s):
    return s if s else ''

post_parser = reqparse.RequestParser()
#########################################
# 1 : hairprd
# 2 : med
#########################################
post_parser.add_argument(
    'category', dest='category', choices=('1', '2'),
    type=str, location='json', required=True,
    help='category is fault',
)
post_parser.add_argument(
    'comp_id', dest='comp_id',
    type=int, location='json', required=True,
    help='comp_id is fault',
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

list_fields = {
    'complist_id': fields.Integer,
    'category': fields.String,
    'comp_id': fields.Integer,
    'hairprd_id': fields.Integer,
    'med_id': fields.Integer,
}

result_fields = {
    'msg': fields.String,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(list_fields))
}


def fetch_list(comp_id, hairprd_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.complist_id, a.category, b.comp_id, b.comp_hg_nm, b.comp_eng_nm, c.hairprd_id, c.hairprd_nm, d.med_id, d.med_nm
          FROM TBCOMP_LIST a
          LEFT JOIN TBCOMP as b
                 ON a.comp_id = b.comp_id
          LEFT JOIN TBHAIRPRD as c
                 ON a.hairprd_id = (CASE WHEN a.category = '1'
                                         THEN c.hairprd_id
                                         ELSE null
                                    END)
          LEFT JOIN TBMEDICINE d
                 ON a.med_id = (CASE WHEN a.category = '2'
                                     THEN d.med_id
                                     ELSE null
                                END)
         WHERE a.category = 1
           AND a.comp_id = %s
           AND a.hairprd_id = %s
    """
    cursor.execute(query, (comp_id, hairprd_id))
    result = cursor.fetchall()
    retObjList = []

    try:
        for item in result:
            complist_id, category, comp_id, hairprd_id, med_id = item
            retObj = {
                "complist_id": complist_id,
                "category": category,
                "comp_id": comp_id,
                "hairprd_id": hairprd_id,
                "med_id": med_id,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


def fetch_list_cnt(comp_id, hairprd_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT count(*)
          FROM TBCOMP_LIST a
          LEFT JOIN TBCOMP as b
                 ON a.comp_id = b.comp_id
          LEFT JOIN TBHAIRPRD as c
                 ON a.hairprd_id = (CASE WHEN a.category = '1'
                                         THEN c.hairprd_id
                                         ELSE null
                                    END)
          LEFT JOIN TBMEDICINE d
                 ON a.med_id = (CASE WHEN a.category = '2'
                                     THEN d.med_id
                                     ELSE null
                                END)
         WHERE a.category = 1
           AND a.comp_id = %s
           AND a.hairprd_id = %s
    """
    cursor.execute(query, (comp_id, hairprd_id))
    result = cursor.fetchall()
    retObjList = []

    try:
        for item in result:
            count = item

    except Exception as e:
        return False, None
    finally:
        conn.close()

    return count


def fetch_detail(complist_id):
    conn = cnx_pool.get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.complist_id, a.category, b.comp_id, b.comp_hg_nm, b.comp_eng_nm, c.hairprd_id, c.hairprd_nm
          FROM TBCOMP_LIST a
          LEFT JOIN TBCOMP as b
                 ON a.comp_id = b.comp_id
          LEFT JOIN TBHAIRPRD as c
                 ON a.hairprd_id = (CASE WHEN a.category = '1'
                                         THEN c.hairprd_id
                                         ELSE null
                                    END)
          LEFT JOIN TBMEDICINE d
                 ON a.med_id = (CASE WHEN a.category = '2'
                                     THEN d.med_id
                                     ELSE null
                                END)
         WHERE a.complist_id = %s
    """
    cursor.execute(query, (complist_id,))
    result = cursor.fetchall()
    retObjList = []

    try:
        for item in result:
            complist_id, category, comp_id, hairprd_id, med_id = item
            retObj = {
                "complist_id": complist_id,
                "category": category,
                "comp_id": comp_id,
                "hairprd_id": hairprd_id,
                "med_id": med_id,
            }

            retObjList.append(retObj)
    except Exception as e:
        return False, None
    finally:
        conn.close()

    return True, retObjList


class CompList_Hairprd(Resource):

    @marshal_with(result_fields)
    # @jwt_required
    def get(self, complist_id=None):
        # args = post_parser.parse_args()
        # current_user = get_jwt_identity()
        args = request.args
        comp_id = args.get('comp_id')
        hairprd_id = args.get('hairprd_id')
        result, complist = fetch_list(comp_id, hairprd_id)

        if complist_id is not None:
            result, complist = fetch_list(comp_id, hairprd_id)
            count = fetch_list_cnt(comp_id, hairprd_id)
        else:
            result, complist = fetch_detail(complist_id)
            if result is False:
                count = 0
            else:
                count = 1

        if not result:
            responseObject = {
                'msg': 'Fail',
                'count': count
            }
            return responseObject, 401
        else:
            responseObject = {
                'msg': 'Success',
                'count': count,
                'results': complist
            }
            return responseObject, 200