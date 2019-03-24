# -*- coding: utf-8 -*-
from flask import render_template
from flask_wtf.csrf import CSRFError

from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(e):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(403)
def forbidden_error(e):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(e):
    return render_template('errors/500.html'), 500


@bp.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('errors/400.html', description=e.description), 400
