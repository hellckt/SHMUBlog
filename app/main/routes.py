# -*- coding: utf-8 -*-
from flask import render_template

from app.main import bp


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    return render_template('index.html')
