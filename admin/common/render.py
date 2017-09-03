from flask import Response, render_template


def output_html(data, code, headers=None):
    resp = Response(data, mimetype='text/html', headers=headers)
    resp.status_code = code
    return resp


def render_html(template, code=200, headers=None, **context):
    return output_html(render_template(template, **context), code, headers)
