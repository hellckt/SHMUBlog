# -*- coding: utf-8 -*-
from flask import url_for, render_template, flash
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.utils import redirect

from app import db
from app.auth import bp
from app.auth.forms import RegisterForm, LoginForm
from app.models import User
from app.utils import redirect_back


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.validate_password(form.password.data):
            if login_user(user, form.remember_me.data):
                flash('登陆成功。', 'info')
                return redirect_back()
            else:
                flash('你的账号已经被封禁。', 'warning')
                return redirect(url_for('main.index'))
        flash('错误的密码或邮箱。', 'warning')
    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # TODO: 考虑跳转到用户主页。
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        user = User(name=name, email=email, username=username)
        user.password = password
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登陆。', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('注销成功。', 'info')
    return redirect(url_for('main.index'))
