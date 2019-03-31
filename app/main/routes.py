# -*- coding: utf-8 -*-
from datetime import datetime

from flask import render_template, send_from_directory, current_app
from flask_login import current_user

from app import db
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        # 记录用户最后活跃时间
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@bp.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'],
                               filename)
